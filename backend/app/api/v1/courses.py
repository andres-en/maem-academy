import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core import storage
from app.core.constants import ADMIN_ROLES, INSTRUCTOR, SUPERADMIN
from app.core.deps import require_roles
from app.core.file_validation import validate_file
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.course import (
    CollaboratorAddRequest,
    CourseCreate,
    CourseDetailRead,
    CourseRead,
    CourseUpdate,
    ForceDeleteRequest,
    ReviewCommentRequest,
)
from app.schemas.module import ModuleCreate, ModuleDetailRead
from app.services import course_service, module_service

router = APIRouter(prefix="/courses", tags=["courses"])

COURSE_ROLES = (*ADMIN_ROLES, INSTRUCTOR)


@router.get("", response_model=Page[CourseRead])
def list_courses(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    category_id: uuid.UUID | None = None,
    mine: bool = False,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> Page[CourseRead]:
    items, total = course_service.list_courses(
        db,
        page=page,
        page_size=page_size,
        status_filter=status,
        category_id=category_id,
        mine_user_id=current_user.id if mine else None,
        search=search,
    )
    return Page(items=[course_service.to_course_read(c) for c in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=CourseDetailRead, status_code=201)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.create_course(
        db,
        current_user=current_user,
        title=payload.title,
        description=payload.description,
        estimated_duration_minutes=payload.estimated_duration_minutes,
        category_ids=payload.category_ids,
    )
    return course_service.to_course_detail(course)


@router.get("/{course_id}", response_model=CourseDetailRead)
def get_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.get_course_detail(db, course_id)
    return course_service.to_course_detail(course)


@router.put("/{course_id}", response_model=CourseDetailRead)
def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.update_course(
        db,
        current_user=current_user,
        course_id=course_id,
        title=payload.title,
        description=payload.description,
        estimated_duration_minutes=payload.estimated_duration_minutes,
        category_ids=payload.category_ids,
    )
    return course_service.to_course_detail(course)


@router.patch("/{course_id}/cover-image", response_model=CourseDetailRead)
async def update_cover_image(
    course_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    data = await file.read()
    validate_file(content_type="IMAGE", filename=file.filename or "", data=data)
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    key = f"courses/{course_id}/cover/{uuid.uuid4()}{ext}"
    storage.upload_bytes(key=key, data=data, content_type=file.content_type or "application/octet-stream")
    course = course_service.update_cover_image(db, current_user=current_user, course_id=course_id, object_key=key)
    return course_service.to_course_detail(course)


@router.post("/{course_id}/collaborators", response_model=CourseDetailRead)
def add_collaborators(
    course_id: uuid.UUID,
    payload: CollaboratorAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.add_collaborators(
        db, current_user=current_user, course_id=course_id, user_ids=payload.user_ids
    )
    return course_service.to_course_detail(course)


@router.delete("/{course_id}/collaborators/{user_id}", response_model=CourseDetailRead)
def remove_collaborator(
    course_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.remove_collaborator(db, current_user=current_user, course_id=course_id, user_id=user_id)
    return course_service.to_course_detail(course)


@router.post("/{course_id}/submit-review", response_model=CourseDetailRead)
def submit_review(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.submit_for_review(db, current_user=current_user, course_id=course_id)
    return course_service.to_course_detail(course)


@router.post("/{course_id}/approve", response_model=CourseDetailRead)
def approve(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.approve_course(db, current_user=current_user, course_id=course_id)
    return course_service.to_course_detail(course)


@router.post("/{course_id}/request-changes", response_model=CourseDetailRead)
def request_changes(
    course_id: uuid.UUID,
    payload: ReviewCommentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.request_changes(db, current_user=current_user, course_id=course_id, comment=payload.comment)
    return course_service.to_course_detail(course)


@router.post("/{course_id}/publish", response_model=CourseDetailRead)
def publish(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.publish_course(db, current_user=current_user, course_id=course_id)
    return course_service.to_course_detail(course)


@router.post("/{course_id}/archive", response_model=CourseDetailRead)
def archive(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> CourseDetailRead:
    course = course_service.archive_course(db, current_user=current_user, course_id=course_id)
    return course_service.to_course_detail(course)


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> None:
    course_service.delete_course(db, current_user=current_user, course_id=course_id)


@router.delete("/{course_id}/force", status_code=204)
def force_delete_course(
    course_id: uuid.UUID,
    payload: ForceDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles((SUPERADMIN,))),
) -> None:
    course_service.force_delete_course(
        db, current_user=current_user, course_id=course_id, confirm_title=payload.confirm_title
    )


@router.post("/{course_id}/modules", response_model=ModuleDetailRead, status_code=201)
def create_module(
    course_id: uuid.UUID,
    payload: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> ModuleDetailRead:
    module = module_service.create_module(
        db, current_user=current_user, course_id=course_id, title=payload.title, description=payload.description
    )
    return ModuleDetailRead(
        id=module.id,
        course_id=module.course_id,
        title=module.title,
        description=module.description,
        position=module.position,
        lessons=[],
    )
