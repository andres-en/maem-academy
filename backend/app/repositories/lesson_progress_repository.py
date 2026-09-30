import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.progress import LessonProgress


def get(db: Session, *, enrollment_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonProgress | None:
    stmt = select(LessonProgress).where(
        LessonProgress.enrollment_id == enrollment_id, LessonProgress.lesson_id == lesson_id
    )
    return db.scalar(stmt)


def list_by_enrollment(db: Session, enrollment_id: uuid.UUID) -> list[LessonProgress]:
    stmt = select(LessonProgress).where(LessonProgress.enrollment_id == enrollment_id)
    return list(db.scalars(stmt))


def ensure_started(db: Session, *, enrollment_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonProgress:
    progress = get(db, enrollment_id=enrollment_id, lesson_id=lesson_id)
    if progress is None:
        progress = LessonProgress(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
            status="IN_PROGRESS",
            progress_percentage=0,
            started_at=datetime.now(UTC),
        )
        db.add(progress)
        db.flush()
    return progress


def upsert_completed(db: Session, *, enrollment_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonProgress:
    progress = get(db, enrollment_id=enrollment_id, lesson_id=lesson_id)
    now = datetime.now(UTC)
    if progress is None:
        progress = LessonProgress(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
            status="COMPLETED",
            progress_percentage=100,
            started_at=now,
            completed_at=now,
        )
        db.add(progress)
    else:
        progress.status = "COMPLETED"
        progress.progress_percentage = 100
        if progress.started_at is None:
            progress.started_at = now
        progress.completed_at = now
    db.flush()
    return progress
