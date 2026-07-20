from pydantic import BaseModel
from datetime import datetime
from app.schemas.book import BookSchema
from app.schemas.member import MemberSchema


class LoanCreate(BaseModel):
    book_id: int
    member_id: int | None = None


class LoanSchema(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    returned_at: datetime | None = None
    is_returned: bool

    class Config:
        from_attributes = True


class LoanDetailSchema(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    returned_at: datetime | None = None
    is_returned: bool
    book: BookSchema
    member: MemberSchema

    class Config:
        from_attributes = True
