import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.attempt import AssessmentStudentSummary
from app.schemas.common import CourseBrief, UserBrief
from app.schemas.course import CourseDetailRead


class EnrollmentCreateRequest(BaseModel):
    user_ids: list[uuid.UUID] = Field(min_length=1)
    is_required: bool = False
    due_date: datetime | None = None


class EnrollmentUpdateRequest(BaseModel):
    due_date: datetime | None = None


class EnrollmentRead(BaseModel):
    id: uuid.UUID
    user: UserBrief
    course: CourseBrief
    assignment_id: uuid.UUID | None
    enrollment_type: str
    status: str
    is_required: bool
    assigned_at: datetime
    started_at: datetime | None
    due_date: datetime | None
    completed_at: datetime | None


class EnrollmentCreateResponse(BaseModel):
    created: int
    skipped: int
    enrollments: list[EnrollmentRead]


class LessonProgressRead(BaseModel):
    lesson_id: uuid.UUID
    status: str
    progress_percentage: float
    completed_at: datetime | None


class EnrollmentSummary(BaseModel):
    id: uuid.UUID
    status: str
    progress_percentage: float
    is_required: bool
    due_date: datetime | None
    overdue_action: str
    started_at: datetime | None
    completed_at: datetime | None


class EnrollmentContentRead(BaseModel):
    enrollment: EnrollmentSummary
    course: CourseDetailRead
    lesson_progress: list[LessonProgressRead]
    assessments: list[AssessmentStudentSummary] = Field(default_factory=list)


class LessonCompleteResponse(BaseModel):
    lesson_progress: LessonProgressRead
    enrollment: EnrollmentSummary
