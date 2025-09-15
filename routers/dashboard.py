from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, condecimal
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
except ImportError:
    from .database import SessionLocal

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ---------- Models ----------
class Summary(BaseModel):
    total_products: int
    total_lots: int
    expired_count: int
    soon_count: int
    green_count: int
    need_to_buy_count: int
    nearest_expiry: Optional[str] = None  # ISO date


class ExpiringItem(BaseModel):
    lot_id: int
    product_id: int
    product_name: str
    quantity: condecimal(max_digits=12, decimal_places=3)
    unit: Optional[str] = None
    expiry_date: Optional[str] = None
    storage_location_id: int
    status_color: str


class RecoItem(BaseModel):
    product_id: int
    name: str
    suggested_qty: condecimal(max_digits=12, decimal_places=3)


# ---------- DB session ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Endpoints ----------
@router.get("/summary", response_model=Summary)
def get_summary(db: Session = Depends(get_db)):
    row = (
        db.execute(
            text(
                """
        SELECT
          (SELECT COUNT(*) FROM products)                                        AS total_products,
          (SELECT COUNT(*) FROM lots)                                            AS total_lots,
          (SELECT COUNT(*) FROM v_lot_status WHERE status_color='red')           AS expired_count,
          (SELECT COUNT(*) FROM v_lot_status WHERE status_color='yellow')        AS soon_count,
          (SELECT COUNT(*) FROM v_lot_status WHERE status_color='green')         AS green_count,
          (SELECT COUNT(*) FROM mv_suggested_purchases WHERE suggested_qty>0)    AS need_to_buy_count,
          (SELECT MIN(expiry_date)::text FROM lots WHERE expiry_date IS NOT NULL) AS nearest_expiry
    """
            )
        )
        .mappings()
        .first()
    )
    return row


@router.get("/expiring", response_model=List[ExpiringItem])
def get_expiring(days: int = Query(7, ge=0, le=90), db: Session = Depends(get_db)):
    # filtre: DLU <= J+days
    rows = (
        db.execute(
            text(
                """
        SELECT
          l.id     AS lot_id,
          p.id     AS product_id,
          p.name   AS product_name,
          l.quantity, l.unit,
          l.expiry_date::text AS expiry_date,
          l.storage_location_id,
          CASE
            WHEN l.expiry_date IS NULL THEN 'green'
            WHEN l.expiry_date < CURRENT_DATE THEN 'red'
            WHEN l.expiry_date <= CURRENT_DATE + (:days || ' days')::interval THEN 'yellow'
            ELSE 'green'
          END AS status_color
        FROM lots l
        JOIN products p ON p.id = l.product_id
        WHERE l.expiry_date IS NOT NULL
          AND l.expiry_date <= (CURRENT_DATE + (:days || ' days')::interval)
        ORDER BY
          CASE
            WHEN l.expiry_date < CURRENT_DATE THEN 0
            WHEN l.expiry_date <= CURRENT_DATE + (:days || ' days')::interval THEN 1
            ELSE 2
          END,
          l.expiry_date ASC, l.id ASC
    """
            ),
            {"days": days},
        )
        .mappings()
        .all()
    )
    return rows


@router.get("/replenishments", response_model=List[RecoItem])
def get_replenishments(
    limit: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)
):
    rows = (
        db.execute(
            text(
                """
        SELECT product_id, name, suggested_qty
        FROM mv_suggested_purchases
        WHERE suggested_qty > 0
        ORDER BY suggested_qty DESC, name ASC
        LIMIT :limit
    """
            ),
            {"limit": limit},
        )
        .mappings()
        .all()
    )
    return rows
