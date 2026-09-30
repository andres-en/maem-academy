import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import ADMIN_ROLES
from app.core.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import (
    AssessmentSummaryReport,
    CourseReportRow,
    EnrollmentAttemptsReport,
    ReportSummary,
    UserReportRow,
)
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary)
def get_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> ReportSummary:
    return report_service.get_summary(db)


@router.get("/courses/{course_id}", response_model=list[CourseReportRow])
def get_course_report(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> list[CourseReportRow]:
    return report_service.get_course_report(db, course_id)


@router.get("/courses/{course_id}/assessment-summary", response_model=list[AssessmentSummaryReport])
def get_course_assessment_summary(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> list[AssessmentSummaryReport]:
    return report_service.get_course_assessment_summary(db, course_id)


@router.get("/enrollments/{enrollment_id}/attempts", response_model=EnrollmentAttemptsReport)
def get_enrollment_attempts(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> EnrollmentAttemptsReport:
    return report_service.get_enrollment_attempts(db, enrollment_id)


@router.get("/users/{user_id}", response_model=list[UserReportRow])
def get_user_report(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(ADMIN_ROLES)),
) -> list[UserReportRow]:
    return report_service.get_user_report(db, user_id)
