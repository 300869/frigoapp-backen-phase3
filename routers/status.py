from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, condecimal
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
except ImportError:
    from .database import SessionLocal

router = APIRouter(prefix="/lots", tags=["lots-status"])


class LotStatus(BaseModel):
    id: int
    product_id: int
    quantity: condecimal(max_digits=12, decimal_places=3)
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    storage_location_id: int
    status_color: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/status", response_model=List[LotStatus])
def get_lot_status(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            text(
                """
        SELECT l.id, l.product_id, l.quantity, l.unit, l.expiry_date, l.storage_location_id, s.status_color
        FROM v_lot_status s
        JOIN lots l ON l.id = s.id
        ORDER BY
          CASE s.status_color WHEN 'red' THEN 0 WHEN 'yellow' THEN 1 ELSE 2 END,
          COALESCE(l.expiry_date, DATE '9999-12-31'), l.id
    """
            )
        )
        .mappings()
        .all()
    )
    return rows
