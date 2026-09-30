import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.assignment import CourseAssignment, CourseAssignmentGroup, CourseAssignmentUser


def _detail_options():
    return (
        joinedload(CourseAssignment.creator),
        selectinload(CourseAssignment.assignment_users).joinedload(CourseAssignmentUser.user),
        selectinload(CourseAssignment.assignment_groups).joinedload(CourseAssignmentGroup.group),
    )


def create(
    db: Session,
    *,
    course_id: uuid.UUID,
    is_required: bool,
    due_date: datetime | None,
    overdue_action: str,
    created_by: uuid.UUID,
) -> CourseAssignment:
    assignment = CourseAssignment(
        course_id=course_id,
        is_required=is_required,
        due_date=due_date,
        overdue_action=overdue_action,
        created_by=created_by,
        status="ACTIVE",
    )
    db.add(assignment)
    return assignment


def add_user_targets(db: Session, *, assignment_id: uuid.UUID, user_ids: list[uuid.UUID]) -> None:
    for user_id in user_ids:
        db.add(CourseAssignmentUser(assignment_id=assignment_id, user_id=user_id))


def add_group_targets(db: Session, *, assignment_id: uuid.UUID, group_ids: list[uuid.UUID]) -> None:
    for group_id in group_ids:
        db.add(CourseAssignmentGroup(assignment_id=assignment_id, group_id=group_id))


def get_by_id(db: Session, assignment_id: uuid.UUID) -> CourseAssignment | None:
    return db.get(CourseAssignment, assignment_id)


def get_detail(db: Session, assignment_id: uuid.UUID) -> CourseAssignment | None:
    stmt = select(CourseAssignment).where(CourseAssignment.id == assignment_id).options(*_detail_options())
    return db.scalar(stmt)


def list_by_course(db: Session, course_id: uuid.UUID) -> list[CourseAssignment]:
    stmt = (
        select(CourseAssignment)
        .where(CourseAssignment.course_id == course_id)
        .options(*_detail_options())
        .order_by(CourseAssignment.created_at.desc())
    )
    return list(db.scalars(stmt).unique())


def list_active_by_group(db: Session, group_id: uuid.UUID) -> list[CourseAssignment]:
    stmt = (
        select(CourseAssignment)
        .join(CourseAssignmentGroup, CourseAssignmentGroup.assignment_id == CourseAssignment.id)
        .where(CourseAssignmentGroup.group_id == group_id, CourseAssignment.status == "ACTIVE")
    )
    return list(db.scalars(stmt))
