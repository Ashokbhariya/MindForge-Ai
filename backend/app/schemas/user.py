import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr
    career_goal: str | None = None

class UserCreate(UserBase):
    password_hash: str

class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
