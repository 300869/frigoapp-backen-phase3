from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    category_id: Optional[int] = None
    quantity: int = Field(default=0, ge=0)
    location: Optional[str] = None
    expiration_date: Optional[date] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    location: Optional[str] = None
    expiration_date: Optional[date] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
