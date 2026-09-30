import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import assessment_repository, attempt_repository, audit_repository
from app.schemas.attempt import (
    AnswerSubmit,
    AttemptAnswerResult,
    AttemptOptionRead,
    AttemptQuestionRead,
    AttemptResultRead,
    AttemptSummaryRead,
    StartAttemptResponse,
)
from app.services import student_service


def _load_assessment_for_enrollment(db, enrollment, assessment_id: uuid.UUID):
    assessment = assessment_repository.get_detail(db, assessment_id)
    if assessment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assessment not found.")
    if assessment.course_id != enrollment.course_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That assessment does not belong to this enrollment's course.")
    return assessment


def start_attempt(
    db: Session, *, current_user: User, enrollment_id: uuid.UUID, assessment_id: uuid.UUID
) -> StartAttemptResponse:
    enrollment = student_service.get_enrollment_for_user(db, current_user=current_user, enrollment_id=enrollment_id)
    student_service.ensure_access(enrollment)
    assessment = _load_assessment_for_enrollment(db, enrollment, assessment_id)

    existing = attempt_repository.get_in_progress(db, enrollment_id=enrollment.id, assessment_id=assessment.id)
    if existing is None:
        graded_count = attempt_repository.count_graded_attempts(
            db, enrollment_id=enrollment.id, assessment_id=assessment.id
        )
        if assessment.max_attempts is not None and graded_count >= assessment.max_attempts:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "You have reached the maximum number of attempts for this assessment."
            )
        attempt_number = attempt_repository.next_attempt_number(
            db, enrollment_id=enrollment.id, assessment_id=assessment.id
        )
        existing = attempt_repository.create(
            db, assessment_id=assessment.id, enrollment_id=enrollment.id, attempt_number=attempt_number
        )
        db.commit()

    questions = [
        AttemptQuestionRead(
            id=q.id,
            question_text=q.question_text,
            points=float(q.points),
            options=[AttemptOptionRead(id=o.id, text=o.option_text) for o in q.options],
        )
        for q in assessment.questions
    ]
    return StartAttemptResponse(
        attempt_id=existing.id, attempt_number=existing.attempt_number, status=existing.status, questions=questions
    )


def submit_attempt(
    db: Session,
    *,
    current_user: User,
    enrollment_id: uuid.UUID,
    attempt_id: uuid.UUID,
    answers: list[AnswerSubmit],
) -> AttemptResultRead:
    enrollment = student_service.get_enrollment_for_user(db, current_user=current_user, enrollment_id=enrollment_id)
    student_service.ensure_access(enrollment)

    attempt = attempt_repository.get_by_id(db, attempt_id)
    if attempt is None or attempt.enrollment_id != enrollment.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Attempt not found.")
    if attempt.status != "IN_PROGRESS":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This attempt was already submitted.")

    assessment = assessment_repository.get_detail(db, attempt.assessment_id)
    answers_by_question = {a.question_id: a.selected_option_id for a in answers}

    total_points = 0.0
    earned_points = 0.0
    results: list[AttemptAnswerResult] = []
    for question in assessment.questions:
        total_points += float(question.points)
        correct_option = next((o for o in question.options if o.is_correct), None)
        selected_option_id = answers_by_question.get(question.id)
        selected_option = next((o for o in question.options if o.id == selected_option_id), None)
        is_correct = selected_option is not None and selected_option.is_correct
        points_awarded = float(question.points) if is_correct else 0.0
        earned_points += points_awarded

        attempt_repository.save_answer(
            db,
            attempt_id=attempt.id,
            question_id=question.id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            points_awarded=points_awarded,
        )
        results.append(
            AttemptAnswerResult(
                question_id=question.id,
                question_text=question.question_text,
                selected_option_id=selected_option_id,
                correct_option_id=correct_option.id if correct_option else None,
                is_correct=is_correct,
                points_awarded=points_awarded,
            )
        )

    score = round((earned_points / total_points) * 100, 2) if total_points > 0 else 0.0
    passed = score >= float(assessment.minimum_score)

    attempt.score = score
    attempt.status = "PASSED" if passed else "FAILED"
    attempt.submitted_at = datetime.now(UTC)
    db.flush()

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="ASSESSMENT_ATTEMPT_SUBMITTED",
        entity_type="assessment_attempt",
        entity_id=attempt.id,
        new_data={"score": score, "status": attempt.status},
    )

    if not passed and assessment.is_required and assessment.max_attempts is not None:
        graded_count = attempt_repository.count_graded_attempts(
            db, enrollment_id=enrollment.id, assessment_id=assessment.id
        )
        if graded_count >= assessment.max_attempts:
            enrollment.status = "FAILED"
            audit_repository.log_action(
                db,
                user_id=current_user.id,
                action="ENROLLMENT_FAILED",
                entity_type="enrollment",
                entity_id=enrollment.id,
                new_data={"reason": "max_attempts_exhausted", "assessment_id": str(assessment.id)},
            )

    student_service.recalculate_completion(db, enrollment)
    db.commit()

    return AttemptResultRead(
        attempt_id=attempt.id,
        attempt_number=attempt.attempt_number,
        score=score,
        status=attempt.status,
        submitted_at=attempt.submitted_at,
        answers=results,
    )


def list_attempts(
    db: Session, *, current_user: User, enrollment_id: uuid.UUID, assessment_id: uuid.UUID
) -> list[AttemptSummaryRead]:
    enrollment = student_service.get_enrollment_for_user(db, current_user=current_user, enrollment_id=enrollment_id)
    attempts = attempt_repository.list_by_enrollment_assessment(
        db, enrollment_id=enrollment.id, assessment_id=assessment_id
    )
    return [
        AttemptSummaryRead(
            id=a.id,
            attempt_number=a.attempt_number,
            score=float(a.score) if a.score is not None else None,
            status=a.status,
            started_at=a.started_at,
            submitted_at=a.submitted_at,
        )
        for a in attempts
    ]
