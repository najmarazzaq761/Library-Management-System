from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import schemas
from app.services import auth as auth_service

router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=schemas.MemberSchema, status_code=201)
def signup(
    member_in: schemas.MemberCreate,
    db: Session = Depends(get_db)
):
    """Register a new member (Public)."""
    return auth_service.create_member(db, member_in)


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login to obtain a JWT access token (Public)."""
    return auth_service.authenticate_member(
        db, form_data.username, form_data.password
    )
