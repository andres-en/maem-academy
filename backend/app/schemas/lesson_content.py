import uuid

from pydantic import BaseModel, Field


class LessonContentRead(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    content_type: str
    title: str | None
    position: int
    text_content: str | None
    external_url: str | None
    file_url: str | None


class LessonContentUpdate(BaseModel):
    title: str | None = None
    text_content: str | None = None
    external_url: str | None = None


class MoveRequest(BaseModel):
    direction: str = Field(pattern="^(up|down)$")
