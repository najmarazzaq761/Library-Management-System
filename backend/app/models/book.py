from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


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
