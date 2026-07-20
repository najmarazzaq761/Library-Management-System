from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


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
