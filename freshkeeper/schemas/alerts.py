from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AlertKind(str, Enum):
    EXPIRED = "EXPIRED"
    SOON = "SOON"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class AlertCreate(BaseModel):
    product_id: int = Field(gt=0)
    kind: AlertKind  # entrée stricte
    message: str = Field(min_length=1, max_length=300)
    due_date: date | None = None


class AlertOut(BaseModel):
    id: int
    product_id: int
    kind: str  # sortie relaxée
    message: str
    due_date: date | None = None
    is_ack: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2


class AlertAckOut(BaseModel):
    id: int
    is_ack: bool
    model_config = ConfigDict(from_attributes=True)
