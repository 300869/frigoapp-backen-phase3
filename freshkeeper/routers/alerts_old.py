# freshkeeper/routers/alerts.py
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()  # <-- PAS de prefix ici


# --- DB session dependency ---
def _get_db_dep():
    try:
        # Si tu as déjà un get_db centralisé, on le réutilise
        from freshkeeper.dependencies import get_db  # type: ignore

        return get_db
    except Exception:
        # Fallback simple basé sur SessionLocal
        from freshkeeper.database import SessionLocal  # type: ignore

        def _get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        return _get_db


get_db = _get_db_dep()

# --- Model Alert ---
from freshkeeper.models.alert import Alert  # type: ignore


# --- Pydantic schemas ---
class AlertOut(BaseModel):
    id: int
    product_id: int
    kind: str
    due_date: Optional[date] = None
    is_ack: Optional[bool] = None
    message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # pydantic v2


class AckIn(BaseModel):
    is_ack: bool = True


def _order_expr(order: str):
    return Alert.id.asc() if order.lower() == "asc" else Alert.id.desc()


# --- Routes ---
@router.get("/", response_model=List[AlertOut])
def list_alerts(
    kind: Optional[str] = Query(default=None),
    only_today: bool = Query(default=False),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    is_ack: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    order: str = Query(default="desc", pattern="^(?i)(asc|desc)$"),
    db: Session = Depends(get_db),
):
    q = db.query(Alert)

    if kind:
        q = q.filter(Alert.kind == kind)
    if only_today:
        q = q.filter(Alert.due_date == date.today())
    else:
        if date_from:
            q = q.filter(Alert.due_date >= date_from)
        if date_to:
            q = q.filter(Alert.due_date <= date_to)
    if is_ack is not None and hasattr(Alert, "is_ack"):
        q = q.filter(Alert.is_ack == is_ack)

    rows = q.order_by(_order_expr(order)).offset(offset).limit(limit).all()
    return rows


@router.get("/today", response_model=List[AlertOut])
def list_today_alerts(
    kind: Optional[str] = Query(default=None),
    is_ack: Optional[bool] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    order: str = Query(default="desc", pattern="^(?i)(asc|desc)$"),
    db: Session = Depends(get_db),
):
    return list_alerts(
        kind=kind,
        only_today=True,
        date_from=None,
        date_to=None,
        is_ack=is_ack,
        limit=limit,
        offset=offset,
        order=order,
        db=db,
    )


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    obj = db.get(Alert, alert_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Alert not found")
    return obj


@router.patch("/{alert_id}/ack", response_model=AlertOut)
def ack_alert(alert_id: int, body: AckIn, db: Session = Depends(get_db)):
    obj = db.get(Alert, alert_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Alert not found")
    if not hasattr(Alert, "is_ack"):
        raise HTTPException(status_code=400, detail="This model has no 'is_ack' column")
    obj.is_ack = body.is_ack
    if hasattr(Alert, "updated_at"):
        obj.updated_at = datetime.utcnow()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    obj = db.get(Alert, alert_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(obj)
    db.commit()
    return None
