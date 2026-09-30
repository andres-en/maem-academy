import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.category import CategoryRead
from app.schemas.common import UserBrief
from app.schemas.module import ModuleDetailRead


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    estimated_duration_minutes: int | None = None
    category_ids: list[uuid.UUID] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    estimated_duration_minutes: int | None = None
    category_ids: list[uuid.UUID] = Field(default_factory=list)


class CollaboratorAddRequest(BaseModel):
    user_ids: list[uuid.UUID] = Field(min_length=1)


class ReviewCommentRequest(BaseModel):
    comment: str = Field(min_length=1)


class ForceDeleteRequest(BaseModel):
    confirm_title: str = Field(min_length=1)


class CourseRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    cover_image_url: str | None
    estimated_duration_minutes: int | None
    status: str
    owner: UserBrief
    categories: list[CategoryRead] = Field(default_factory=list)
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CourseDetailRead(CourseRead):
    collaborators: list[UserBrief] = Field(default_factory=list)
    reviewed_by: UserBrief | None = None
    review_comment: str | None = None
    reviewed_at: datetime | None = None
    modules: list[ModuleDetailRead] = Field(default_factory=list)
