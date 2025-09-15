from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel

AlertKind = Literal["PERIME", "BIENTOT", "STOCK_BAS"]
AlertStatus = Literal["OPEN", "DONE"]


class AlertBase(BaseModel):
    product_id: int
    kind: AlertKind
    status: AlertStatus
    due_at: Optional[date] = None


class AlertCreate(AlertBase):
    created_at: Optional[datetime] = None


class AlertRead(AlertBase):
    id: int
    created_at: datetime

    # Pydantic v2: remplace l'ancien Config(orm_mode=True)
    model_config = {"from_attributes": True}
