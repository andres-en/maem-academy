import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES
from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryStatusUpdate, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    status: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> list[CategoryRead]:
    return [CategoryRead.model_validate(c) for c in category_service.list_categories(db, status_filter=status)]


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> CategoryRead:
    category = category_service.create_category(
        db, current_user=current_user, name=payload.name, description=payload.description
    )
    return CategoryRead.model_validate(category)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> CategoryRead:
    category = category_service.update_category(
        db, current_user=current_user, category_id=category_id, name=payload.name, description=payload.description
    )
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}/status", response_model=CategoryRead)
def update_category_status(
    category_id: uuid.UUID,
    payload: CategoryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> CategoryRead:
    category = category_service.set_status(
        db, current_user=current_user, category_id=category_id, new_status=payload.status
    )
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> None:
    category_service.delete_category(db, current_user=current_user, category_id=category_id)
