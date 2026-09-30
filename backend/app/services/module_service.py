import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.module import CourseModule
from app.models.user import User
from app.repositories import audit_repository, course_repository, module_repository
from app.services.course_permissions import ensure_can_edit_course


def _load_module_and_course(db: Session, module_id: uuid.UUID) -> tuple[CourseModule, "Course"]:  # noqa: F821
    module = module_repository.get_by_id(db, module_id)
    if module is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Module not found.")
    course = course_repository.get_by_id(db, module.course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    return module, course


def create_module(
    db: Session, *, current_user: User, course_id: uuid.UUID, title: str, description: str | None
) -> CourseModule:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    module = module_repository.create(db, course_id=course_id, title=title, description=description)
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_MODULE_CREATED",
        entity_type="course_module",
        entity_id=module.id,
        new_data={"course_id": str(course_id), "title": title},
    )
    db.commit()
    db.refresh(module)
    return module


def update_module(
    db: Session, *, current_user: User, module_id: uuid.UUID, title: str, description: str | None
) -> CourseModule:
    module, course = _load_module_and_course(db, module_id)
    ensure_can_edit_course(db, course, current_user)
    module.title = title
    module.description = description
    db.commit()
    db.refresh(module)
    return module


def delete_module(db: Session, *, current_user: User, module_id: uuid.UUID) -> None:
    module, course = _load_module_and_course(db, module_id)
    ensure_can_edit_course(db, course, current_user)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_MODULE_DELETED",
        entity_type="course_module",
        entity_id=module.id,
        old_data={"title": module.title},
    )
    db.delete(module)
    db.commit()


def move_module(db: Session, *, current_user: User, module_id: uuid.UUID, direction: str) -> CourseModule:
    module, course = _load_module_and_course(db, module_id)
    ensure_can_edit_course(db, course, current_user)
    sibling = module_repository.get_sibling(db, module, direction)
    if sibling is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is no neighboring module in that direction.")
    module_repository.swap_positions(db, module, sibling)
    db.commit()
    db.refresh(module)
    return module
