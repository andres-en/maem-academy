from fastapi import APIRouter

from app.api.v1 import (
    assessments,
    assignments,
    attempts,
    auth,
    categories,
    course_modules,
    courses,
    enrollments,
    groups,
    lesson_contents,
    lessons,
    reports,
    roles,
    users,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(categories.router)
api_router.include_router(courses.router)
api_router.include_router(course_modules.router)
api_router.include_router(lessons.router)
api_router.include_router(lesson_contents.router)
api_router.include_router(assignments.router)
api_router.include_router(enrollments.router)
api_router.include_router(assessments.router)
api_router.include_router(attempts.router)
api_router.include_router(reports.router)
