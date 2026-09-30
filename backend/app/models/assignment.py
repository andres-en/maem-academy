import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

ASSIGNMENT_OVERDUE_ACTIONS = ("ALLOW_CONTINUE", "BLOCK")
ASSIGNMENT_STATUSES = ("ACTIVE", "INACTIVE")


class CourseAssignment(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "course_assignments"
    __table_args__ = (
        CheckConstraint(f"overdue_action IN {ASSIGNMENT_OVERDUE_ACTIONS}", name="overdue_action_valid"),
        CheckConstraint(f"status IN {ASSIGNMENT_STATUSES}", name="status_valid"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    overdue_action: Mapped[str] = mapped_column(String(30), nullable=False, default="ALLOW_CONTINUE")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    course: Mapped["Course"] = relationship()  # noqa: F821
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])  # noqa: F821
    assignment_users: Mapped[list["CourseAssignmentUser"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )
    assignment_groups: Mapped[list["CourseAssignmentGroup"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )


class CourseAssignmentUser(Base):
    __tablename__ = "course_assignment_users"

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("course_assignments.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    assignment: Mapped["CourseAssignment"] = relationship(back_populates="assignment_users")
    user: Mapped["User"] = relationship()  # noqa: F821


class CourseAssignmentGroup(Base):
    __tablename__ = "course_assignment_groups"

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("course_assignments.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )

    assignment: Mapped["CourseAssignment"] = relationship(back_populates="assignment_groups")
    group: Mapped["Group"] = relationship()  # noqa: F821
