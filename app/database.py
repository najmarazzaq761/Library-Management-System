"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/library_db"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_data():
    """Add sample data."""
    from app.models import Book, Member
    db = SessionLocal()
    try:
        # Check if data exists
        if db.query(Book).count() == 0:
            books = [
                Book(
                    title="1984",
                    author="George Orwell",
                    isbn="978-0451524935"
                ),
                Book(
                    title="Brave New World",
                    author="Aldous Huxley",
                    isbn="978-0060850524"
                ),
                Book(
                    title="The Hobbit",
                    author="J.R.R. Tolkien",
                    isbn="978-0547928227"
                ),
                Book(
                    title="Pride and Prejudice",
                    author="Jane Austen",
                    isbn="978-0141439518"
                ),
                Book(
                    title="The Great Gatsby",
                    author="F. Scott Fitzgerald",
                    isbn="978-0743273565"
                ),
            ]
            for book in books:
                db.add(book)
            db.commit()
            print("Sample books added!")

        if db.query(Member).count() == 0:
            members = [
                Member(name="Ali", email="ali@gamil.com"),
                Member(name="Asad", email="asad@gmail.com"),
                Member(name="Asif", email="asif@gmail.com"),

            ]
            for member in members:
                db.add(member)
            db.commit()
            print("Sample members added!")
    finally:
        db.close()