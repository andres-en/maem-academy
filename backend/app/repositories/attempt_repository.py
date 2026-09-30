import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.assessment import AssessmentAttempt, AttemptAnswer

GRADED_STATUSES = ("PASSED", "FAILED")


def get_in_progress(db: Session, *, enrollment_id: uuid.UUID, assessment_id: uuid.UUID) -> AssessmentAttempt | None:
    stmt = select(AssessmentAttempt).where(
        AssessmentAttempt.enrollment_id == enrollment_id,
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.status == "IN_PROGRESS",
    )
    return db.scalar(stmt)


def count_graded_attempts(db: Session, *, enrollment_id: uuid.UUID, assessment_id: uuid.UUID) -> int:
    stmt = (
        select(func.count())
        .select_from(AssessmentAttempt)
        .where(
            AssessmentAttempt.enrollment_id == enrollment_id,
            AssessmentAttempt.assessment_id == assessment_id,
            AssessmentAttempt.status.in_(GRADED_STATUSES),
        )
    )
    return db.scalar(stmt) or 0


def next_attempt_number(db: Session, *, enrollment_id: uuid.UUID, assessment_id: uuid.UUID) -> int:
    current_max = db.scalar(
        select(func.max(AssessmentAttempt.attempt_number)).where(
            AssessmentAttempt.enrollment_id == enrollment_id, AssessmentAttempt.assessment_id == assessment_id
        )
    )
    return (current_max if current_max is not None else 0) + 1


def create(
    db: Session, *, assessment_id: uuid.UUID, enrollment_id: uuid.UUID, attempt_number: int
) -> AssessmentAttempt:
    attempt = AssessmentAttempt(
        assessment_id=assessment_id,
        enrollment_id=enrollment_id,
        attempt_number=attempt_number,
        status="IN_PROGRESS",
        started_at=datetime.now(UTC),
    )
    db.add(attempt)
    db.flush()
    return attempt


def get_by_id(db: Session, attempt_id: uuid.UUID) -> AssessmentAttempt | None:
    stmt = (
        select(AssessmentAttempt)
        .where(AssessmentAttempt.id == attempt_id)
        .options(selectinload(AssessmentAttempt.answers))
    )
    return db.scalar(stmt)


def list_by_enrollment_assessment(
    db: Session, *, enrollment_id: uuid.UUID, assessment_id: uuid.UUID
) -> list[AssessmentAttempt]:
    stmt = (
        select(AssessmentAttempt)
        .where(AssessmentAttempt.enrollment_id == enrollment_id, AssessmentAttempt.assessment_id == assessment_id)
        .order_by(AssessmentAttempt.attempt_number)
    )
    return list(db.scalars(stmt))


def list_by_enrollment(db: Session, enrollment_id: uuid.UUID) -> list[AssessmentAttempt]:
    stmt = (
        select(AssessmentAttempt)
        .where(AssessmentAttempt.enrollment_id == enrollment_id)
        .options(selectinload(AssessmentAttempt.answers))
        .order_by(AssessmentAttempt.attempt_number)
    )
    return list(db.scalars(stmt))


def list_graded_by_assessment(db: Session, assessment_id: uuid.UUID) -> list[AssessmentAttempt]:
    stmt = (
        select(AssessmentAttempt)
        .where(AssessmentAttempt.assessment_id == assessment_id, AssessmentAttempt.status.in_(GRADED_STATUSES))
        .options(selectinload(AssessmentAttempt.answers))
    )
    return list(db.scalars(stmt))


def save_answer(
    db: Session,
    *,
    attempt_id: uuid.UUID,
    question_id: uuid.UUID,
    selected_option_id: uuid.UUID | None,
    is_correct: bool,
    points_awarded: float,
) -> AttemptAnswer:
    answer = AttemptAnswer(
        attempt_id=attempt_id,
        question_id=question_id,
        selected_option_id=selected_option_id,
        is_correct=is_correct,
        points_awarded=points_awarded,
    )
    db.add(answer)
    return answer
