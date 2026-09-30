import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.storage import ensure_bucket

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        ensure_bucket()
    except Exception:  # noqa: BLE001 - no debe impedir que el backend arranque
        logger.exception("Could not initialize the storage bucket.")
    yield


API_DESCRIPTION = """
REST API of **MAEM Academy**, a corporate learning management system (LMS).

* **Auth** - Google Sign-In is exchanged for the API's own JWT (`POST /api/v1/auth/google`);
  send it as `Authorization: Bearer <token>`.
* **Roles** - `SUPERADMIN`, `ADMIN`, `INSTRUCTOR` and `USER` (learner), enforced per endpoint.
* **Course workflow** - `DRAFT -> IN_REVIEW -> (CHANGES_REQUESTED | APPROVED) -> PUBLISHED -> ARCHIVED`.
* **Learning** - enrollments (individual or by group), lesson progress, graded assessments with
  attempt limits, due dates that can block access, and reports.
"""

OPENAPI_TAGS = [
    {"name": "auth", "description": "Google Sign-In exchange and the current user."},
    {"name": "roles", "description": "Role catalog."},
    {"name": "users", "description": "User management and bulk import from Excel (admins)."},
    {"name": "groups", "description": "Teams used for bulk enrollment."},
    {"name": "categories", "description": "Course categories."},
    {"name": "courses", "description": "Course authoring (modules, lessons, contents) and the review workflow."},
    {"name": "enrollments", "description": "Assignments, enrollments and the learner's progress."},
    {"name": "assessments", "description": "Assessments, questions and graded attempts."},
    {"name": "reports", "description": "Platform, course and user reports."},
    {"name": "system", "description": "Health and public configuration."},
]

app = FastAPI(
    title="MAEM Academy API",
    version="1.0.0",
    description=API_DESCRIPTION,
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/v1/system/info", tags=["system"])
def system_info() -> dict:
    return {
        "environment": settings.environment,
        "google_oauth_enabled": bool(settings.google_client_id),
    }


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok"}
