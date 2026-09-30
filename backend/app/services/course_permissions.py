from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES
from app.models.course import Course
from app.models.user import User
from app.repositories import course_repository

EDITABLE_STATUSES = ("DRAFT", "CHANGES_REQUESTED")


def ensure_can_edit_course(db: Session, course: Course, current_user: User) -> None:
    if current_user.role.name in ADMIN_ROLES:
        return
    is_editor = course_repository.is_owner_or_collaborator(db, course_id=course.id, user_id=current_user.id)
    if not is_editor:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to edit this course.")
    if course.status not in EDITABLE_STATUSES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "The course cannot be edited while it is in review, approved, published or archived.",
        )


def ensure_is_owner_or_admin(current_user: User, course: Course) -> None:
    if current_user.role.name in ADMIN_ROLES:
        return
    if course.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the course owner can perform this action.")
