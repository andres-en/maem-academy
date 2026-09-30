from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import InvalidTokenError, create_access_token, verify_google_id_token
from app.models.user import User
from app.repositories import user_repository

settings = get_settings()


def _finish_login(db: Session, user: User) -> str:
    if user.status != "ACTIVE":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Your user is inactive. Please contact an administrator.")
    user.last_login_at = datetime.now(UTC)
    db.flush()
    return create_access_token(subject=str(user.id))


def login_with_google(db: Session, id_token: str) -> tuple[User, str]:
    try:
        claims = verify_google_id_token(id_token)
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid Google token: {exc}") from exc

    email = claims.get("email")
    if not email or not claims.get("email_verified", False):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "The Google email is not verified.")

    user = user_repository.get_by_email(db, email)
    if user is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "This email is not authorized on the platform. Ask an administrator to create your user.",
        )

    if not user.google_id:
        user.google_id = claims.get("sub")

    token = _finish_login(db, user)
    return user, token
