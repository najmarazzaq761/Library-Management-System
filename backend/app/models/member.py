from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Member(Base):
    """Library member/user model."""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(
        String(50), default="member", server_default="member", nullable=False
    )
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with loans
    loans = relationship("Loan", back_populates="member")

    def __repr__(self):
        return f"<Member(name='{self.name}', email='{self.email}')>"
