import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.assignment import AssignmentCreate, AssignmentCreateResponse, AssignmentRead, AssignmentUpdate
from app.services import enrollment_service

router = APIRouter(tags=["enrollments"])


@router.post("/courses/{course_id}/assignments", response_model=AssignmentCreateResponse, status_code=201)
def create_assignment(
    course_id: uuid.UUID,
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> AssignmentCreateResponse:
    assignment, created, skipped = enrollment_service.create_assignment(
        db,
        current_user=current_user,
        course_id=course_id,
        user_ids=payload.user_ids,
        group_ids=payload.group_ids,
        is_required=payload.is_required,
        due_date=payload.due_date,
        overdue_action=payload.overdue_action,
    )
    return AssignmentCreateResponse(
        assignment=enrollment_service.to_assignment_read(assignment),
        enrollments_created=created,
        enrollments_skipped=skipped,
    )


@router.get("/courses/{course_id}/assignments", response_model=list[AssignmentRead])
def list_assignments(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> list[AssignmentRead]:
    assignments = enrollment_service.list_assignments(db, course_id)
    return [enrollment_service.to_assignment_read(a) for a in assignments]


@router.patch("/assignments/{assignment_id}", response_model=AssignmentRead)
def update_assignment(
    assignment_id: uuid.UUID,
    payload: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> AssignmentRead:
    assignment = enrollment_service.update_assignment(
        db,
        current_user=current_user,
        assignment_id=assignment_id,
        is_required=payload.is_required,
        due_date=payload.due_date,
        due_date_set="due_date" in payload.model_fields_set,
        overdue_action=payload.overdue_action,
        status_value=payload.status,
    )
    return enrollment_service.to_assignment_read(assignment)
