"""Database models for Library Management System."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Book(Base):
    """Book model."""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    available_copies = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with loans
    loans = relationship("Loan", back_populates="book")

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"


class Member(Base):
    """Library member model."""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with loans
    loans = relationship("Loan", back_populates="member")

    def __repr__(self):
        return f"<Member(name='{self.name}', email='{self.email}')>"


class Loan(Base):
    """Book loan/borrowing record."""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    member_id = Column(Integer, ForeignKey("members.id"))
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    returned_at = Column(DateTime, nullable=True)
    is_returned = Column(Boolean, default=False)

    # Relationships
    book = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")

    def __repr__(self):
        status = "returned" if self.is_returned else "borrowed"
        return (
            f"<Loan(book='{self.book.title}', "
            f"member='{self.member.name}', status='{status}')>"
        )