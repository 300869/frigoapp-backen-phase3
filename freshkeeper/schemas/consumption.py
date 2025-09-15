from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsumptionCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=16)
    consumed_at: datetime | None = None  # si None, on mettra "maintenant" côté service


class ConsumptionOut(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit: str
    consumed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2
