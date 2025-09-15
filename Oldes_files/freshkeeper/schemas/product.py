from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    default_shelf_life_days: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    default_shelf_life_days: Optional[int] = None


class ProductRead(BaseModel):
    id: int
    name: str
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    default_shelf_life_days: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # permet de renvoyer un modèle SQLAlchemy directement
