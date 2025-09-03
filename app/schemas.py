from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

# ---------- Categories ----------
class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)

class CategoryRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2


# ---------- Products ----------
class ProductCreate(BaseModel):
    name: str
    category_id: int
    quantity: int = Field(ge=0)
    location: str
    expiry_date: Optional[date] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    location: Optional[str] = None
    expiry_date: Optional[date] = None

class ProductRead(BaseModel):
    id: int
    name: str
    category_id: Optional[int] = None
    quantity: int
    location: Optional[str] = None
    expiry_date: Optional[date] = None
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2


# ---------- Alerts ----------
AlertKind = Literal["PERIME", "BIENTOT", "STOCK_BAS"]
AlertStatus = Literal["OPEN", "DONE"]

class AlertCreate(BaseModel):
    product_id: int
    kind: AlertKind
    status: AlertStatus = "OPEN"
    due_at: Optional[date] = None

class AlertUpdate(BaseModel):
    kind: Optional[AlertKind] = None
    status: Optional[AlertStatus] = None
    due_at: Optional[date] = None

class AlertRead(BaseModel):
    id: int
    product_id: int
    kind: AlertKind
    status: AlertStatus
    due_at: Optional[date] = None
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2
