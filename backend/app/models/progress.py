import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPKMixin

LESSON_PROGRESS_STATUSES = ("NOT_STARTED", "IN_PROGRESS", "COMPLETED")


class LessonProgress(UUIDPKMixin, Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "lesson_id", name="uq_lesson_progress_enrollment_lesson"),
        CheckConstraint(f"status IN {LESSON_PROGRESS_STATUSES}", name="status_valid"),
        CheckConstraint("progress_percentage >= 0 AND progress_percentage <= 100", name="progress_percentage_range"),
        Index("ix_lesson_progress_enrollment_id", "enrollment_id"),
        Index("ix_lesson_progress_lesson_id", "lesson_id"),
        Index("ix_lesson_progress_status", "status"),
    )

    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NOT_STARTED")
    progress_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    enrollment: Mapped["Enrollment"] = relationship()  # noqa: F821
    lesson: Mapped["Lesson"] = relationship()  # noqa: F821
