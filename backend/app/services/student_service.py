import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories import (
    assessment_repository,
    attempt_repository,
    audit_repository,
    enrollment_repository,
    lesson_progress_repository,
)
from app.schemas.attempt import AssessmentStudentSummary
from app.schemas.enrollment import EnrollmentContentRead, EnrollmentSummary, LessonCompleteResponse, LessonProgressRead
from app.services import course_service

BLOCKED_STATUSES = ("CANCELLED", "BLOCKED")


def _overdue_action_for(enrollment: Enrollment) -> str:
    if enrollment.assignment is not None:
        return enrollment.assignment.overdue_action
    return "ALLOW_CONTINUE"


def ensure_access(enrollment: Enrollment) -> None:
    if enrollment.status in BLOCKED_STATUSES:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This enrollment is no longer active.")
    if enrollment.status == "OVERDUE" and _overdue_action_for(enrollment) == "BLOCK":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This enrollment is past its due date and the course is blocked."
        )


def get_enrollment_for_user(db: Session, *, current_user: User, enrollment_id: uuid.UUID) -> Enrollment:
    enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if enrollment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enrollment not found.")
    if enrollment.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This enrollment does not belong to you.")
    enrollment_repository.apply_overdue(db, enrollment)
    return enrollment


def _calculate_progress(total_lessons: int, completed_lessons: int) -> float:
    if total_lessons == 0:
        return 0.0
    return round((completed_lessons / total_lessons) * 100, 2)


def _to_summary(db: Session, enrollment: Enrollment, progress_percentage: float) -> EnrollmentSummary:
    return EnrollmentSummary(
        id=enrollment.id,
        status=enrollment.status,
        progress_percentage=progress_percentage,
        is_required=enrollment.is_required,
        due_date=enrollment.due_date,
        overdue_action=_overdue_action_for(enrollment),
        started_at=enrollment.started_at,
        completed_at=enrollment.completed_at,
    )


def _all_lessons(course) -> list:
    lessons = []
    for module in course.modules:
        lessons.extend(module.lessons)
    return lessons


def _assessment_summary(db: Session, *, enrollment: Enrollment, assessment) -> AssessmentStudentSummary:
    attempts = attempt_repository.list_by_enrollment_assessment(
        db, enrollment_id=enrollment.id, assessment_id=assessment.id
    )
    graded = [a for a in attempts if a.status in ("PASSED", "FAILED")]
    best_score = max((float(a.score) for a in graded if a.score is not None), default=None)
    if any(a.status == "PASSED" for a in attempts):
        student_status = "passed"
    elif any(a.status == "IN_PROGRESS" for a in attempts):
        student_status = "in_progress"
    elif graded:
        student_status = "failed"
    else:
        student_status = "not_started"
    return AssessmentStudentSummary(
        id=assessment.id,
        title=assessment.title,
        module_id=assessment.module_id,
        minimum_score=float(assessment.minimum_score),
        max_attempts=assessment.max_attempts,
        is_required=assessment.is_required,
        attempts_used=len(graded),
        best_score=best_score,
        status=student_status,
    )


def _has_passed(db: Session, *, enrollment_id: uuid.UUID, assessment_id: uuid.UUID) -> bool:
    attempts = attempt_repository.list_by_enrollment_assessment(
        db, enrollment_id=enrollment_id, assessment_id=assessment_id
    )
    return any(a.status == "PASSED" for a in attempts)


def recalculate_completion(db: Session, enrollment: Enrollment) -> None:
    """Sección 35: el curso se considera terminado cuando se completan todas las
    lecciones y se aprueban todas las evaluaciones obligatorias. Sin evaluaciones
    obligatorias de por medio, el estado terminal es COMPLETED; con ellas, PASSED."""
    if enrollment.status in ("CANCELLED", "BLOCKED", "FAILED", "COMPLETED", "PASSED"):
        return

    course = course_service.get_course_detail(db, enrollment.course_id)
    lessons = _all_lessons(course)
    progress_rows = lesson_progress_repository.list_by_enrollment(db, enrollment.id)
    completed_lesson_ids = {p.lesson_id for p in progress_rows if p.status == "COMPLETED"}
    lessons_done = all(lesson.id in completed_lesson_ids for lesson in lessons)

    assessments = assessment_repository.list_by_course(db, enrollment.course_id)
    required_assessments = [a for a in assessments if a.is_required]
    assessments_done = all(
        _has_passed(db, enrollment_id=enrollment.id, assessment_id=a.id) for a in required_assessments
    )

    if lessons_done and assessments_done:
        enrollment.status = "PASSED" if required_assessments else "COMPLETED"
        enrollment.completed_at = enrollment.completed_at or datetime.now(UTC)
        db.flush()


