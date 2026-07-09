from pydantic import BaseModel
from datetime import datetime

class BookSchema(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    available_copies: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    available_copies: int = 1

class MemberSchema(BaseModel):
    id: int
    name: str
    email: str
    role: str
    registered_at: datetime

    class Config:
        from_attributes = True

class MemberCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "member"  # can be "member" or "librarian"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class LoanCreate(BaseModel):
    book_id: int
    member_id: int | None = None  # if not specified, default to logged in member

class LoanSchema(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    returned_at: datetime | None = None
    is_returned: bool

    class Config:
        from_attributes = True


