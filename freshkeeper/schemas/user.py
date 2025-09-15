from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
