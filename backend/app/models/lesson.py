import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

LESSON_COMPLETION_TYPES = ("MANUAL", "AUTO")
LESSON_CONTENT_TYPES = ("TEXT", "VIDEO", "PDF", "IMAGE", "AUDIO", "YOUTUBE", "VIMEO", "LINK")


class Lesson(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "position", name="uq_lessons_position"),
        CheckConstraint(f"completion_type IN {LESSON_COMPLETION_TYPES}", name="completion_type_valid"),
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_type: Mapped[str] = mapped_column(String(20), nullable=False, default="MANUAL")

    module: Mapped["CourseModule"] = relationship(back_populates="lessons")  # noqa: F821
    contents: Mapped[list["LessonContent"]] = relationship(
        back_populates="lesson", order_by="LessonContent.position", cascade="all, delete-orphan"
    )


class LessonContent(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "lesson_contents"
    __table_args__ = (
        UniqueConstraint("lesson_id", "position", name="uq_lesson_contents_position"),
        CheckConstraint(f"content_type IN {LESSON_CONTENT_TYPES}", name="content_type_valid"),
    )

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="contents")
