import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.category import Category
from app.models.course import Course, CourseCategory, CourseCollaborator
from app.models.lesson import Lesson
from app.models.module import CourseModule


def _detail_options():
    return (
        joinedload(Course.owner),
        joinedload(Course.reviewer),
        selectinload(Course.categories),
        selectinload(Course.collaborator_links).joinedload(CourseCollaborator.user),
        selectinload(Course.modules).selectinload(CourseModule.lessons).selectinload(Lesson.contents),
    )


def get_by_id(db: Session, course_id: uuid.UUID) -> Course | None:
    return db.get(Course, course_id)


def get_detail(db: Session, course_id: uuid.UUID) -> Course | None:
    stmt = select(Course).where(Course.id == course_id).options(*_detail_options())
    return db.scalar(stmt)


def list_courses(
    db: Session,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    category_id: uuid.UUID | None = None,
    mine_user_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Course], int]:
    stmt = select(Course).options(joinedload(Course.owner), selectinload(Course.categories))
    count_stmt = select(func.count(func.distinct(Course.id))).select_from(Course)

    if status:
        stmt = stmt.where(Course.status == status)
        count_stmt = count_stmt.where(Course.status == status)

    if category_id:
        stmt = stmt.join(CourseCategory, CourseCategory.course_id == Course.id).where(
            CourseCategory.category_id == category_id
        )
        count_stmt = count_stmt.join(CourseCategory, CourseCategory.course_id == Course.id).where(
            CourseCategory.category_id == category_id
        )

    if mine_user_id:
        collab_subquery = select(CourseCollaborator.course_id).where(CourseCollaborator.user_id == mine_user_id)
        condition = or_(Course.owner_id == mine_user_id, Course.id.in_(collab_subquery))
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if search:
        pattern = f"%{search.lower()}%"
        stmt = stmt.where(func.lower(Course.title).like(pattern))
        count_stmt = count_stmt.where(func.lower(Course.title).like(pattern))

    total = db.scalar(count_stmt) or 0
    stmt = stmt.order_by(Course.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).unique())
    return items, total


def create(
    db: Session, *, title: str, description: str | None, estimated_duration_minutes: int | None, owner_id: uuid.UUID
) -> Course:
    course = Course(
        title=title,
        description=description,
        estimated_duration_minutes=estimated_duration_minutes,
        owner_id=owner_id,
        status="DRAFT",
    )
    db.add(course)
    return course


def set_categories(db: Session, course: Course, category_ids: list[uuid.UUID]) -> None:
    if not category_ids:
        course.categories = []
        return
    categories = list(db.scalars(select(Category).where(Category.id.in_(category_ids))))
    course.categories = categories


def add_collaborators(db: Session, *, course_id: uuid.UUID, user_ids: list[uuid.UUID], added_by: uuid.UUID) -> None:
    existing = set(
        db.scalars(
            select(CourseCollaborator.user_id).where(
                CourseCollaborator.course_id == course_id, CourseCollaborator.user_id.in_(user_ids)
            )
        )
    )
    for user_id in user_ids:
        if user_id not in existing and user_id != added_by:
            db.add(CourseCollaborator(course_id=course_id, user_id=user_id, added_by=added_by))


def remove_collaborator(db: Session, *, course_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    link = db.get(CourseCollaborator, {"course_id": course_id, "user_id": user_id})
    if link is None:
        return False
    db.delete(link)
    return True


def is_owner_or_collaborator(db: Session, *, course_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    link = db.get(CourseCollaborator, {"course_id": course_id, "user_id": user_id})
    if link is not None:
        return True
    course = db.get(Course, course_id)
    return course is not None and course.owner_id == user_id
