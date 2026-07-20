from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.book import Book
from app.schemas.book import BookCreate


def get_books(db: Session, skip: int = 0, limit: int = 100) -> list[Book]:
    """Retrieve book list with pagination."""
    return db.query(Book).offset(skip).limit(limit).all()


def search_books(
    db: Session, title: str | None = None, author: str | None = None
) -> list[Book]:
    """Search catalog matching title or author parameters."""
    query = db.query(Book)
    conditions = []
    if title:
        conditions.append(Book.title.ilike(f"%{title}%"))
    if author:
        conditions.append(Book.author.ilike(f"%{author}%"))

    if conditions:
        query = query.filter(or_(*conditions))
    return query.all()


def add_book(db: Session, book_in: BookCreate) -> Book:
    """Register a new book into the library catalog."""
    existing_book = db.query(Book).filter(Book.isbn == book_in.isbn).first()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ISBN '{book_in.isbn}' already exists."
        )

    db_book = Book(
        title=book_in.title,
        author=book_in.author,
        isbn=book_in.isbn,
        available_copies=book_in.available_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
