import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.group import UserGroup
from app.models.user import User


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.scalar(select(User).where(User.id == user_id).options(joinedload(User.role)))


def get_with_groups(db: Session, user_id: uuid.UUID) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            joinedload(User.role),
            selectinload(User.user_groups).selectinload(UserGroup.group),
        )
    )
    return db.scalar(stmt)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email).options(joinedload(User.role)))


def list_users(
    db: Session,
    *,
    page: int,
    page_size: int,
    role_id: uuid.UUID | None = None,
    status: str | None = None,
    group_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[User], int]:
    stmt = select(User).options(joinedload(User.role))
    count_stmt = select(func.count(func.distinct(User.id))).select_from(User)

    if group_id is not None:
        stmt = stmt.join(UserGroup, UserGroup.user_id == User.id).where(UserGroup.group_id == group_id)
        count_stmt = count_stmt.join(UserGroup, UserGroup.user_id == User.id).where(UserGroup.group_id == group_id)
    if role_id is not None:
        stmt = stmt.where(User.role_id == role_id)
        count_stmt = count_stmt.where(User.role_id == role_id)
    if status is not None:
        stmt = stmt.where(User.status == status)
        count_stmt = count_stmt.where(User.status == status)
    if search:
        pattern = f"%{search.lower()}%"
        stmt = stmt.where(func.lower(User.full_name).like(pattern) | func.lower(User.email).like(pattern))
        count_stmt = count_stmt.where(func.lower(User.full_name).like(pattern) | func.lower(User.email).like(pattern))

    total = db.scalar(count_stmt) or 0
    stmt = stmt.order_by(User.full_name).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).unique())
    return items, total


def create(db: Session, *, full_name: str, email: str, role_id: uuid.UUID) -> User:
    user = User(full_name=full_name, email=email, role_id=role_id, status="ACTIVE")
    db.add(user)
    return user


def set_groups(db: Session, *, user_id: uuid.UUID, group_ids: list[uuid.UUID]) -> None:
    db.query(UserGroup).filter(UserGroup.user_id == user_id).delete(synchronize_session=False)
    for group_id in group_ids:
        db.add(UserGroup(user_id=user_id, group_id=group_id))


def existing_emails(db: Session, emails: list[str]) -> set[str]:
    if not emails:
        return set()
    return set(db.scalars(select(User.email).where(User.email.in_(emails))))


def get_many_by_ids(db: Session, user_ids: list[uuid.UUID]) -> list[User]:
    if not user_ids:
        return []
    return list(db.scalars(select(User).where(User.id.in_(user_ids))))
