import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role


def list_roles(db: Session) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.display_name)))


def get_by_id(db: Session, role_id: uuid.UUID) -> Role | None:
    return db.get(Role, role_id)


def get_by_name(db: Session, name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == name))
