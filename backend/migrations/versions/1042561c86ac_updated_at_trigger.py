"""updated_at trigger

Revision ID: 1042561c86ac
Revises: 92da9ab934c3
Create Date: 2026-09-08 15:51:41.177031

"""
from collections.abc import Sequence

from alembic import op

revision: str = '1042561c86ac'
down_revision: str | None = '92da9ab934c3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Tablas con columna updated_at (ver sección 30, punto 9 del modelo de datos).
TABLES_WITH_UPDATED_AT = [
    "users",
    "groups",
    "categories",
    "courses",
    "course_modules",
    "lessons",
    "lesson_contents",
    "course_assignments",
    "enrollments",
    "lesson_progress",
    "assessments",
    "assessment_questions",
]


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in TABLES_WITH_UPDATED_AT:
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_set_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in TABLES_WITH_UPDATED_AT:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_set_updated_at ON {table};")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")
