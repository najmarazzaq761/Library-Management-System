from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.member import Member
from app.schemas.member import MemberCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def create_member(db: Session, member_in: MemberCreate) -> Member:
    """Register a new library member."""
    existing_user = db.query(Member).filter(
        Member.email == member_in.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{member_in.email}' is already registered."
        )

    db_member = Member(
        name=member_in.name,
        email=member_in.email,
        hashed_password=hash_password(member_in.password),
        role=member_in.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def authenticate_member(db: Session, email: str, password: str) -> dict:
    """Verify credentials and return access tokens."""
    member = db.query(Member).filter(Member.email == email).first()
    if not member or not verify_password(password, member.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": member.email})
    return {"access_token": access_token, "token_type": "bearer"}
