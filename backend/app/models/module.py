import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class CourseModule(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "course_modules"
    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_course_modules_position"),)

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="modules")  # noqa: F821
    lessons: Mapped[list["Lesson"]] = relationship(  # noqa: F821
        back_populates="module", order_by="Lesson.position", cascade="all, delete-orphan"
    )