def get_course_content(db: Session, *, current_user: User, enrollment_id: uuid.UUID) -> EnrollmentContentRead:
    enrollment = get_enrollment_for_user(db, current_user=current_user, enrollment_id=enrollment_id)
    ensure_access(enrollment)

    if enrollment.status == "ASSIGNED":
        enrollment.status = "IN_PROGRESS"
        enrollment.started_at = enrollment.started_at or datetime.now(UTC)
        db.commit()

    course = course_service.get_course_detail(db, enrollment.course_id)
    progress_rows = lesson_progress_repository.list_by_enrollment(db, enrollment.id)
    progress_by_lesson = {p.lesson_id: p for p in progress_rows}

    lessons = _all_lessons(course)
    completed = sum(
        1
        for lesson in lessons
        if progress_by_lesson.get(lesson.id) and progress_by_lesson[lesson.id].status == "COMPLETED"
    )
    progress_percentage = _calculate_progress(len(lessons), completed)

    assessments = assessment_repository.list_by_course(db, enrollment.course_id)

    return EnrollmentContentRead(
        enrollment=_to_summary(db, enrollment, progress_percentage),
        course=course_service.to_course_detail(course),
        lesson_progress=[
            LessonProgressRead(
                lesson_id=p.lesson_id,
                status=p.status,
                progress_percentage=float(p.progress_percentage),
                completed_at=p.completed_at,
            )
            for p in progress_rows
        ],
        assessments=[_assessment_summary(db, enrollment=enrollment, assessment=a) for a in assessments],
    )


def complete_lesson(
    db: Session, *, current_user: User, enrollment_id: uuid.UUID, lesson_id: uuid.UUID
) -> LessonCompleteResponse:
    enrollment = get_enrollment_for_user(db, current_user=current_user, enrollment_id=enrollment_id)
    ensure_access(enrollment)

    course = course_service.get_course_detail(db, enrollment.course_id)
    lessons = _all_lessons(course)
    if lesson_id not in {lesson.id for lesson in lessons}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That lesson does not belong to this enrollment's course.")

    if enrollment.status == "ASSIGNED":
        enrollment.status = "IN_PROGRESS"
        enrollment.started_at = enrollment.started_at or datetime.now(UTC)

    progress = lesson_progress_repository.upsert_completed(db, enrollment_id=enrollment.id, lesson_id=lesson_id)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="LESSON_COMPLETED",
        entity_type="lesson_progress",
        entity_id=progress.id,
        new_data={"enrollment_id": str(enrollment.id), "lesson_id": str(lesson_id)},
    )

    progress_rows = lesson_progress_repository.list_by_enrollment(db, enrollment.id)
    progress_by_lesson = {p.lesson_id: p for p in progress_rows}
    completed = sum(
        1
        for lesson in lessons
        if progress_by_lesson.get(lesson.id) and progress_by_lesson[lesson.id].status == "COMPLETED"
    )
    progress_percentage = _calculate_progress(len(lessons), completed)

    status_before = enrollment.status
    recalculate_completion(db, enrollment)
    if enrollment.status != status_before and enrollment.status in ("COMPLETED", "PASSED"):
        audit_repository.log_action(
            db,
            user_id=current_user.id,
            action="ENROLLMENT_COMPLETED",
            entity_type="enrollment",
            entity_id=enrollment.id,
            new_data={"status": enrollment.status},
        )

    db.commit()
    db.refresh(progress)
    db.refresh(enrollment)

    return LessonCompleteResponse(
        lesson_progress=LessonProgressRead(
            lesson_id=progress.lesson_id,
            status=progress.status,
            progress_percentage=float(progress.progress_percentage),
            completed_at=progress.completed_at,
        ),
        enrollment=_to_summary(db, enrollment, progress_percentage),
    )
