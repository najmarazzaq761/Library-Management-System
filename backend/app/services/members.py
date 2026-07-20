from sqlalchemy.orm import Session
from app.models.member import Member


def get_members(db: Session, skip: int = 0, limit: int = 100) -> list[Member]:
    """Retrieve a list of registered members (Librarian only)."""
    return db.query(Member).offset(skip).limit(limit).all()
