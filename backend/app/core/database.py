import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()


def init_db():
    """Create all tables via Alembic migrations on startup."""
    from alembic.config import Config
    from alembic import command

    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    ini_path = os.path.join(base_dir, "alembic.ini")

    alembic_cfg = Config(ini_path)
    migrations_dir = os.path.join(base_dir, "migrations")
    alembic_cfg.set_main_option("script_location", migrations_dir)

    command.upgrade(alembic_cfg, "head")


def get_db():
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_data():
    """Add sample data if database is empty."""
    from app.models.book import Book
    from app.models.member import Member
    from app.core.security import hash_password

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
                Member(
                    name="Ali",
                    email="ali@gamil.com",
                    hashed_password=hash_password("password123"),
                    role="member"
                ),
                Member(
                    name="Asad",
                    email="asad@gmail.com",
                    hashed_password=hash_password("password123"),
                    role="member"
                ),
                Member(
                    name="Asif",
                    email="asif@gmail.com",
                    hashed_password=hash_password("password123"),
                    role="member"
                ),
                Member(
                    name="Librarian Jane",
                    email="librarian@library.com",
                    hashed_password=hash_password("librarianpass"),
                    role="librarian"
                ),
            ]
            for member in members:
                db.add(member)
            db.commit()
            print("Sample members and librarian added!")
    finally:
        db.close()
