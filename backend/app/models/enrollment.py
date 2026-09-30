import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

ENROLLMENT_TYPES = ("ASSIGNMENT", "MANUAL", "RETAKE")
ENROLLMENT_STATUSES = (
    "ASSIGNED",
    "IN_PROGRESS",
    "COMPLETED",
    "PASSED",
    "FAILED",
    "OVERDUE",
    "BLOCKED",
    "CANCELLED",
)

ACTIVE_ENROLLMENT_STATUSES = ("ASSIGNED", "IN_PROGRESS", "OVERDUE", "BLOCKED")


class Enrollment(UUIDPKMixin, TimestampMixin, Base):
    """No se aplica UNIQUE(user_id, course_id): un usuario puede repetir un curso
    y cada realización es una matrícula independiente (ver sección 27 del modelo de datos)."""

    __tablename__ = "enrollments"
    __table_args__ = (
        CheckConstraint(f"enrollment_type IN {ENROLLMENT_TYPES}", name="enrollment_type_valid"),
        CheckConstraint(f"status IN {ENROLLMENT_STATUSES}", name="status_valid"),
        Index("ix_enrollments_user_id", "user_id"),
        Index("ix_enrollments_course_id", "course_id"),
        Index("ix_enrollments_status", "status"),
        Index("ix_enrollments_due_date", "due_date"),
        Index("ix_enrollments_user_id_course_id", "user_id", "course_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("course_assignments.id", ondelete="SET NULL"), nullable=True
    )
    enrollment_type: Mapped[str] = mapped_column(String(30), nullable=False, default="MANUAL")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ASSIGNED")
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821
    course: Mapped["Course"] = relationship()  # noqa: F821
    assignment: Mapped["CourseAssignment | None"] = relationship()  # noqa: F821
