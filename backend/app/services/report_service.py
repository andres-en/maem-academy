import uuid
from collections import Counter, defaultdict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import storage
from app.models.assessment import Assessment
from app.models.enrollment import Enrollment
from app.repositories import (
    assessment_repository,
    attempt_repository,
    course_repository,
    enrollment_repository,
    lesson_progress_repository,
    lesson_repository,
    user_repository,
)
from app.schemas.common import CourseBrief, UserBrief
from app.schemas.report import (
    AssessmentAttemptsDetail,
    AssessmentSummaryReport,
    AttemptAnswerDetail,
    AttemptDetail,
    CourseReportRow,
    EnrollmentAttemptsReport,
    OptionStat,
    QuestionStat,
    ReportSummary,
    UserReportRow,
)


def get_summary(db: Session) -> ReportSummary:
    enrollment_repository.apply_overdue_bulk(db)

    _, active_users = user_repository.list_users(db, page=1, page_size=1, status="ACTIVE")
    _, published_courses = course_repository.list_courses(db, page=1, page_size=1, status="PUBLISHED")
    _, courses_in_review = course_repository.list_courses(db, page=1, page_size=1, status="IN_REVIEW")

    counts = enrollment_repository.count_by_status(db)

    return ReportSummary(
        active_users=active_users,
        published_courses=published_courses,
        courses_in_review=courses_in_review,
        enrollments_total=sum(counts.values()),
        pending=counts.get("ASSIGNED", 0),
        in_progress=counts.get("IN_PROGRESS", 0),
        completed=counts.get("COMPLETED", 0),
        passed=counts.get("PASSED", 0),
        failed=counts.get("FAILED", 0),
        overdue=counts.get("OVERDUE", 0) + counts.get("BLOCKED", 0),
        cancelled=counts.get("CANCELLED", 0),
    )


def _progress_and_score(db: Session, enrollment: Enrollment) -> tuple[float, float | None]:
    total_lessons = lesson_repository.count_by_course(db, enrollment.course_id)
    if total_lessons > 0:
        progress_rows = lesson_progress_repository.list_by_enrollment(db, enrollment.id)
        completed = sum(1 for p in progress_rows if p.status == "COMPLETED")
        progress_percentage = round((completed / total_lessons) * 100, 2)
    else:
        progress_percentage = 0.0

    score = None
    final_assessment = assessment_repository.get_final_assessment(db, enrollment.course_id)
    if final_assessment is not None:
        attempts = attempt_repository.list_by_enrollment_assessment(
            db, enrollment_id=enrollment.id, assessment_id=final_assessment.id
        )
        graded_scores = [float(a.score) for a in attempts if a.score is not None]
        if graded_scores:
            score = max(graded_scores)

    return progress_percentage, score


def get_course_report(db: Session, course_id: uuid.UUID) -> list[CourseReportRow]:
    enrollment_repository.apply_overdue_bulk(db)
    enrollments = enrollment_repository.list_all_by_course(db, course_id)
    rows = []
    for enrollment in enrollments:
        progress_percentage, score = _progress_and_score(db, enrollment)
        rows.append(
            CourseReportRow(
                enrollment_id=enrollment.id,
                user=UserBrief(id=enrollment.user.id, full_name=enrollment.user.full_name, email=enrollment.user.email),
                status=enrollment.status,
                progress_percentage=progress_percentage,
                score=score,
                is_required=enrollment.is_required,
                assigned_at=enrollment.assigned_at,
                due_date=enrollment.due_date,
                completed_at=enrollment.completed_at,
            )
        )
    return rows


def get_user_report(db: Session, user_id: uuid.UUID) -> list[UserReportRow]:
    enrollment_repository.apply_overdue_bulk(db)
    enrollments = enrollment_repository.list_by_user(db, user_id)
    rows = []
    for enrollment in enrollments:
        progress_percentage, score = _progress_and_score(db, enrollment)
        rows.append(
            UserReportRow(
                enrollment_id=enrollment.id,
                course=CourseBrief(
                    id=enrollment.course.id,
                    title=enrollment.course.title,
                    cover_image_url=storage.build_public_url(enrollment.course.cover_image_url),
                    status=enrollment.course.status,
                ),
                status=enrollment.status,
                progress_percentage=progress_percentage,
                score=score,
                is_required=enrollment.is_required,
                assigned_at=enrollment.assigned_at,
                due_date=enrollment.due_date,
                completed_at=enrollment.completed_at,
            )
        )
    return rows


