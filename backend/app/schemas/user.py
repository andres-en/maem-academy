import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.group import GroupRead
from app.schemas.role import RoleRead


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    role_id: uuid.UUID
    group_ids: list[uuid.UUID] = Field(default_factory=list)


class UserUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    role_id: uuid.UUID
    group_ids: list[uuid.UUID] = Field(default_factory=list)


class UserStatusUpdate(BaseModel):
    status: str = Field(pattern="^(ACTIVE|INACTIVE)$")


class ForceDeleteUserRequest(BaseModel):
    confirm_email: str = Field(min_length=1)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    status: str
    role: RoleRead
    last_login_at: datetime | None
    created_at: datetime


class UserDetailRead(UserRead):
    groups: list[GroupRead] = Field(default_factory=list)


class ImportRowResult(BaseModel):
    row_number: int
    full_name: str | None = None
    email: str | None = None
    role: str | None = None
    groups: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


class ImportPreviewResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    rows: list[ImportRowResult]


class ImportConfirmResponse(BaseModel):
    created: int
    skipped: int
    rows: list[ImportRowResult]
