import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.assessment import Assessment, AssessmentQuestion
from app.models.user import User
from app.repositories import assessment_repository, audit_repository, course_repository, question_repository
from app.schemas.assessment import QuestionOptionCreate
from app.services.course_permissions import ensure_can_edit_course


def _load_course_for_assessment(db: Session, assessment_id: uuid.UUID):
    assessment = assessment_repository.get_by_id(db, assessment_id)
    if assessment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assessment not found.")
    course = course_repository.get_by_id(db, assessment.course_id)
    return assessment, course


def _validate_options(options: list[QuestionOptionCreate]) -> None:
    correct_count = sum(1 for o in options if o.is_correct)
    if correct_count != 1:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Each question must have exactly one option marked as correct."
        )


def list_assessments(db: Session, course_id: uuid.UUID) -> list[Assessment]:
    return assessment_repository.list_by_course(db, course_id)


def create_assessment(
    db: Session,
    *,
    current_user: User,
    course_id: uuid.UUID,
    module_id: uuid.UUID | None,
    title: str,
    description: str | None,
    minimum_score: float,
    max_attempts: int | None,
    is_required: bool,
) -> Assessment:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    if module_id is not None:
        from app.repositories import module_repository

        module = module_repository.get_by_id(db, module_id)
        if module is None or module.course_id != course_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid module for this course.")

    assessment = assessment_repository.create(
        db,
        course_id=course_id,
        module_id=module_id,
        title=title,
        description=description,
        minimum_score=minimum_score,
        max_attempts=max_attempts,
        is_required=is_required,
    )
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="ASSESSMENT_CREATED",
        entity_type="assessment",
        entity_id=assessment.id,
        new_data={"course_id": str(course_id), "module_id": str(module_id) if module_id else None, "title": title},
    )
    db.commit()
    return assessment_repository.get_detail(db, assessment.id)


def update_assessment(
    db: Session,
    *,
    current_user: User,
    assessment_id: uuid.UUID,
    title: str,
    description: str | None,
    minimum_score: float,
    max_attempts: int | None,
    is_required: bool,
) -> Assessment:
    assessment, course = _load_course_for_assessment(db, assessment_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    assessment.title = title
    assessment.description = description
    assessment.minimum_score = minimum_score
    assessment.max_attempts = max_attempts
    assessment.is_required = is_required
    db.commit()
    return assessment_repository.get_detail(db, assessment_id)


def delete_assessment(db: Session, *, current_user: User, assessment_id: uuid.UUID) -> None:
    assessment, course = _load_course_for_assessment(db, assessment_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    audit_repository.log_action(
        db, user_id=current_user.id, action="ASSESSMENT_DELETED", entity_type="assessment", entity_id=assessment.id
    )
    assessment_repository.delete(db, assessment)
    db.commit()


def create_question(
    db: Session,
    *,
    current_user: User,
    assessment_id: uuid.UUID,
    question_text: str,
    points: float,
    options: list[QuestionOptionCreate],
) -> AssessmentQuestion:
    assessment, course = _load_course_for_assessment(db, assessment_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)
    _validate_options(options)

    question = question_repository.create_with_options(
        db,
        assessment_id=assessment_id,
        question_text=question_text,
        points=points,
        options=[(o.text, o.is_correct) for o in options],
    )
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="ASSESSMENT_QUESTION_CREATED",
        entity_type="assessment_question",
        entity_id=question.id,
        new_data={"assessment_id": str(assessment_id)},
    )
    db.commit()
    return question_repository.get_by_id(db, question.id)


def update_question(
    db: Session,
    *,
    current_user: User,
    question_id: uuid.UUID,
    question_text: str,
    points: float,
    options: list[QuestionOptionCreate],
) -> AssessmentQuestion:
    question = question_repository.get_by_id(db, question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")
    assessment, course = _load_course_for_assessment(db, question.assessment_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)
    _validate_options(options)

    question.question_text = question_text
    question.points = points
    question_repository.replace_options(db, question, [(o.text, o.is_correct) for o in options])
    db.commit()
    return question_repository.get_by_id(db, question_id)


def delete_question(db: Session, *, current_user: User, question_id: uuid.UUID) -> None:
    question = question_repository.get_by_id(db, question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")
    assessment, course = _load_course_for_assessment(db, question.assessment_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    question_repository.delete(db, question)
    db.commit()
