import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def list_categories(db: Session, *, status: str | None = None) -> list[Category]:
    stmt = select(Category).order_by(Category.name)
    if status:
        stmt = stmt.where(Category.status == status)
    return list(db.scalars(stmt))


def get_by_id(db: Session, category_id: uuid.UUID) -> Category | None:
    return db.get(Category, category_id)


def get_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))


def create(db: Session, *, name: str, description: str | None) -> Category:
    category = Category(name=name, description=description, status="ACTIVE")
    db.add(category)
    return category
