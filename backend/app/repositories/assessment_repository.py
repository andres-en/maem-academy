import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.assessment import Assessment, AssessmentQuestion


def _detail_options():
    return (selectinload(Assessment.questions).selectinload(AssessmentQuestion.options),)


def create(
    db: Session,
    *,
    course_id: uuid.UUID,
    module_id: uuid.UUID | None,
    title: str,
    description: str | None,
    minimum_score: float,
    max_attempts: int | None,
    is_required: bool,
) -> Assessment:
    assessment = Assessment(
        course_id=course_id,
        module_id=module_id,
        title=title,
        description=description,
        minimum_score=minimum_score,
        max_attempts=max_attempts,
        is_required=is_required,
        position=0,
    )
    db.add(assessment)
    return assessment


def get_by_id(db: Session, assessment_id: uuid.UUID) -> Assessment | None:
    return db.get(Assessment, assessment_id)


def get_detail(db: Session, assessment_id: uuid.UUID) -> Assessment | None:
    stmt = select(Assessment).where(Assessment.id == assessment_id).options(*_detail_options())
    return db.scalar(stmt)


def list_by_course(db: Session, course_id: uuid.UUID) -> list[Assessment]:
    stmt = select(Assessment).where(Assessment.course_id == course_id).options(*_detail_options())
    return list(db.scalars(stmt).unique())


def delete(db: Session, assessment: Assessment) -> None:
    db.delete(assessment)


def get_final_assessment(db: Session, course_id: uuid.UUID) -> Assessment | None:
    stmt = select(Assessment).where(Assessment.course_id == course_id, Assessment.module_id.is_(None))
    return db.scalar(stmt)
