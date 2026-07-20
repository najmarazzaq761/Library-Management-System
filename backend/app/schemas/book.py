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
        from_attributes = True


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    available_copies: int = 1