def _pct(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _module_title(assessment: Assessment) -> str | None:
    return assessment.module.title if assessment.module is not None else None


def _assessment_sort_key(assessment: Assessment) -> tuple[bool, str, str]:
    return (assessment.module_id is None, _module_title(assessment) or "", assessment.title)


def get_enrollment_attempts(db: Session, enrollment_id: uuid.UUID) -> EnrollmentAttemptsReport:
    enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if enrollment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enrollment not found.")

    assessments = {a.id: a for a in assessment_repository.list_by_course(db, enrollment.course_id)}
    attempts_by_assessment = defaultdict(list)
    for attempt in attempt_repository.list_by_enrollment(db, enrollment.id):
        attempts_by_assessment[attempt.assessment_id].append(attempt)

    details = []
    attempted = [assessments[i] for i in attempts_by_assessment if i in assessments]
    for assessment in sorted(attempted, key=_assessment_sort_key):
        questions = {q.id: q for q in assessment.questions}
        attempt_details = []
        for attempt in attempts_by_assessment[assessment.id]:
            answer_details = []
            ordered_answers = sorted(
                (a for a in attempt.answers if a.question_id in questions),
                key=lambda a: questions[a.question_id].position,
            )
            for answer in ordered_answers:
                question = questions[answer.question_id]
                selected = next((o for o in question.options if o.id == answer.selected_option_id), None)
                correct = next((o for o in question.options if o.is_correct), None)
                answer_details.append(
                    AttemptAnswerDetail(
                        question_id=question.id,
                        question_text=question.question_text,
                        points=float(question.points),
                        selected_option_text=selected.option_text if selected else None,
                        correct_option_text=correct.option_text if correct else None,
                        is_correct=answer.is_correct,
                        points_awarded=float(answer.points_awarded),
                    )
                )
            attempt_details.append(
                AttemptDetail(
                    id=attempt.id,
                    attempt_number=attempt.attempt_number,
                    score=float(attempt.score) if attempt.score is not None else None,
                    status=attempt.status,
                    started_at=attempt.started_at,
                    submitted_at=attempt.submitted_at,
                    answers=answer_details,
                )
            )
        details.append(
            AssessmentAttemptsDetail(
                assessment_id=assessment.id,
                title=assessment.title,
                module_title=_module_title(assessment),
                minimum_score=float(assessment.minimum_score),
                attempts=attempt_details,
            )
        )

    return EnrollmentAttemptsReport(
        user=UserBrief(id=enrollment.user.id, full_name=enrollment.user.full_name, email=enrollment.user.email),
        course=CourseBrief(
            id=enrollment.course.id,
            title=enrollment.course.title,
            cover_image_url=storage.build_public_url(enrollment.course.cover_image_url),
            status=enrollment.course.status,
        ),
        assessments=details,
    )


def get_course_assessment_summary(db: Session, course_id: uuid.UUID) -> list[AssessmentSummaryReport]:
    reports = []
    for assessment in sorted(assessment_repository.list_by_course(db, course_id), key=_assessment_sort_key):
        attempts = attempt_repository.list_graded_by_assessment(db, assessment.id)
        answers_by_question = defaultdict(list)
        for attempt in attempts:
            for answer in attempt.answers:
                answers_by_question[answer.question_id].append(answer)

        question_stats = []
        for question in assessment.questions:
            answers = answers_by_question.get(question.id, [])
            total = len(answers)
            counts = Counter(a.selected_option_id for a in answers if a.selected_option_id is not None)
            correct_count = sum(1 for a in answers if a.is_correct)
            unanswered_count = sum(1 for a in answers if a.selected_option_id is None)
            question_stats.append(
                QuestionStat(
                    question_id=question.id,
                    question_text=question.question_text,
                    points=float(question.points),
                    total_answers=total,
                    correct_count=correct_count,
                    correct_percentage=_pct(correct_count, total),
                    unanswered_count=unanswered_count,
                    unanswered_percentage=_pct(unanswered_count, total),
                    options=[
                        OptionStat(
                            option_id=o.id,
                            text=o.option_text,
                            is_correct=o.is_correct,
                            count=counts.get(o.id, 0),
                            percentage=_pct(counts.get(o.id, 0), total),
                        )
                        for o in question.options
                    ],
                )
            )

        scores = [float(a.score) for a in attempts if a.score is not None]
        passed = sum(1 for a in attempts if a.status == "PASSED")
        reports.append(
            AssessmentSummaryReport(
                assessment_id=assessment.id,
                title=assessment.title,
                module_title=_module_title(assessment),
                minimum_score=float(assessment.minimum_score),
                graded_attempts=len(attempts),
                students=len({a.enrollment_id for a in attempts}),
                average_score=round(sum(scores) / len(scores), 2) if scores else None,
                pass_rate=_pct(passed, len(attempts)) if attempts else None,
                questions=question_stats,
            )
        )
    return reports
