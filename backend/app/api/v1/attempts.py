import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.attempt import AttemptResultRead, AttemptSummaryRead, StartAttemptResponse, SubmitAttemptRequest
from app.services import attempt_service

router = APIRouter(tags=["assessments"])


@router.post("/enrollments/{enrollment_id}/assessments/{assessment_id}/start", response_model=StartAttemptResponse)
def start_attempt(
    enrollment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StartAttemptResponse:
    return attempt_service.start_attempt(
        db, current_user=current_user, enrollment_id=enrollment_id, assessment_id=assessment_id
    )


@router.post("/enrollments/{enrollment_id}/attempts/{attempt_id}/submit", response_model=AttemptResultRead)
def submit_attempt(
    enrollment_id: uuid.UUID,
    attempt_id: uuid.UUID,
    payload: SubmitAttemptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttemptResultRead:
    return attempt_service.submit_attempt(
        db,
        current_user=current_user,
        enrollment_id=enrollment_id,
        attempt_id=attempt_id,
        answers=payload.answers,
    )


@router.get(
    "/enrollments/{enrollment_id}/assessments/{assessment_id}/attempts", response_model=list[AttemptSummaryRead]
)
def list_attempts(
    enrollment_id: uuid.UUID,
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AttemptSummaryRead]:
    return attempt_service.list_attempts(
        db, current_user=current_user, enrollment_id=enrollment_id, assessment_id=assessment_id
    )
