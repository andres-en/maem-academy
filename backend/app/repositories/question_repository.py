import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assessment import AssessmentQuestion, QuestionOption


def next_position(db: Session, assessment_id: uuid.UUID) -> int:
    current_max = db.scalar(
        select(func.max(AssessmentQuestion.position)).where(AssessmentQuestion.assessment_id == assessment_id)
    )
    return (current_max if current_max is not None else -1) + 1


def create_with_options(
    db: Session,
    *,
    assessment_id: uuid.UUID,
    question_text: str,
    points: float,
    options: list[tuple[str, bool]],
) -> AssessmentQuestion:
    question = AssessmentQuestion(
        assessment_id=assessment_id,
        question_text=question_text,
        points=points,
        position=next_position(db, assessment_id),
    )
    db.add(question)
    db.flush()
    for index, (text, is_correct) in enumerate(options):
        db.add(QuestionOption(question_id=question.id, option_text=text, is_correct=is_correct, position=index))
    db.flush()
    return question


def get_by_id(db: Session, question_id: uuid.UUID) -> AssessmentQuestion | None:
    return db.get(AssessmentQuestion, question_id)


def replace_options(db: Session, question: AssessmentQuestion, options: list[tuple[str, bool]]) -> None:
    for option in list(question.options):
        db.delete(option)
    db.flush()
    for index, (text, is_correct) in enumerate(options):
        db.add(QuestionOption(question_id=question.id, option_text=text, is_correct=is_correct, position=index))
    db.flush()


def delete(db: Session, question: AssessmentQuestion) -> None:
    db.delete(question)
