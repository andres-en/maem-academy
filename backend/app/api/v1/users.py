import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES, STAFF_ROLES, SUPERADMIN
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.group import GroupRead
from app.schemas.user import (
    ForceDeleteUserRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
    UserCreate,
    UserDetailRead,
    UserRead,
    UserStatusUpdate,
    UserUpdate,
)
from app.services import import_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


def _to_detail(user: User) -> UserDetailRead:
    groups = [
        GroupRead(
            id=ug.group.id,
            name=ug.group.name,
            description=ug.group.description,
            status=ug.group.status,
            created_at=ug.group.created_at,
        )
        for ug in user.user_groups
    ]
    return UserDetailRead(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        status=user.status,
        role=user.role,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        groups=groups,
    )


@router.get("", response_model=Page[UserRead])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role_id: uuid.UUID | None = None,
    status: str | None = None,
    group_id: uuid.UUID | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles(STAFF_ROLES)),
) -> Page[UserRead]:
    items, total = user_service.list_users(
        db, page=page, page_size=page_size, role_id=role_id, status_filter=status, group_id=group_id, search=search
    )
    return Page(items=[UserRead.model_validate(u) for u in items], total=total, page=page, page_size=page_size)


@router.get("/import/template")
def download_import_template() -> StreamingResponse:
    content = import_service.build_template()
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=users_template.xlsx"},
    )


@router.post("/import/validate", response_model=ImportPreviewResponse)
async def validate_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLES)),
) -> ImportPreviewResponse:
    content = await file.read()
    return import_service.preview_import(db, content)


@router.post("/import/confirm", response_model=ImportConfirmResponse)
async def confirm_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> ImportConfirmResponse:
    content = await file.read()
    return import_service.confirm_import(db, current_user=current_user, file_bytes=content)


@router.post("", response_model=UserDetailRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> UserDetailRead:
    user = user_service.create_user(
        db,
        current_user=current_user,
        full_name=payload.full_name,
        email=payload.email,
        role_id=payload.role_id,
        group_ids=payload.group_ids,
    )
    return _to_detail(user)


@router.get("/{user_id}", response_model=UserDetailRead)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles(STAFF_ROLES)),
) -> UserDetailRead:
    user = user_service.get_user_detail(db, user_id)
    return _to_detail(user)


@router.put("/{user_id}", response_model=UserDetailRead)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> UserDetailRead:
    user = user_service.update_user(
        db,
        current_user=current_user,
        user_id=user_id,
        full_name=payload.full_name,
        role_id=payload.role_id,
        group_ids=payload.group_ids,
    )
    return _to_detail(user)


@router.patch("/{user_id}/status", response_model=UserDetailRead)
def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> UserDetailRead:
    user = user_service.set_status(db, current_user=current_user, user_id=user_id, new_status=payload.status)
    return _to_detail(user)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> None:
    user_service.delete_user(db, current_user=current_user, user_id=user_id)


@router.delete("/{user_id}/force", status_code=204)
def force_delete_user(
    user_id: uuid.UUID,
    payload: ForceDeleteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles((SUPERADMIN,))),
) -> None:
    user_service.force_delete_user(db, current_user=current_user, user_id=user_id, confirm_email=payload.confirm_email)
