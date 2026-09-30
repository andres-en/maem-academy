import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.group import Group, UserGroup


def list_groups(db: Session, *, status: str | None = None) -> list[tuple[Group, int]]:
    stmt = (
        select(Group, func.count(UserGroup.user_id))
        .outerjoin(UserGroup, UserGroup.group_id == Group.id)
        .group_by(Group.id)
        .order_by(Group.name)
    )
    if status:
        stmt = stmt.where(Group.status == status)
    return [(g, count) for g, count in db.execute(stmt).all()]


def get_by_id(db: Session, group_id: uuid.UUID) -> Group | None:
    return db.get(Group, group_id)


def get_with_members(db: Session, group_id: uuid.UUID) -> Group | None:
    stmt = (
        select(Group).where(Group.id == group_id).options(selectinload(Group.user_groups).selectinload(UserGroup.user))
    )
    return db.scalar(stmt)


def get_by_name(db: Session, name: str) -> Group | None:
    return db.scalar(select(Group).where(Group.name == name))


def create(db: Session, *, name: str, description: str | None) -> Group:
    group = Group(name=name, description=description, status="ACTIVE")
    db.add(group)
    return group


def add_users(db: Session, *, group_id: uuid.UUID, user_ids: list[uuid.UUID]) -> None:
    existing = set(
        db.scalars(select(UserGroup.user_id).where(UserGroup.group_id == group_id, UserGroup.user_id.in_(user_ids)))
    )
    for user_id in user_ids:
        if user_id not in existing:
            db.add(UserGroup(group_id=group_id, user_id=user_id))


def remove_user(db: Session, *, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    link = db.get(UserGroup, {"group_id": group_id, "user_id": user_id})
    if link is None:
        return False
    db.delete(link)
    return True


def member_count(db: Session, group_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(UserGroup).where(UserGroup.group_id == group_id)) or 0


def list_member_user_ids(db: Session, group_id: uuid.UUID) -> list[uuid.UUID]:
    return list(db.scalars(select(UserGroup.user_id).where(UserGroup.group_id == group_id)))
