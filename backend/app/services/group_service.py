import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import User
from app.repositories import audit_repository, group_repository, user_repository
from app.services import enrollment_service
from app.services.deletion import run_delete_or_conflict


def list_groups(db: Session, *, status_filter: str | None = None) -> list[tuple[Group, int]]:
    return group_repository.list_groups(db, status=status_filter)


def get_group_detail(db: Session, group_id: uuid.UUID) -> Group:
    group = group_repository.get_with_members(db, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    return group


def _validate_user_ids(db: Session, user_ids: list[uuid.UUID]) -> None:
    if not user_ids:
        return
    found = user_repository.get_many_by_ids(db, user_ids)
    missing = set(user_ids) - {u.id for u in found}
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Users not found: {', '.join(map(str, missing))}")


def create_group(
    db: Session, *, current_user: User, name: str, description: str | None, user_ids: list[uuid.UUID]
) -> Group:
    _validate_user_ids(db, user_ids)
    group = group_repository.create(db, name=name, description=description)
    db.flush()
    if user_ids:
        group_repository.add_users(db, group_id=group.id, user_ids=user_ids)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="GROUP_CREATED",
        entity_type="group",
        entity_id=group.id,
        new_data={"name": name, "description": description, "user_ids": [str(u) for u in user_ids]},
    )
    db.commit()
    db.refresh(group)
    return group


def update_group(db: Session, *, current_user: User, group_id: uuid.UUID, name: str, description: str | None) -> Group:
    group = group_repository.get_by_id(db, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    old_data = {"name": group.name, "description": group.description}
    group.name = name
    group.description = description
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="GROUP_UPDATED",
        entity_type="group",
        entity_id=group.id,
        old_data=old_data,
        new_data={"name": name, "description": description},
    )
    db.commit()
    db.refresh(group)
    return group


def set_status(db: Session, *, current_user: User, group_id: uuid.UUID, new_status: str) -> Group:
    group = group_repository.get_by_id(db, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    old_status = group.status
    group.status = new_status
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="GROUP_STATUS_CHANGED",
        entity_type="group",
        entity_id=group.id,
        old_data={"status": old_status},
        new_data={"status": new_status},
    )
    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, *, current_user: User, group_id: uuid.UUID) -> None:
    group = group_repository.get_by_id(db, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    if group.status != "INACTIVE":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must deactivate the group before deleting it.")

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="GROUP_DELETED",
        entity_type="group",
        entity_id=group.id,
        old_data={"name": group.name},
    )
    run_delete_or_conflict(db, group, "Cannot delete: the group has related data.")


def add_users(db: Session, *, current_user: User, group_id: uuid.UUID, user_ids: list[uuid.UUID]) -> Group:
    group = group_repository.get_by_id(db, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    _validate_user_ids(db, user_ids)
    group_repository.add_users(db, group_id=group_id, user_ids=user_ids)
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="GROUP_MEMBERS_ADDED",
        entity_type="group",
        entity_id=group.id,
        new_data={"user_ids": [str(u) for u in user_ids]},
    )
    # Matrícula automática (sección 22): si el grupo tiene cursos obligatorios/asignados activos,
    # los nuevos miembros quedan matriculados automáticamente.
    enrollment_service.sync_group_assignment(db, group_id=group_id, user_ids=user_ids, actor_id=current_user.id)
    db.commit()
    return get_group_detail(db, group_id)


def remove_user(db: Session, *, current_user: User, group_id: uuid.UUID, user_id: uuid.UUID) -> Group:
    group = group_repository.get_by_id(db, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Group not found.")
    removed = group_repository.remove_user(db, group_id=group_id, user_id=user_id)
    if not removed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The user does not belong to this group.")
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="GROUP_MEMBER_REMOVED",
        entity_type="group",
        entity_id=group.id,
        new_data={"user_id": str(user_id)},
    )
    db.commit()
    return get_group_detail(db, group_id)
