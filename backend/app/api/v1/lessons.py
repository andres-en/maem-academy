import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES, INSTRUCTOR
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.lesson import LessonDetailRead, LessonUpdate
from app.schemas.lesson_content import LessonContentRead, MoveRequest
from app.services import lesson_content_service, lesson_service

router = APIRouter(prefix="/lessons", tags=["courses"])

COURSE_ROLES = (*ADMIN_ROLES, INSTRUCTOR)


def _to_lesson_read(lesson) -> LessonDetailRead:
    return LessonDetailRead(
        id=lesson.id,
        module_id=lesson.module_id,
        title=lesson.title,
        description=lesson.description,
        position=lesson.position,
        completion_type=lesson.completion_type,
        contents=[],
    )


@router.put("/{lesson_id}", response_model=LessonDetailRead)
def update_lesson(
    lesson_id: uuid.UUID,
    payload: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> LessonDetailRead:
    lesson = lesson_service.update_lesson(
        db,
        current_user=current_user,
        lesson_id=lesson_id,
        title=payload.title,
        description=payload.description,
        completion_type=payload.completion_type,
    )
    return _to_lesson_read(lesson)


@router.delete("/{lesson_id}", status_code=204)
def delete_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> None:
    lesson_service.delete_lesson(db, current_user=current_user, lesson_id=lesson_id)


@router.post("/{lesson_id}/move", response_model=LessonDetailRead)
def move_lesson(
    lesson_id: uuid.UUID,
    payload: MoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> LessonDetailRead:
    lesson = lesson_service.move_lesson(db, current_user=current_user, lesson_id=lesson_id, direction=payload.direction)
    return _to_lesson_read(lesson)


@router.post("/{lesson_id}/contents", response_model=LessonContentRead, status_code=201)
async def create_content(
    lesson_id: uuid.UUID,
    content_type: str = Form(...),
    title: str | None = Form(None),
    text_content: str | None = Form(None),
    external_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> LessonContentRead:
    file_bytes = await file.read() if file is not None else None
    result = lesson_content_service.create_content(
        db,
        current_user=current_user,
        lesson_id=lesson_id,
        content_type=content_type,
        title=title,
        text_content=text_content,
        external_url=external_url,
        file_bytes=file_bytes,
        filename=file.filename if file is not None else None,
    )
    return LessonContentRead(**result)
