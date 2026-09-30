import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import storage
from app.models.assignment import CourseAssignment
from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories import (
    assignment_repository,
    audit_repository,
    course_repository,
    enrollment_repository,
    group_repository,
    user_repository,
)
from app.schemas.assignment import AssignmentRead, GroupBrief
from app.schemas.common import CourseBrief, UserBrief
from app.schemas.enrollment import EnrollmentRead


def _user_brief(user: User) -> UserBrief:
    return UserBrief(id=user.id, full_name=user.full_name, email=user.email)


def _course_brief(course) -> CourseBrief:
    return CourseBrief(
        id=course.id,
        title=course.title,
        cover_image_url=storage.build_public_url(course.cover_image_url),
        status=course.status,
    )


def to_assignment_read(assignment: CourseAssignment) -> AssignmentRead:
    return AssignmentRead(
        id=assignment.id,
        course_id=assignment.course_id,
        is_required=assignment.is_required,
        due_date=assignment.due_date,
        overdue_action=assignment.overdue_action,
        status=assignment.status,
        created_by=_user_brief(assignment.creator),
        created_at=assignment.created_at,
        target_users=[_user_brief(link.user) for link in assignment.assignment_users],
        target_groups=[GroupBrief(id=link.group.id, name=link.group.name) for link in assignment.assignment_groups],
    )


def to_enrollment_read(enrollment: Enrollment) -> EnrollmentRead:
    return EnrollmentRead(
        id=enrollment.id,
        user=_user_brief(enrollment.user),
        course=_course_brief(enrollment.course),
        assignment_id=enrollment.assignment_id,
        enrollment_type=enrollment.enrollment_type,
        status=enrollment.status,
        is_required=enrollment.is_required,
        assigned_at=enrollment.assigned_at,
        started_at=enrollment.started_at,
        due_date=enrollment.due_date,
        completed_at=enrollment.completed_at,
    )


def _require_published_course(db: Session, course_id: uuid.UUID):
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status != "PUBLISHED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Users can only be enrolled in published courses.")
    return course


def _enroll_user_if_possible(
    db: Session,
    *,
    user_id: uuid.UUID,
    course_id: uuid.UUID,
    assignment_id: uuid.UUID | None,
    enrollment_type: str,
    is_required: bool,
    due_date: datetime | None,
    actor_id: uuid.UUID | None,
) -> bool:
    """Crea la matrícula si no hay una activa para ese usuario+curso (RN-008). Devuelve True si se creó."""
    if enrollment_repository.get_active_for_user_course(db, user_id=user_id, course_id=course_id) is not None:
        return False

    final_type = enrollment_type
    if enrollment_type == "MANUAL" and enrollment_repository.has_terminal_for_user_course(
        db, user_id=user_id, course_id=course_id
    ):
        final_type = "RETAKE"

    enrollment = enrollment_repository.create(
        db,
        user_id=user_id,
        course_id=course_id,
        assignment_id=assignment_id,
        enrollment_type=final_type,
        is_required=is_required,
        due_date=due_date,
    )
    db.flush()
    audit_repository.log_action(
        db,
        user_id=actor_id,
        action="ENROLLMENT_CREATED",
        entity_type="enrollment",
        entity_id=enrollment.id,
        new_data={"user_id": str(user_id), "course_id": str(course_id), "type": final_type},
    )
    return True


def create_assignment(
    db: Session,
    *,
    current_user: User,
    course_id: uuid.UUID,
    user_ids: list[uuid.UUID],
    group_ids: list[uuid.UUID],
    is_required: bool,
    due_date: datetime | None,
    overdue_action: str,
) -> tuple[CourseAssignment, int, int]:
    if not user_ids and not group_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Select at least one user or group.")

    _require_published_course(db, course_id)

    missing_users = set(user_ids) - {u.id for u in user_repository.get_many_by_ids(db, user_ids)}
    if missing_users:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Users not found: {', '.join(map(str, missing_users))}")
    for group_id in group_ids:
        if group_repository.get_by_id(db, group_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Group not found: {group_id}")

    assignment = assignment_repository.create(
        db,
        course_id=course_id,
        is_required=is_required,
        due_date=due_date,
        overdue_action=overdue_action,
        created_by=current_user.id,
    )
    db.flush()
    if user_ids:
        assignment_repository.add_user_targets(db, assignment_id=assignment.id, user_ids=user_ids)
    if group_ids:
        assignment_repository.add_group_targets(db, assignment_id=assignment.id, group_ids=group_ids)

    target_user_ids: set[uuid.UUID] = set(user_ids)
    for group_id in group_ids:
        target_user_ids.update(group_repository.list_member_user_ids(db, group_id))

    created = 0
    skipped = 0
    for user_id in target_user_ids:
        ok = _enroll_user_if_possible(
            db,
            user_id=user_id,
            course_id=course_id,
            assignment_id=assignment.id,
            enrollment_type="ASSIGNMENT",
            is_required=is_required,
            due_date=due_date,
            actor_id=current_user.id,
        )
        created += 1 if ok else 0
        skipped += 0 if ok else 1

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_ASSIGNMENT_CREATED",
        entity_type="course_assignment",
        entity_id=assignment.id,
        new_data={
            "course_id": str(course_id),
            "user_ids": [str(u) for u in user_ids],
            "group_ids": [str(g) for g in group_ids],
            "is_required": is_required,
        },
    )
    db.commit()

    detail = assignment_repository.get_detail(db, assignment.id)
    return detail, created, skipped


