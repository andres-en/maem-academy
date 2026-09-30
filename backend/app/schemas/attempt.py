import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AttemptOptionRead(BaseModel):
    id: uuid.UUID
    text: str


class AttemptQuestionRead(BaseModel):
    id: uuid.UUID
    question_text: str
    points: float
    options: list[AttemptOptionRead]


class StartAttemptResponse(BaseModel):
    attempt_id: uuid.UUID
    attempt_number: int
    status: str
    questions: list[AttemptQuestionRead]


class AnswerSubmit(BaseModel):
    question_id: uuid.UUID
    selected_option_id: uuid.UUID | None = None


class SubmitAttemptRequest(BaseModel):
    answers: list[AnswerSubmit] = Field(default_factory=list)


class AttemptAnswerResult(BaseModel):
    question_id: uuid.UUID
    question_text: str
    selected_option_id: uuid.UUID | None
    correct_option_id: uuid.UUID | None
    is_correct: bool
    points_awarded: float


class AttemptResultRead(BaseModel):
    attempt_id: uuid.UUID
    attempt_number: int
    score: float
    status: str
    submitted_at: datetime | None
    answers: list[AttemptAnswerResult]


class AttemptSummaryRead(BaseModel):
    id: uuid.UUID
    attempt_number: int
    score: float | None
    status: str
    started_at: datetime
    submitted_at: datetime | None


class AssessmentStudentSummary(BaseModel):
    id: uuid.UUID
    title: str
    module_id: uuid.UUID | None
    minimum_score: float
    max_attempts: int | None
    is_required: bool
    attempts_used: int
    best_score: float | None
    status: str
