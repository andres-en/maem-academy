import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import storage
from app.core.file_validation import validate_file
from app.models.lesson import LESSON_CONTENT_TYPES, LessonContent
from app.models.user import User
from app.repositories import (
    audit_repository,
    course_repository,
    lesson_content_repository,
    lesson_repository,
    module_repository,
)
from app.services.course_permissions import ensure_can_edit_course

FILE_CONTENT_TYPES = {"IMAGE", "VIDEO", "AUDIO", "PDF"}
URL_CONTENT_TYPES = {"YOUTUBE", "VIMEO", "LINK"}

_MIME_BY_EXTENSION = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".pdf": "application/pdf",
}


def _guess_mime(filename: str) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return _MIME_BY_EXTENSION.get(ext, "application/octet-stream")


def _load_lesson_and_course(db: Session, lesson_id: uuid.UUID):
    lesson = lesson_repository.get_by_id(db, lesson_id)
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found.")
    module = module_repository.get_by_id(db, lesson.module_id)
    course = course_repository.get_by_id(db, module.course_id)
    return lesson, course


def _load_content_with_course(db: Session, content_id: uuid.UUID):
    content = lesson_content_repository.get_by_id(db, content_id)
    if content is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Content not found.")
    lesson, course = _load_lesson_and_course(db, content.lesson_id)
    return content, course


def _to_read_dict(content: LessonContent) -> dict:
    return {
        "id": content.id,
        "lesson_id": content.lesson_id,
        "content_type": content.content_type,
        "title": content.title,
        "position": content.position,
        "text_content": content.text_content,
        "external_url": content.external_url,
        "file_url": storage.build_public_url(content.file_url),
    }


def create_content(
    db: Session,
    *,
    current_user: User,
    lesson_id: uuid.UUID,
    content_type: str,
    title: str | None,
    text_content: str | None,
    external_url: str | None,
    file_bytes: bytes | None,
    filename: str | None,
) -> dict:
    if content_type not in LESSON_CONTENT_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid content type.")

    lesson, course = _load_lesson_and_course(db, lesson_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    file_key = None
    final_text = None
    final_url = None

    if content_type in FILE_CONTENT_TYPES:
        if not file_bytes or not filename:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A file is required for this content type.")
        validate_file(content_type=content_type, filename=filename, data=file_bytes)
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        file_key = f"courses/{course.id}/lessons/{lesson_id}/{uuid.uuid4()}{ext}"
        storage.upload_bytes(key=file_key, data=file_bytes, content_type=_guess_mime(filename))
    elif content_type == "TEXT":
        if not text_content:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Text content cannot be empty.")
        final_text = text_content
    elif content_type in URL_CONTENT_TYPES:
        if not external_url:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A URL is required for this content type.")
        final_url = external_url

    content = lesson_content_repository.create(
        db,
        lesson_id=lesson_id,
        content_type=content_type,
        title=title,
        text_content=final_text,
        file_url=file_key,
        external_url=final_url,
    )
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_CONTENT_CREATED",
        entity_type="lesson_content",
        entity_id=content.id,
        new_data={"lesson_id": str(lesson_id), "content_type": content_type},
    )
    db.commit()
    db.refresh(content)
    return _to_read_dict(content)


def update_content(
    db: Session,
    *,
    current_user: User,
    content_id: uuid.UUID,
    title: str | None,
    text_content: str | None,
    external_url: str | None,
) -> dict:
    content, course = _load_content_with_course(db, content_id)
    ensure_can_edit_course(db, course, current_user)

    content.title = title
    if content.content_type == "TEXT" and text_content is not None:
        content.text_content = text_content
    if content.content_type in URL_CONTENT_TYPES and external_url is not None:
        content.external_url = external_url

    db.commit()
    db.refresh(content)
    return _to_read_dict(content)


def delete_content(db: Session, *, current_user: User, content_id: uuid.UUID) -> None:
    content, course = _load_content_with_course(db, content_id)
    ensure_can_edit_course(db, course, current_user)

    if content.file_url:
        storage.delete_object(content.file_url)

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_CONTENT_DELETED",
        entity_type="lesson_content",
        entity_id=content.id,
    )
    db.delete(content)
    db.commit()


def move_content(db: Session, *, current_user: User, content_id: uuid.UUID, direction: str) -> dict:
    content, course = _load_content_with_course(db, content_id)
    ensure_can_edit_course(db, course, current_user)
    sibling = lesson_content_repository.get_sibling(db, content, direction)
    if sibling is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is no neighboring content in that direction.")
    lesson_content_repository.swap_positions(db, content, sibling)
    db.commit()
    db.refresh(content)
    return _to_read_dict(content)
