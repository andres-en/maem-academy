from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.repositories import role_repository
from app.schemas.role import RoleRead

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleRead])
def list_roles(db: Session = Depends(get_db), _=Depends(get_current_user)) -> list[RoleRead]:
    return [RoleRead.model_validate(r) for r in role_repository.list_roles(db)]
