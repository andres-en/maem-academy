import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    user_ids: list[uuid.UUID] = Field(default_factory=list)


class GroupUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class GroupStatusUpdate(BaseModel):
    status: str = Field(pattern="^(ACTIVE|INACTIVE)$")


class GroupAddUsersRequest(BaseModel):
    user_ids: list[uuid.UUID] = Field(min_length=1)


class GroupMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    status: str
    created_at: datetime
    member_count: int = 0


class GroupDetailRead(GroupRead):
    members: list[GroupMemberRead] = Field(default_factory=list)
