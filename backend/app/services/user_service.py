import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import audit_repository, enrollment_repository, group_repository, role_repository, user_repository
from app.services.deletion import run_delete_or_conflict


def _validate_role(db: Session, role_id: uuid.UUID) -> None:
    if role_repository.get_by_id(db, role_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid role.")


def _validate_groups(db: Session, group_ids: list[uuid.UUID]) -> None:
    for group_id in group_ids:
        if group_repository.get_by_id(db, group_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Group not found: {group_id}")


def list_users(
    db: Session,
    *,
    page: int,
    page_size: int,
    role_id: uuid.UUID | None,
    status_filter: str | None,
    group_id: uuid.UUID | None,
    search: str | None,
) -> tuple[list[User], int]:
    return user_repository.list_users(
        db,
        page=page,
        page_size=page_size,
        role_id=role_id,
        status=status_filter,
        group_id=group_id,
        search=search,
    )


def get_user_detail(db: Session, user_id: uuid.UUID) -> User:
    user = user_repository.get_with_groups(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return user


def create_user(
    db: Session,
    *,
    current_user: User,
    full_name: str,
    email: str,
    role_id: uuid.UUID,
    group_ids: list[uuid.UUID],
) -> User:
    if user_repository.get_by_email(db, email):
        raise HTTPException(status.HTTP_409_CONFLICT, "A user with that email already exists.")
    _validate_role(db, role_id)
    _validate_groups(db, group_ids)

    user = user_repository.create(db, full_name=full_name, email=email, role_id=role_id)
    db.flush()
    if group_ids:
        user_repository.set_groups(db, user_id=user.id, group_ids=group_ids)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="USER_CREATED",
        entity_type="user",
        entity_id=user.id,
        new_data={"full_name": full_name, "email": email, "role_id": str(role_id)},
    )
    db.commit()
    return get_user_detail(db, user.id)


def update_user(
    db: Session,
    *,
    current_user: User,
    user_id: uuid.UUID,
    full_name: str,
    role_id: uuid.UUID,
    group_ids: list[uuid.UUID],
) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    _validate_role(db, role_id)
    _validate_groups(db, group_ids)

    old_data = {"full_name": user.full_name, "role_id": str(user.role_id)}
    user.full_name = full_name
    user.role_id = role_id
    user_repository.set_groups(db, user_id=user.id, group_ids=group_ids)
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="USER_UPDATED",
        entity_type="user",
        entity_id=user.id,
        old_data=old_data,
        new_data={"full_name": full_name, "role_id": str(role_id)},
    )
    db.commit()
    return get_user_detail(db, user.id)


def delete_user(db: Session, *, current_user: User, user_id: uuid.UUID) -> None:
    if user_id == current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot delete your own user.")
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if user.status != "INACTIVE":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must deactivate the user before deleting it.")

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="USER_DELETED",
        entity_type="user",
        entity_id=user.id,
        old_data={"full_name": user.full_name, "email": user.email},
    )
    run_delete_or_conflict(
        db, user, "Cannot delete: the user has created courses, enrollments or other related activity."
    )


def force_delete_user(db: Session, *, current_user: User, user_id: uuid.UUID, confirm_email: str) -> None:
    """Elimina al usuario junto con sus PROPIAS matrículas, progreso y resultados de evaluación
    (como estudiante). Si el usuario posee cursos, creó asignaciones o agregó colaboradores, la
    base de datos sigue bloqueando el borrado (ON DELETE RESTRICT) — esto no cascada hacia cursos
    ni afecta el historial de otros usuarios. Irreversible — solo para SUPERADMIN (ver router)."""
    if user_id == current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot delete your own user.")
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if user.status != "INACTIVE":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must deactivate the user before deleting it.")
    if confirm_email != user.email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The email entered does not match the user's email.")

    enrollments_count = enrollment_repository.count_by_user(db, user_id)

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="USER_FORCE_DELETED",
        entity_type="user",
        entity_id=user.id,
        old_data={"full_name": user.full_name, "email": user.email, "enrollments_deleted": enrollments_count},
    )
    enrollment_repository.delete_all_by_user(db, user_id)
    run_delete_or_conflict(
        db,
        user,
        "Cannot delete: the user owns courses, created assignments or added collaborators. "
        "Reassign those items to another user before forcing the deletion.",
    )


def set_status(db: Session, *, current_user: User, user_id: uuid.UUID, new_status: str) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    old_status = user.status
    user.status = new_status
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="USER_STATUS_CHANGED",
        entity_type="user",
        entity_id=user.id,
        old_data={"status": old_status},
        new_data={"status": new_status},
    )
    db.commit()
    return get_user_detail(db, user.id)
