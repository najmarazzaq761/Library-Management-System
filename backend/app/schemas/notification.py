from pydantic import BaseModel
from datetime import datetime


class NotificationSchema(BaseModel):
    id: int
    member_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
