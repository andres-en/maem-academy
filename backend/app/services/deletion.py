from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def run_delete_or_conflict(db: Session, entity, conflict_message: str) -> None:
    """Intenta eliminar `entity`; si la base de datos lo bloquea por una relación
    RESTRICT (historial académico real), traduce el error a un 409 legible."""
    db.delete(entity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, conflict_message) from None
