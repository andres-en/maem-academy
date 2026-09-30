import uuid

from pydantic import BaseModel, Field

from app.schemas.lesson import LessonDetailRead


class ModuleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ModuleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ModuleRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    description: str | None
    position: int


class ModuleDetailRead(ModuleRead):
    lessons: list[LessonDetailRead] = Field(default_factory=list)
