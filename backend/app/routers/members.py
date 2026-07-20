from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app import schemas, models
from app.services import members as members_service

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("", response_model=list[schemas.MemberSchema])
def list_members(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Retrieve a list of members with pagination (Librarian only)."""
    return members_service.get_members(db, skip, limit)
