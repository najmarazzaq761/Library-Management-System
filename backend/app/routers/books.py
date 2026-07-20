from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app import schemas, models
from app.services import books as books_service

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[schemas.BookSchema])
def list_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve a list of books with pagination (Public)."""
    return books_service.get_books(db, skip, limit)


@router.get("/search", response_model=list[schemas.BookSchema])
def search_books(
    title: str | None = Query(
        None, description="Search by book title (case-insensitive)"
    ),
    author: str | None = Query(
        None, description="Search by book author (case-insensitive)"
    ),
    db: Session = Depends(get_db)
):
    """Search books by title and/or author (Public)."""
    return books_service.search_books(db, title, author)


@router.post("", response_model=schemas.BookSchema, status_code=201)
def add_book(
    book_in: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Add a new book to the library (Librarian only)."""
    return books_service.add_book(db, book_in)
