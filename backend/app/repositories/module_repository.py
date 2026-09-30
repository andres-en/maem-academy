import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.module import CourseModule


def get_by_id(db: Session, module_id: uuid.UUID) -> CourseModule | None:
    return db.get(CourseModule, module_id)


def list_by_course(db: Session, course_id: uuid.UUID) -> list[CourseModule]:
    stmt = select(CourseModule).where(CourseModule.course_id == course_id).order_by(CourseModule.position)
    return list(db.scalars(stmt))


def next_position(db: Session, course_id: uuid.UUID) -> int:
    current_max = db.scalar(select(func.max(CourseModule.position)).where(CourseModule.course_id == course_id))
    return (current_max if current_max is not None else -1) + 1


def create(db: Session, *, course_id: uuid.UUID, title: str, description: str | None) -> CourseModule:
    module = CourseModule(
        course_id=course_id, title=title, description=description, position=next_position(db, course_id)
    )
    db.add(module)
    return module


def get_sibling(db: Session, module: CourseModule, direction: str) -> CourseModule | None:
    stmt = select(CourseModule).where(CourseModule.course_id == module.course_id)
    if direction == "up":
        stmt = stmt.where(CourseModule.position < module.position).order_by(CourseModule.position.desc())
    else:
        stmt = stmt.where(CourseModule.position > module.position).order_by(CourseModule.position.asc())
    return db.scalar(stmt.limit(1))


def swap_positions(db: Session, item_a: CourseModule, item_b: CourseModule) -> None:
    pos_a, pos_b = item_a.position, item_b.position
    item_a.position = -1
    db.flush()
    item_b.position = pos_a
    db.flush()
    item_a.position = pos_b
    db.flush()
