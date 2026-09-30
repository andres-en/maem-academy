import uuid

from pydantic import BaseModel, Field


class QuestionOptionCreate(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool = False


class QuestionCreate(BaseModel):
    question_text: str = Field(min_length=1)
    points: float = Field(default=1, gt=0)
    options: list[QuestionOptionCreate] = Field(min_length=2)


class QuestionOptionRead(BaseModel):
    id: uuid.UUID
    text: str
    is_correct: bool
    position: int


class QuestionRead(BaseModel):
    id: uuid.UUID
    question_text: str
    points: float
    position: int
    options: list[QuestionOptionRead]


class AssessmentCreate(BaseModel):
    module_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    minimum_score: float = Field(default=70, ge=0, le=100)
    max_attempts: int | None = Field(default=None, gt=0)
    is_required: bool = True


class AssessmentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    minimum_score: float = Field(ge=0, le=100)
    max_attempts: int | None = Field(default=None, gt=0)
    is_required: bool = True


class AssessmentRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    module_id: uuid.UUID | None
    title: str
    description: str | None
    minimum_score: float
    max_attempts: int | None
    is_required: bool
    questions: list[QuestionRead]
