from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertOut(BaseModel):
    id: int
    product_id: int
    kind: str
    due_date: Optional[date] = None
    message: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    lot_id: Optional[int] = None

    class Config:
        from_attributes = True


class AlertPatch(BaseModel):
    is_active: Optional[bool] = None
    message: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[AlertOut])
def list_alerts(
    kind: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    due_from: Optional[date] = Query(None),
    due_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    conds, params = [], {}
    if kind is not None:
        conds.append("kind = :kind")
        params["kind"] = kind.lower()
    if is_active is not None:
        conds.append("is_active = :is_active")
        params["is_active"] = is_active
    if due_from is not None:
        conds.append("due_date >= :due_from")
        params["due_from"] = due_from
    if due_to is not None:
        conds.append("due_date <= :due_to")
        params["due_to"] = due_to

    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    sql = text(
        f"""
        SELECT id, product_id, kind, due_date, message, is_active, created_at, updated_at, lot_id
        FROM alerts
        {where}
        ORDER BY due_date NULLS LAST, id
    """
    )
    rows = db.execute(sql, params).mappings().all()
    return rows


@router.patch("/{alert_id}", response_model=AlertOut)
def update_alert(alert_id: int, payload: AlertPatch, db: Session = Depends(get_db)):
    row = (
        db.execute(
            text(
                """
            UPDATE alerts
            SET
              is_active  = COALESCE(:is_active, is_active),
              message    = COALESCE(:message, message),
              updated_at = now()
            WHERE id = :id
            RETURNING id, product_id, kind, due_date::date AS due_date, message,
                      is_active, created_at, updated_at, lot_id
        """
            ),
            {
                "id": alert_id,
                "is_active": payload.is_active,
                "message": payload.message,
            },
        )
        .mappings()
        .first()
    )

    db.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    return row
