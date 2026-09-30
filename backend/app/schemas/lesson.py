import uuid

from pydantic import BaseModel, Field

from app.schemas.lesson_content import LessonContentRead


class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    completion_type: str = Field(default="MANUAL", pattern="^(MANUAL|AUTO)$")


class LessonUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    completion_type: str = Field(pattern="^(MANUAL|AUTO)$")


class LessonRead(BaseModel):
    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    description: str | None
    position: int
    completion_type: str


class LessonDetailRead(LessonRead):
    contents: list[LessonContentRead] = Field(default_factory=list)
