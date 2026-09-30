import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.module import CourseModule


def get_by_id(db: Session, lesson_id: uuid.UUID) -> Lesson | None:
    return db.get(Lesson, lesson_id)


def count_by_course(db: Session, course_id: uuid.UUID) -> int:
    stmt = (
        select(func.count())
        .select_from(Lesson)
        .join(CourseModule, CourseModule.id == Lesson.module_id)
        .where(CourseModule.course_id == course_id)
    )
    return db.scalar(stmt) or 0


def next_position(db: Session, module_id: uuid.UUID) -> int:
    current_max = db.scalar(select(func.max(Lesson.position)).where(Lesson.module_id == module_id))
    return (current_max if current_max is not None else -1) + 1


def create(db: Session, *, module_id: uuid.UUID, title: str, description: str | None, completion_type: str) -> Lesson:
    lesson = Lesson(
        module_id=module_id,
        title=title,
        description=description,
        completion_type=completion_type,
        position=next_position(db, module_id),
    )
    db.add(lesson)
    return lesson


def get_sibling(db: Session, lesson: Lesson, direction: str) -> Lesson | None:
    stmt = select(Lesson).where(Lesson.module_id == lesson.module_id)
    if direction == "up":
        stmt = stmt.where(Lesson.position < lesson.position).order_by(Lesson.position.desc())
    else:
        stmt = stmt.where(Lesson.position > lesson.position).order_by(Lesson.position.asc())
    return db.scalar(stmt.limit(1))


def swap_positions(db: Session, item_a: Lesson, item_b: Lesson) -> None:
    pos_a, pos_b = item_a.position, item_b.position
    item_a.position = -1
    db.flush()
    item_b.position = pos_a
    db.flush()
    item_a.position = pos_b
    db.flush()
