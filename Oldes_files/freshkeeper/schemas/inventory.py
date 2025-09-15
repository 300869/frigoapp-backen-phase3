from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)
    expires_at: Optional[date] = None
    note: Optional[str] = None


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=0)
    expires_at: Optional[date] = None
    note: Optional[str] = None


class InventoryRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    added_at: datetime
    expires_at: Optional[date] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True
