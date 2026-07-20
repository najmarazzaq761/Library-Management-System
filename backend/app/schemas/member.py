from pydantic import BaseModel
from datetime import datetime


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
    role: str = "member"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
