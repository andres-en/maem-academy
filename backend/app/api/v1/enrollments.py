import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES
from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.enrollment import (
    EnrollmentContentRead,
    EnrollmentCreateRequest,
    EnrollmentCreateResponse,
    EnrollmentRead,
    EnrollmentUpdateRequest,
    LessonCompleteResponse,
)
from app.services import enrollment_service, student_service

router = APIRouter(tags=["enrollments"])


@router.post("/courses/{course_id}/enrollments", response_model=EnrollmentCreateResponse, status_code=201)
def create_enrollments(
    course_id: uuid.UUID,
    payload: EnrollmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> EnrollmentCreateResponse:
    created, skipped, enrollments = enrollment_service.create_manual_enrollments(
        db,
        current_user=current_user,
        course_id=course_id,
        user_ids=payload.user_ids,
        is_required=payload.is_required,
        due_date=payload.due_date,
    )
    return EnrollmentCreateResponse(
        created=created, skipped=skipped, enrollments=[enrollment_service.to_enrollment_read(e) for e in enrollments]
    )


@router.get("/courses/{course_id}/enrollments", response_model=Page[EnrollmentRead])
def list_course_enrollments(
    course_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> Page[EnrollmentRead]:
    items, total = enrollment_service.list_course_enrollments(db, course_id=course_id, page=page, page_size=page_size)
    return Page(
        items=[enrollment_service.to_enrollment_read(e) for e in items], total=total, page=page, page_size=page_size
    )


@router.get("/enrollments/me", response_model=list[EnrollmentRead])
def my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EnrollmentRead]:
    items = enrollment_service.list_user_enrollments(db, current_user.id)
    return [enrollment_service.to_enrollment_read(e) for e in items]


@router.get("/users/{user_id}/enrollments", response_model=list[EnrollmentRead])
def user_enrollments(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> list[EnrollmentRead]:
    items = enrollment_service.list_user_enrollments(db, user_id)
    return [enrollment_service.to_enrollment_read(e) for e in items]


@router.patch("/enrollments/{enrollment_id}", response_model=EnrollmentRead)
def update_enrollment(
    enrollment_id: uuid.UUID,
    payload: EnrollmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> EnrollmentRead:
    enrollment = enrollment_service.update_due_date(
        db, current_user=current_user, enrollment_id=enrollment_id, due_date=payload.due_date
    )
    return enrollment_service.to_enrollment_read(enrollment)


@router.post("/enrollments/{enrollment_id}/cancel", response_model=EnrollmentRead)
def cancel_enrollment(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> EnrollmentRead:
    enrollment = enrollment_service.cancel_enrollment(db, current_user=current_user, enrollment_id=enrollment_id)
    return enrollment_service.to_enrollment_read(enrollment)


@router.get("/enrollments/{enrollment_id}/content", response_model=EnrollmentContentRead)
def get_enrollment_content(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnrollmentContentRead:
    return student_service.get_course_content(db, current_user=current_user, enrollment_id=enrollment_id)


@router.post("/enrollments/{enrollment_id}/lessons/{lesson_id}/complete", response_model=LessonCompleteResponse)
def complete_lesson(
    enrollment_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonCompleteResponse:
    return student_service.complete_lesson(
        db, current_user=current_user, enrollment_id=enrollment_id, lesson_id=lesson_id
    )