def list_assignments(db: Session, course_id: uuid.UUID) -> list[CourseAssignment]:
    return assignment_repository.list_by_course(db, course_id)


def update_assignment(
    db: Session,
    *,
    current_user: User,
    assignment_id: uuid.UUID,
    is_required: bool | None,
    due_date: datetime | None,
    due_date_set: bool,
    overdue_action: str | None,
    status_value: str | None,
) -> CourseAssignment:
    assignment = assignment_repository.get_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found.")

    if is_required is not None:
        assignment.is_required = is_required
    if due_date_set:
        assignment.due_date = due_date
    if overdue_action is not None:
        assignment.overdue_action = overdue_action
    if status_value is not None:
        assignment.status = status_value

    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_ASSIGNMENT_UPDATED",
        entity_type="course_assignment",
        entity_id=assignment.id,
    )
    db.commit()
    return assignment_repository.get_detail(db, assignment_id)


def create_manual_enrollments(
    db: Session,
    *,
    current_user: User,
    course_id: uuid.UUID,
    user_ids: list[uuid.UUID],
    is_required: bool,
    due_date: datetime | None,
) -> tuple[int, int, list[Enrollment]]:
    _require_published_course(db, course_id)

    missing_users = set(user_ids) - {u.id for u in user_repository.get_many_by_ids(db, user_ids)}
    if missing_users:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Users not found: {', '.join(map(str, missing_users))}")

    created = 0
    skipped = 0
    for user_id in user_ids:
        ok = _enroll_user_if_possible(
            db,
            user_id=user_id,
            course_id=course_id,
            assignment_id=None,
            enrollment_type="MANUAL",
            is_required=is_required,
            due_date=due_date,
            actor_id=current_user.id,
        )
        created += 1 if ok else 0
        skipped += 0 if ok else 1

    db.commit()

    enrollments = (
        [e for e in enrollment_repository.list_by_user(db, user_ids[0]) if e.course_id == course_id]
        if len(user_ids) == 1
        else []
    )
    return created, skipped, enrollments


def sync_group_assignment(
    db: Session, *, group_id: uuid.UUID, user_ids: list[uuid.UUID], actor_id: uuid.UUID | None
) -> None:
    """Matrícula automática (sección 22): al agregar usuarios a un grupo, se matriculan
    en los cursos con una asignación ACTIVE dirigida a ese grupo."""
    if not user_ids:
        return
    assignments = assignment_repository.list_active_by_group(db, group_id)
    for assignment in assignments:
        for user_id in user_ids:
            _enroll_user_if_possible(
                db,
                user_id=user_id,
                course_id=assignment.course_id,
                assignment_id=assignment.id,
                enrollment_type="ASSIGNMENT",
                is_required=assignment.is_required,
                due_date=assignment.due_date,
                actor_id=actor_id,
            )


def list_course_enrollments(
    db: Session, *, course_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[Enrollment], int]:
    items, total = enrollment_repository.list_by_course(db, course_id=course_id, page=page, page_size=page_size)
    for item in items:
        enrollment_repository.apply_overdue(db, item)
    db.commit()
    return items, total


def list_user_enrollments(db: Session, user_id: uuid.UUID) -> list[Enrollment]:
    items = enrollment_repository.list_by_user(db, user_id)
    for item in items:
        enrollment_repository.apply_overdue(db, item)
    db.commit()
    return items


def update_due_date(
    db: Session, *, current_user: User, enrollment_id: uuid.UUID, due_date: datetime | None
) -> Enrollment:
    enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if enrollment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enrollment not found.")
    old_due_date = enrollment.due_date
    enrollment.due_date = due_date
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="ENROLLMENT_DUE_DATE_CHANGED",
        entity_type="enrollment",
        entity_id=enrollment.id,
        old_data={"due_date": old_due_date.isoformat() if old_due_date else None},
        new_data={"due_date": due_date.isoformat() if due_date else None},
    )
    db.commit()
    return enrollment_repository.get_by_id(db, enrollment_id)


def cancel_enrollment(db: Session, *, current_user: User, enrollment_id: uuid.UUID) -> Enrollment:
    enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if enrollment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enrollment not found.")
    if enrollment.status == "CANCELLED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The enrollment is already cancelled.")

    enrollment.status = "CANCELLED"
    db.flush()
    audit_repository.log_action(
        db, user_id=current_user.id, action="ENROLLMENT_CANCELLED", entity_type="enrollment", entity_id=enrollment.id
    )
    db.commit()
    return enrollment_repository.get_by_id(db, enrollment_id)
