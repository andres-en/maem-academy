import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import storage
from app.core.constants import ADMIN_ROLES
from app.models.course import Course
from app.models.user import User
from app.repositories import audit_repository, course_repository, enrollment_repository, user_repository
from app.schemas.category import CategoryRead
from app.schemas.common import UserBrief
from app.schemas.course import CourseDetailRead, CourseRead
from app.schemas.lesson import LessonDetailRead
from app.schemas.lesson_content import LessonContentRead
from app.schemas.module import ModuleDetailRead
from app.services.course_permissions import ensure_can_edit_course, ensure_is_owner_or_admin
from app.services.deletion import run_delete_or_conflict


def _user_brief(user: User) -> UserBrief:
    return UserBrief(id=user.id, full_name=user.full_name, email=user.email)


def to_course_read(course: Course) -> CourseRead:
    return CourseRead(
        id=course.id,
        title=course.title,
        description=course.description,
        cover_image_url=storage.build_public_url(course.cover_image_url),
        estimated_duration_minutes=course.estimated_duration_minutes,
        status=course.status,
        owner=_user_brief(course.owner),
        categories=[CategoryRead.model_validate(c) for c in course.categories],
        published_at=course.published_at,
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


def to_course_detail(course: Course) -> CourseDetailRead:
    base = to_course_read(course)
    modules: list[ModuleDetailRead] = []
    for m in sorted(course.modules, key=lambda x: x.position):
        lessons: list[LessonDetailRead] = []
        for lesson in sorted(m.lessons, key=lambda x: x.position):
            contents = [
                LessonContentRead(
                    id=c.id,
                    lesson_id=c.lesson_id,
                    content_type=c.content_type,
                    title=c.title,
                    position=c.position,
                    text_content=c.text_content,
                    external_url=c.external_url,
                    file_url=storage.build_public_url(c.file_url),
                )
                for c in sorted(lesson.contents, key=lambda x: x.position)
            ]
            lessons.append(
                LessonDetailRead(
                    id=lesson.id,
                    module_id=lesson.module_id,
                    title=lesson.title,
                    description=lesson.description,
                    position=lesson.position,
                    completion_type=lesson.completion_type,
                    contents=contents,
                )
            )
        modules.append(
            ModuleDetailRead(
                id=m.id,
                course_id=m.course_id,
                title=m.title,
                description=m.description,
                position=m.position,
                lessons=lessons,
            )
        )

    return CourseDetailRead(
        **base.model_dump(),
        collaborators=[_user_brief(link.user) for link in course.collaborator_links],
        reviewed_by=_user_brief(course.reviewer) if course.reviewer else None,
        review_comment=course.review_comment,
        reviewed_at=course.reviewed_at,
        modules=modules,
    )


def list_courses(
    db: Session,
    *,
    page: int,
    page_size: int,
    status_filter: str | None,
    category_id: uuid.UUID | None,
    mine_user_id: uuid.UUID | None,
    search: str | None,
) -> tuple[list[Course], int]:
    return course_repository.list_courses(
        db,
        page=page,
        page_size=page_size,
        status=status_filter,
        category_id=category_id,
        mine_user_id=mine_user_id,
        search=search,
    )


def get_course_detail(db: Session, course_id: uuid.UUID) -> Course:
    course = course_repository.get_detail(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    return course


def create_course(
    db: Session,
    *,
    current_user: User,
    title: str,
    description: str | None,
    estimated_duration_minutes: int | None,
    category_ids: list[uuid.UUID],
) -> Course:
    course = course_repository.create(
        db,
        title=title,
        description=description,
        estimated_duration_minutes=estimated_duration_minutes,
        owner_id=current_user.id,
    )
    db.flush()
    course_repository.set_categories(db, course, category_ids)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_CREATED",
        entity_type="course",
        entity_id=course.id,
        new_data={"title": title},
    )
    db.commit()
    return get_course_detail(db, course.id)


def update_course(
    db: Session,
    *,
    current_user: User,
    course_id: uuid.UUID,
    title: str,
    description: str | None,
    estimated_duration_minutes: int | None,
    category_ids: list[uuid.UUID],
) -> Course:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)

    old_data = {"title": course.title}
    course.title = title
    course.description = description
    course.estimated_duration_minutes = estimated_duration_minutes
    course_repository.set_categories(db, course, category_ids)
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_UPDATED",
        entity_type="course",
        entity_id=course.id,
        old_data=old_data,
        new_data={"title": title},
    )
    db.commit()
    return get_course_detail(db, course.id)


def update_cover_image(db: Session, *, current_user: User, course_id: uuid.UUID, object_key: str) -> Course:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)
    course.cover_image_url = object_key
    db.commit()
    return get_course_detail(db, course.id)


def add_collaborators(db: Session, *, current_user: User, course_id: uuid.UUID, user_ids: list[uuid.UUID]) -> Course:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_is_owner_or_admin(current_user, course)

    found = user_repository.get_many_by_ids(db, user_ids)
    missing = set(user_ids) - {u.id for u in found}
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Users not found: {', '.join(map(str, missing))}")

    course_repository.add_collaborators(db, course_id=course_id, user_ids=user_ids, added_by=current_user.id)
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_COLLABORATOR_ADDED",
        entity_type="course",
        entity_id=course.id,
        new_data={"user_ids": [str(u) for u in user_ids]},
    )
    db.commit()
    return get_course_detail(db, course_id)


