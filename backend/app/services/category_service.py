import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.user import User
from app.repositories import audit_repository, category_repository
from app.services.deletion import run_delete_or_conflict


def list_categories(db: Session, *, status_filter: str | None = None) -> list[Category]:
    return category_repository.list_categories(db, status=status_filter)


def create_category(db: Session, *, current_user: User, name: str, description: str | None) -> Category:
    if category_repository.get_by_name(db, name):
        raise HTTPException(status.HTTP_409_CONFLICT, "A category with that name already exists.")
    category = category_repository.create(db, name=name, description=description)
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="CATEGORY_CREATED",
        entity_type="category",
        entity_id=category.id,
        new_data={"name": name, "description": description},
    )
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session, *, current_user: User, category_id: uuid.UUID, name: str, description: str | None
) -> Category:
    category = category_repository.get_by_id(db, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found.")
    existing = category_repository.get_by_name(db, name)
    if existing and existing.id != category.id:
        raise HTTPException(status.HTTP_409_CONFLICT, "A category with that name already exists.")

    old_data = {"name": category.name, "description": category.description}
    category.name = name
    category.description = description
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="CATEGORY_UPDATED",
        entity_type="category",
        entity_id=category.id,
        old_data=old_data,
        new_data={"name": name, "description": description},
    )
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, *, current_user: User, category_id: uuid.UUID) -> None:
    category = category_repository.get_by_id(db, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found.")
    if category.name == "GENERAL":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The GENERAL category cannot be deleted.")
    if category.status != "INACTIVE":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must deactivate the category before deleting it.")

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="CATEGORY_DELETED",
        entity_type="category",
        entity_id=category.id,
        old_data={"name": category.name},
    )
    run_delete_or_conflict(db, category, "Cannot delete: the category is used by one or more courses.")


def set_status(db: Session, *, current_user: User, category_id: uuid.UUID, new_status: str) -> Category:
    category = category_repository.get_by_id(db, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found.")
    old_status = category.status
    category.status = new_status
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="CATEGORY_STATUS_CHANGED",
        entity_type="category",
        entity_id=category.id,
        old_data={"status": old_status},
        new_data={"status": new_status},
    )
    db.commit()
    db.refresh(category)
    return category
