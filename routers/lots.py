from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
except ImportError:
    from .database import SessionLocal

router = APIRouter(prefix="/lots", tags=["lots"])


class LotUpsert(BaseModel):
    product_id: int
    quantity: condecimal(max_digits=12, decimal_places=3)
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    storage_location_id: int


class LotRead(BaseModel):
    id: int
    product_id: int
    quantity: condecimal(max_digits=12, decimal_places=3)
    unit: Optional[str] = None
    expiry_date: Optional[date] = None
    storage_location_id: int

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=LotRead)
def upsert_lot(payload: LotUpsert, db: Session = Depends(get_db)):
    # Merge key uses generated column unit_norm, so unit NULL/'' behave the same
    sql = text(
        """
        INSERT INTO lots (product_id, quantity, unit, expiry_date, storage_location_id)
        VALUES (:product_id, :quantity, :unit, :expiry_date, :storage_location_id)
        ON CONFLICT (product_id, expiry_date, storage_location_id, unit_norm)
        DO UPDATE SET quantity = lots.quantity + EXCLUDED.quantity,
                      updated_at = now()
        RETURNING id, product_id, quantity, unit, expiry_date, storage_location_id
    """
    )
    row = db.execute(sql, payload.model_dump()).mappings().first()
    db.commit()
    return row


@router.get("", response_model=List[LotRead])
def list_lots(
    product_id: Optional[int] = None,
    storage_location_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    conds = []
    params = {}
    if product_id is not None:
        conds.append("product_id = :product_id")
        params["product_id"] = product_id
    if storage_location_id is not None:
        conds.append("storage_location_id = :storage_location_id")
        params["storage_location_id"] = storage_location_id
    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    sql = text(
        f"""
        SELECT id, product_id, quantity, unit, expiry_date, storage_location_id
        FROM lots
        {where}
        ORDER BY COALESCE(expiry_date, DATE '9999-12-31') ASC, id ASC
    """
    )
    rows = db.execute(sql, params).mappings().all()
    return rows