def remove_collaborator(db: Session, *, current_user: User, course_id: uuid.UUID, user_id: uuid.UUID) -> Course:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_is_owner_or_admin(current_user, course)

    removed = course_repository.remove_collaborator(db, course_id=course_id, user_id=user_id)
    if not removed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That user is not a collaborator of this course.")
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_COLLABORATOR_REMOVED",
        entity_type="course",
        entity_id=course.id,
        new_data={"user_id": str(user_id)},
    )
    db.commit()
    return get_course_detail(db, course_id)


def submit_for_review(db: Session, *, current_user: User, course_id: uuid.UUID) -> Course:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    ensure_can_edit_course(db, course, current_user)
    if course.status not in ("DRAFT", "CHANGES_REQUESTED"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "The course is not in a valid state to be submitted for review."
        )
    if not course.modules:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "The course needs at least one module before it can be submitted for review."
        )

    old_status = course.status
    course.status = "IN_REVIEW"
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_SUBMITTED_REVIEW",
        entity_type="course",
        entity_id=course.id,
        old_data={"status": old_status},
        new_data={"status": "IN_REVIEW"},
    )
    db.commit()
    return get_course_detail(db, course_id)


def _require_admin_review(current_user: User) -> None:
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only an administrator can review courses.")


def approve_course(db: Session, *, current_user: User, course_id: uuid.UUID) -> Course:
    _require_admin_review(current_user)
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status != "IN_REVIEW":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only courses in review can be approved.")

    course.status = "APPROVED"
    course.reviewed_by = current_user.id
    course.reviewed_at = datetime.now(UTC)
    course.review_comment = None
    db.flush()
    audit_repository.log_action(
        db, user_id=current_user.id, action="COURSE_APPROVED", entity_type="course", entity_id=course.id
    )
    db.commit()
    return get_course_detail(db, course_id)


def request_changes(db: Session, *, current_user: User, course_id: uuid.UUID, comment: str) -> Course:
    _require_admin_review(current_user)
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status != "IN_REVIEW":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only courses in review can be sent back.")

    course.status = "CHANGES_REQUESTED"
    course.reviewed_by = current_user.id
    course.reviewed_at = datetime.now(UTC)
    course.review_comment = comment
    db.flush()
    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_CHANGES_REQUESTED",
        entity_type="course",
        entity_id=course.id,
        new_data={"comment": comment},
    )
    db.commit()
    return get_course_detail(db, course_id)


def publish_course(db: Session, *, current_user: User, course_id: uuid.UUID) -> Course:
    _require_admin_review(current_user)
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status != "APPROVED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only approved courses can be published.")

    course.status = "PUBLISHED"
    course.published_at = datetime.now(UTC)
    db.flush()
    audit_repository.log_action(
        db, user_id=current_user.id, action="COURSE_PUBLISHED", entity_type="course", entity_id=course.id
    )
    db.commit()
    return get_course_detail(db, course_id)


def archive_course(db: Session, *, current_user: User, course_id: uuid.UUID) -> Course:
    _require_admin_review(current_user)
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status == "ARCHIVED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The course is already archived.")

    course.status = "ARCHIVED"
    db.flush()
    audit_repository.log_action(
        db, user_id=current_user.id, action="COURSE_ARCHIVED", entity_type="course", entity_id=course.id
    )
    db.commit()
    return get_course_detail(db, course_id)


def _collect_course_file_keys(course: Course) -> list[str]:
    file_keys: list[str] = []
    if course.cover_image_url:
        file_keys.append(course.cover_image_url)
    for module in course.modules:
        for lesson in module.lessons:
            for content in lesson.contents:
                if content.file_url:
                    file_keys.append(content.file_url)
    return file_keys


def delete_course(db: Session, *, current_user: User, course_id: uuid.UUID) -> None:
    course = course_repository.get_detail(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status != "ARCHIVED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must archive the course before deleting it.")

    file_keys = _collect_course_file_keys(course)

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_DELETED",
        entity_type="course",
        entity_id=course.id,
        old_data={"title": course.title},
    )
    run_delete_or_conflict(db, course, "Cannot delete: the course has enrollments.")

    for key in file_keys:
        storage.delete_object(key)


def force_delete_course(db: Session, *, current_user: User, course_id: uuid.UUID, confirm_title: str) -> None:
    """Elimina el curso JUNTO CON sus matrículas, progreso y resultados de evaluación de
    todos los estudiantes inscritos. Irreversible — solo para SUPERADMIN (ver router)."""
    course = course_repository.get_detail(db, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if course.status != "ARCHIVED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You must archive the course before deleting it.")
    if confirm_title != course.title:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The title entered does not match the course title.")

    file_keys = _collect_course_file_keys(course)
    enrollments_count = enrollment_repository.count_by_course(db, course_id)

    audit_repository.log_action(
        db,
        user_id=current_user.id,
        action="COURSE_FORCE_DELETED",
        entity_type="course",
        entity_id=course.id,
        old_data={"title": course.title, "enrollments_deleted": enrollments_count},
    )
    enrollment_repository.delete_all_by_course(db, course_id)
    db.delete(course)
    db.commit()

    for key in file_keys:
        storage.delete_object(key)
