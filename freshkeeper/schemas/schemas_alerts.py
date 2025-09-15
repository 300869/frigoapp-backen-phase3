# app/schemas/alerts.py
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertKind(str, Enum):
    EXPIRED = "EXPIRED"
    SOON = "SOON"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class AlertBase(BaseModel):
    product_id: int = Field(gt=0)
    kind: AlertKind
    message: str = Field(min_length=1, max_length=300)
    due_date: date | None = None


class AlertCreate(AlertBase):
    pass


class AlertOut(AlertBase):
    id: int
    is_ack: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2


class AlertAckOut(BaseModel):
    id: int
    is_ack: bool
