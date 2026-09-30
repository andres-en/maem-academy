import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.user import User
from app.repositories import audit_repository, course_repository, lesson_repository, module_repository
from app.services.course_permissions import ensure_can_edit_course


def _load_lesson_and_course(db: Session, lesson_id: uuid.UUID):
    lesson = lesson_repository.get_by_id(db, lesson_id)
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found.")
    module = module_repository.get_by_id(db, lesson.module_id)
    if module is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Module not found.")
    course = course_repository.get_by_id(db, module.course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    return lesson, course


def create_lesson(
    db: Session,
    *,
    current_user: User,
    module_id: uuid.UUID,
    title: str,
    description: str | None,
    completion_type: str,
) -> Lesson:
    module = module_repository.get_by_id(db, module_id)
    if module is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Module not found.")
    course = course_repository.get_by_id(db, module.course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    lesson = lesson_repository.create(
        db, module_id=module_id, title=title, description=description, completion_type=completion_type
    )
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_LESSON_CREATED",
        entity_type="lesson",
        entity_id=lesson.id,
        new_data={"module_id": str(module_id), "title": title},
    )
    db.commit()
    db.refresh(lesson)
    return lesson


def update_lesson(
    db: Session,
    *,
    current_user: User,
    lesson_id: uuid.UUID,
    title: str,
    description: str | None,
    completion_type: str,
) -> Lesson:
    lesson, course = _load_lesson_and_course(db, lesson_id)
    ensure_can_edit_course(db, course, current_user)
    lesson.title = title
    lesson.description = description
    lesson.completion_type = completion_type
    db.commit()
    db.refresh(lesson)
    return lesson


def delete_lesson(db: Session, *, current_user: User, lesson_id: uuid.UUID) -> None:
    lesson, course = _load_lesson_and_course(db, lesson_id)
    ensure_can_edit_course(db, course, current_user)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_LESSON_DELETED",
        entity_type="lesson",
        entity_id=lesson.id,
        old_data={"title": lesson.title},
    )
    db.delete(lesson)
    db.commit()


def move_lesson(db: Session, *, current_user: User, lesson_id: uuid.UUID, direction: str) -> Lesson:
    lesson, course = _load_lesson_and_course(db, lesson_id)
    ensure_can_edit_course(db, course, current_user)
    sibling = lesson_repository.get_sibling(db, lesson, direction)
    if sibling is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is no neighboring lesson in that direction.")
    lesson_repository.swap_positions(db, lesson, sibling)
    db.commit()
    db.refresh(lesson)
    return lesson
