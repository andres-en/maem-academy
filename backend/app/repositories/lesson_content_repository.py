import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lesson import LessonContent


def get_by_id(db: Session, content_id: uuid.UUID) -> LessonContent | None:
    return db.get(LessonContent, content_id)


def next_position(db: Session, lesson_id: uuid.UUID) -> int:
    current_max = db.scalar(select(func.max(LessonContent.position)).where(LessonContent.lesson_id == lesson_id))
    return (current_max if current_max is not None else -1) + 1


def create(
    db: Session,
    *,
    lesson_id: uuid.UUID,
    content_type: str,
    title: str | None,
    text_content: str | None,
    file_url: str | None,
    external_url: str | None,
) -> LessonContent:
    content = LessonContent(
        lesson_id=lesson_id,
        content_type=content_type,
        title=title,
        text_content=text_content,
        file_url=file_url,
        external_url=external_url,
        position=next_position(db, lesson_id),
    )
    db.add(content)
    return content


def get_sibling(db: Session, content: LessonContent, direction: str) -> LessonContent | None:
    stmt = select(LessonContent).where(LessonContent.lesson_id == content.lesson_id)
    if direction == "up":
        stmt = stmt.where(LessonContent.position < content.position).order_by(LessonContent.position.desc())
    else:
        stmt = stmt.where(LessonContent.position > content.position).order_by(LessonContent.position.asc())
    return db.scalar(stmt.limit(1))


def swap_positions(db: Session, item_a: LessonContent, item_b: LessonContent) -> None:
    pos_a, pos_b = item_a.position, item_b.position
    item_a.position = -1
    db.flush()
    item_b.position = pos_a
    db.flush()
    item_a.position = pos_b
    db.flush()
