import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.enrollment import ACTIVE_ENROLLMENT_STATUSES, Enrollment

TERMINAL_STATUSES = ("COMPLETED", "PASSED", "FAILED", "CANCELLED")


def _with_relations(stmt):
    return stmt.options(joinedload(Enrollment.user), joinedload(Enrollment.course))


def create(
    db: Session,
    *,
    user_id: uuid.UUID,
    course_id: uuid.UUID,
    assignment_id: uuid.UUID | None,
    enrollment_type: str,
    is_required: bool,
    due_date: datetime | None,
) -> Enrollment:
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        assignment_id=assignment_id,
        enrollment_type=enrollment_type,
        status="ASSIGNED",
        is_required=is_required,
        due_date=due_date,
        assigned_at=datetime.now(UTC),
    )
    db.add(enrollment)
    return enrollment


def get_by_id(db: Session, enrollment_id: uuid.UUID) -> Enrollment | None:
    stmt = _with_relations(select(Enrollment).where(Enrollment.id == enrollment_id))
    return db.scalar(stmt)


def get_active_for_user_course(db: Session, *, user_id: uuid.UUID, course_id: uuid.UUID) -> Enrollment | None:
    stmt = select(Enrollment).where(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id,
        Enrollment.status.in_(ACTIVE_ENROLLMENT_STATUSES),
    )
    return db.scalar(stmt)


def has_terminal_for_user_course(db: Session, *, user_id: uuid.UUID, course_id: uuid.UUID) -> bool:
    stmt = select(Enrollment.id).where(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id,
        Enrollment.status.in_(TERMINAL_STATUSES),
    )
    return db.scalar(stmt) is not None


def list_by_course(db: Session, *, course_id: uuid.UUID, page: int, page_size: int) -> tuple[list[Enrollment], int]:
    stmt = _with_relations(select(Enrollment).where(Enrollment.course_id == course_id))
    total = db.scalar(select(func.count()).select_from(Enrollment).where(Enrollment.course_id == course_id)) or 0
    stmt = stmt.order_by(Enrollment.assigned_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).unique())
    return items, total


def list_by_user(db: Session, user_id: uuid.UUID) -> list[Enrollment]:
    stmt = _with_relations(select(Enrollment).where(Enrollment.user_id == user_id)).order_by(
        Enrollment.assigned_at.desc()
    )
    return list(db.scalars(stmt).unique())


def apply_overdue(db: Session, enrollment: Enrollment) -> Enrollment:
    if (
        enrollment.due_date is not None
        and enrollment.due_date < datetime.now(UTC)
        and enrollment.status in ("ASSIGNED", "IN_PROGRESS")
    ):
        enrollment.status = "OVERDUE"
        db.flush()
    return enrollment


def apply_overdue_bulk(db: Session) -> None:
    """Normaliza en bloque las matrículas vencidas antes de generar reportes,
    sin depender de que cada una haya sido leída individualmente (ver apply_overdue)."""
    stmt = (
        update(Enrollment)
        .where(Enrollment.due_date < datetime.now(UTC), Enrollment.status.in_(("ASSIGNED", "IN_PROGRESS")))
        .values(status="OVERDUE")
    )
    db.execute(stmt)
    db.commit()


def count_by_status(db: Session) -> dict[str, int]:
    stmt = select(Enrollment.status, func.count()).group_by(Enrollment.status)
    return {status: count for status, count in db.execute(stmt).all()}


def list_all_by_course(db: Session, course_id: uuid.UUID) -> list[Enrollment]:
    stmt = _with_relations(select(Enrollment).where(Enrollment.course_id == course_id)).order_by(
        Enrollment.assigned_at.desc()
    )
    return list(db.scalars(stmt).unique())


def count_by_course(db: Session, course_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(Enrollment).where(Enrollment.course_id == course_id)) or 0


def delete_all_by_course(db: Session, course_id: uuid.UUID) -> None:
    """Borra en bloque todas las matrículas de un curso; lesson_progress, assessment_attempts
    y attempt_answers se eliminan en cascada automáticamente (ON DELETE CASCADE)."""
    db.execute(delete(Enrollment).where(Enrollment.course_id == course_id))


def count_by_user(db: Session, user_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(Enrollment).where(Enrollment.user_id == user_id)) or 0


def delete_all_by_user(db: Session, user_id: uuid.UUID) -> None:
    """Borra en bloque las matrículas propias de un usuario (como estudiante); lesson_progress,
    assessment_attempts y attempt_answers se eliminan en cascada. No toca cursos que el usuario
    posea como propietario/creador — esos siguen protegidos por ON DELETE RESTRICT."""
    db.execute(delete(Enrollment).where(Enrollment.user_id == user_id))
