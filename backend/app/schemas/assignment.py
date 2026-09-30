import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import UserBrief


class AssignmentCreate(BaseModel):
    user_ids: list[uuid.UUID] = Field(default_factory=list)
    group_ids: list[uuid.UUID] = Field(default_factory=list)
    is_required: bool = False
    due_date: datetime | None = None
    overdue_action: str = Field(default="ALLOW_CONTINUE", pattern="^(ALLOW_CONTINUE|BLOCK)$")


class AssignmentUpdate(BaseModel):
    is_required: bool | None = None
    due_date: datetime | None = None
    overdue_action: str | None = Field(default=None, pattern="^(ALLOW_CONTINUE|BLOCK)$")
    status: str | None = Field(default=None, pattern="^(ACTIVE|INACTIVE)$")


class GroupBrief(BaseModel):
    id: uuid.UUID
    name: str


class AssignmentRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    is_required: bool
    due_date: datetime | None
    overdue_action: str
    status: str
    created_by: UserBrief
    created_at: datetime
    target_users: list[UserBrief] = Field(default_factory=list)
    target_groups: list[GroupBrief] = Field(default_factory=list)


class AssignmentCreateResponse(BaseModel):
    assignment: AssignmentRead
    enrollments_created: int
    enrollments_skipped: int
