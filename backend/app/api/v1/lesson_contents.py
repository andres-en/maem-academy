import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES, INSTRUCTOR
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.lesson_content import LessonContentRead, LessonContentUpdate, MoveRequest
from app.services import lesson_content_service

router = APIRouter(prefix="/lesson-contents", tags=["courses"])

COURSE_ROLES = (*ADMIN_ROLES, INSTRUCTOR)


@router.put("/{content_id}", response_model=LessonContentRead)
def update_content(
    content_id: uuid.UUID,
    payload: LessonContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> LessonContentRead:
    result = lesson_content_service.update_content(
        db,
        current_user=current_user,
        content_id=content_id,
        title=payload.title,
        text_content=payload.text_content,
        external_url=payload.external_url,
    )
    return LessonContentRead(**result)


@router.delete("/{content_id}", status_code=204)
def delete_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> None:
    lesson_content_service.delete_content(db, current_user=current_user, content_id=content_id)


@router.post("/{content_id}/move", response_model=LessonContentRead)
def move_content(
    content_id: uuid.UUID,
    payload: MoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> LessonContentRead:
    result = lesson_content_service.move_content(
        db, current_user=current_user, content_id=content_id, direction=payload.direction
    )
    return LessonContentRead(**result)
