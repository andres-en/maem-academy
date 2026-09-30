import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES, INSTRUCTOR
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.assessment import AssessmentCreate, AssessmentRead, AssessmentUpdate, QuestionCreate, QuestionRead
from app.services import assessment_service

router = APIRouter(tags=["assessments"])

COURSE_ROLES = (*ADMIN_ROLES, INSTRUCTOR)


def _to_question_read(question) -> QuestionRead:
    return QuestionRead(
        id=question.id,
        question_text=question.question_text,
        points=float(question.points),
        position=question.position,
        options=[
            {"id": o.id, "text": o.option_text, "is_correct": o.is_correct, "position": o.position}
            for o in question.options
        ],
    )


def _to_assessment_read(assessment) -> AssessmentRead:
    return AssessmentRead(
        id=assessment.id,
        course_id=assessment.course_id,
        module_id=assessment.module_id,
        title=assessment.title,
        description=assessment.description,
        minimum_score=float(assessment.minimum_score),
        max_attempts=assessment.max_attempts,
        is_required=assessment.is_required,
        questions=[_to_question_read(q) for q in assessment.questions],
    )


@router.post("/courses/{course_id}/assessments", response_model=AssessmentRead, status_code=201)
def create_assessment(
    course_id: uuid.UUID,
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> AssessmentRead:
    assessment = assessment_service.create_assessment(
        db,
        current_user=current_user,
        course_id=course_id,
        module_id=payload.module_id,
        title=payload.title,
        description=payload.description,
        minimum_score=payload.minimum_score,
        max_attempts=payload.max_attempts,
        is_required=payload.is_required,
    )
    return _to_assessment_read(assessment)


@router.get("/courses/{course_id}/assessments", response_model=list[AssessmentRead])
def list_assessments(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> list[AssessmentRead]:
    assessments = assessment_service.list_assessments(db, course_id)
    return [_to_assessment_read(a) for a in assessments]


@router.put("/assessments/{assessment_id}", response_model=AssessmentRead)
def update_assessment(
    assessment_id: uuid.UUID,
    payload: AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> AssessmentRead:
    assessment = assessment_service.update_assessment(
        db,
        current_user=current_user,
        assessment_id=assessment_id,
        title=payload.title,
        description=payload.description,
        minimum_score=payload.minimum_score,
        max_attempts=payload.max_attempts,
        is_required=payload.is_required,
    )
    return _to_assessment_read(assessment)


@router.delete("/assessments/{assessment_id}", status_code=204)
def delete_assessment(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> None:
    assessment_service.delete_assessment(db, current_user=current_user, assessment_id=assessment_id)


@router.post("/assessments/{assessment_id}/questions", response_model=QuestionRead, status_code=201)
def create_question(
    assessment_id: uuid.UUID,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> QuestionRead:
    question = assessment_service.create_question(
        db,
        current_user=current_user,
        assessment_id=assessment_id,
        question_text=payload.question_text,
        points=payload.points,
        options=payload.options,
    )
    return _to_question_read(question)


@router.put("/questions/{question_id}", response_model=QuestionRead)
def update_question(
    question_id: uuid.UUID,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> QuestionRead:
    question = assessment_service.update_question(
        db,
        current_user=current_user,
        question_id=question_id,
        question_text=payload.question_text,
        points=payload.points,
        options=payload.options,
    )
    return _to_question_read(question)


@router.delete("/questions/{question_id}", status_code=204)
def delete_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(COURSE_ROLES)),
) -> None:
    assessment_service.delete_question(db, current_user=current_user, question_id=question_id)
