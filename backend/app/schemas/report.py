import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import CourseBrief, UserBrief


class ReportSummary(BaseModel):
    active_users: int
    published_courses: int
    courses_in_review: int
    enrollments_total: int
    pending: int
    in_progress: int
    completed: int
    passed: int
    failed: int
    overdue: int
    cancelled: int


class CourseReportRow(BaseModel):
    enrollment_id: uuid.UUID
    user: UserBrief
    status: str
    progress_percentage: float
    score: float | None
    is_required: bool
    assigned_at: datetime
    due_date: datetime | None
    completed_at: datetime | None


class UserReportRow(BaseModel):
    enrollment_id: uuid.UUID
    course: CourseBrief
    status: str
    progress_percentage: float
    score: float | None
    is_required: bool
    assigned_at: datetime
    due_date: datetime | None
    completed_at: datetime | None


class AttemptAnswerDetail(BaseModel):
    question_id: uuid.UUID
    question_text: str
    points: float
    selected_option_text: str | None
    correct_option_text: str | None
    is_correct: bool
    points_awarded: float


class AttemptDetail(BaseModel):
    id: uuid.UUID
    attempt_number: int
    score: float | None
    status: str
    started_at: datetime
    submitted_at: datetime | None
    answers: list[AttemptAnswerDetail]


class AssessmentAttemptsDetail(BaseModel):
    assessment_id: uuid.UUID
    title: str
    module_title: str | None
    minimum_score: float
    attempts: list[AttemptDetail]


class EnrollmentAttemptsReport(BaseModel):
    user: UserBrief
    course: CourseBrief
    assessments: list[AssessmentAttemptsDetail]


class OptionStat(BaseModel):
    option_id: uuid.UUID
    text: str
    is_correct: bool
    count: int
    percentage: float


class QuestionStat(BaseModel):
    question_id: uuid.UUID
    question_text: str
    points: float
    total_answers: int
    correct_count: int
    correct_percentage: float
    unanswered_count: int
    unanswered_percentage: float
    options: list[OptionStat]


class AssessmentSummaryReport(BaseModel):
    assessment_id: uuid.UUID
    title: str
    module_title: str | None
    minimum_score: float
    graded_attempts: int
    students: int
    average_score: float | None
    pass_rate: float | None
    questions: list[QuestionStat]
