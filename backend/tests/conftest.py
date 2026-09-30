"""Test infrastructure.

Tests run against a real PostgreSQL database (the app relies on UUID, JSONB,
CHECK constraints and triggers), created with `alembic upgrade head` so the
migrations are exercised too. Point TEST_DATABASE_URL at a disposable database:

    docker run -d --name maem-pg-test -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=maem_test -p 55432:5432 postgres:16-alpine
    pytest

Object storage (S3/MinIO) is replaced by an in-memory fake.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

# Must be set before any `app.*` import: settings are read at import time.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:55432/maem_test"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET"] = "test-secret-not-used-anywhere-else"
os.environ["GOOGLE_CLIENT_ID"] = ""

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.security import create_access_token  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.role import Role  # noqa: E402
from app.models.user import User  # noqa: E402
from app.scripts.seed_initial_data import ROLE_DEFINITIONS  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def _migrated_database():
    """Fresh schema for the whole run, built by the Alembic migrations."""
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    command.upgrade(cfg, "head")
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables():
    """Every test starts from the seeded baseline: the 4 roles and the GENERAL category."""
    with engine.begin() as conn:
        tables = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename <> 'alembic_version'")
        ).scalars()
        conn.execute(text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"))
    with SessionLocal() as db:
        for name, display_name, description in ROLE_DEFINITIONS:
            db.add(Role(name=name, display_name=display_name, description=description))
        db.add(Category(name="GENERAL", description="Company-wide training.", status="ACTIVE"))
        db.commit()


class FakeStorage:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def upload_bytes(self, *, key: str, data: bytes, content_type: str) -> None:
        self.objects[key] = data

    def delete_object(self, key: str) -> None:
        self.objects.pop(key, None)

    @staticmethod
    def build_public_url(key: str | None) -> str | None:
        return f"http://storage.test/{key}" if key else None


@pytest.fixture(autouse=True)
def storage(monkeypatch) -> FakeStorage:
    fake = FakeStorage()
    import app.core.storage as storage_module

    for name in ("upload_bytes", "delete_object", "build_public_url"):
        monkeypatch.setattr(storage_module, name, getattr(fake, name))
    monkeypatch.setattr("app.main.ensure_bucket", lambda: None)
    return fake


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_user():
    """Create an active user with the given role; returns `(user_id, auth_headers)`."""

    def _make(role: str = "USER", *, email: str | None = None, status: str = "ACTIVE"):
        with SessionLocal() as db:
            role_row = db.query(Role).filter(Role.name == role).one()
            user = User(
                full_name=f"{role.title()} Tester",
                email=email or f"{role.lower()}-{uuid.uuid4().hex[:8]}@example.com",
                role_id=role_row.id,
                status=status,
            )
            db.add(user)
            db.commit()
            user_id = user.id
        token = create_access_token(subject=str(user_id))
        return user_id, {"Authorization": f"Bearer {token}"}

    return _make
