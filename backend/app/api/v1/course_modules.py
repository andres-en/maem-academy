import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES, INSTRUCTOR
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.lesson import LessonCreate, LessonDetailRead
from app.schemas.lesson_content import MoveRequest
from app.schemas.module import ModuleDetailRead, ModuleUpdate
from app.services import lesson_service, module_service

router = APIRouter(prefix="/course-modules", tags=["courses"])

COURSE_ROLES = (*ADMIN_ROLES, INSTRUCTOR)


def _to_module_read(module) -> ModuleDetailRead:
    return ModuleDetailRead(
        id=module.id,
        course_id=module.course_id,
        title=module.title,
        description=module.description,
        position=module.position,
        lessons=[],
    )


@router.put("/{module_id}", response_model=ModuleDetailRead)
def update_module(
    module_id: uuid.UUID,
    payload: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> ModuleDetailRead:
    module = module_service.update_module(
        db, current_user=current_user, module_id=module_id, title=payload.title, description=payload.description
    )
    return _to_module_read(module)


@router.delete("/{module_id}", status_code=204)
def delete_module(
    module_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> None:
    module_service.delete_module(db, current_user=current_user, module_id=module_id)


@router.post("/{module_id}/move", response_model=ModuleDetailRead)
def move_module(
    module_id: uuid.UUID,
    payload: MoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> ModuleDetailRead:
    module = module_service.move_module(db, current_user=current_user, module_id=module_id, direction=payload.direction)
    return _to_module_read(module)


@router.post("/{module_id}/lessons", response_model=LessonDetailRead, status_code=201)
def create_lesson(
    module_id: uuid.UUID,
    payload: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> LessonDetailRead:
    lesson = lesson_service.create_lesson(
        db,
        current_user=current_user,
        module_id=module_id,
        title=payload.title,
        description=payload.description,
        completion_type=payload.completion_type,
    )
    return LessonDetailRead(
        id=lesson.id,
        module_id=lesson.module_id,
        title=lesson.title,
        description=lesson.description,
        position=lesson.position,
        completion_type=lesson.completion_type,
        contents=[],
    )
