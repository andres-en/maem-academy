import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES, STAFF_ROLES
from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.group import (
    GroupAddUsersRequest,
    GroupCreate,
    GroupDetailRead,
    GroupMemberRead,
    GroupRead,
    GroupStatusUpdate,
    GroupUpdate,
)
from app.services import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


def _to_detail(group) -> GroupDetailRead:
    members = [GroupMemberRead.model_validate(ug.user) for ug in group.user_groups]
    return GroupDetailRead(
        id=group.id,
        name=group.name,
        description=group.description,
        status=group.status,
        created_at=group.created_at,
        member_count=len(members),
        members=members,
    )


@router.get("", response_model=list[GroupRead])
def list_groups(
    status: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> list[GroupRead]:
    pairs = group_service.list_groups(db, status_filter=status)
    return [
        GroupRead(
            id=g.id,
            name=g.name,
            description=g.description,
            status=g.status,
            created_at=g.created_at,
            member_count=count,
        )
        for g, count in pairs
    ]


@router.post("", response_model=GroupDetailRead, status_code=201)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> GroupDetailRead:
    created = group_service.create_group(
        db, current_user=current_user, name=payload.name, description=payload.description, user_ids=payload.user_ids
    )
    return _to_detail(group_service.get_group_detail(db, created.id))


@router.get("/{group_id}", response_model=GroupDetailRead)
def get_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(STAFF_ROLES)),
) -> GroupDetailRead:
    group = group_service.get_group_detail(db, group_id)
    return _to_detail(group)


@router.put("/{group_id}", response_model=GroupDetailRead)
def update_group(
    group_id: uuid.UUID,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> GroupDetailRead:
    group_service.update_group(
        db, current_user=current_user, group_id=group_id, name=payload.name, description=payload.description
    )
    return _to_detail(group_service.get_group_detail(db, group_id))


@router.patch("/{group_id}/status", response_model=GroupDetailRead)
def update_group_status(
    group_id: uuid.UUID,
    payload: GroupStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> GroupDetailRead:
    group_service.set_status(db, current_user=current_user, group_id=group_id, new_status=payload.status)
    return _to_detail(group_service.get_group_detail(db, group_id))


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> None:
    group_service.delete_group(db, current_user=current_user, group_id=group_id)


@router.post("/{group_id}/users", response_model=GroupDetailRead)
def add_group_users(
    group_id: uuid.UUID,
    payload: GroupAddUsersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> GroupDetailRead:
    group = group_service.add_users(db, current_user=current_user, group_id=group_id, user_ids=payload.user_ids)
    return _to_detail(group)


@router.delete("/{group_id}/users/{user_id}", response_model=GroupDetailRead)
def remove_group_user(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> GroupDetailRead:
    group = group_service.remove_user(db, current_user=current_user, group_id=group_id, user_id=user_id)
    return _to_detail(group)
