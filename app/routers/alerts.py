from datetime import date
from typing import Optional
import enum

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/alerts", tags=["alerts"])

# --- helpers de conversion (strings -> enums du modèle) ----------------------
def _to_status(value: Optional[str]) -> Optional[models.AlertStatus]:
    if value is None:
        return None
    try:
        return models.AlertStatus(value)
    except ValueError:
        raise HTTPException(422, detail="status invalide (OPEN ou DONE)")

def _to_kind(value: Optional[str]) -> Optional[models.AlertKind]:
    if value is None:
        return None
    try:
        return models.AlertKind(value)
    except ValueError:
        raise HTTPException(422, detail="kind invalide (PERIME, BIENTOT, STOCK_BAS)")

# --- créer une alerte manuellement (optionnel, pour tests) -------------------
@router.post("", response_model=schemas.AlertRead, status_code=201)
def create_alert(payload: schemas.AlertCreate, db: Session = Depends(get_db)):
    prod = db.get(models.Product, payload.product_id)
    if not prod:
        raise HTTPException(422, detail="product_id invalide")

    kind_enum = _to_kind(payload.kind if isinstance(payload.kind, str) else str(payload.kind))
    status_enum = _to_status(payload.status if isinstance(payload.status, str) else str(payload.status))

    obj = models.Alert(
        product_id=payload.product_id,
        kind=kind_enum,
        status=status_enum,
        due_at=payload.due_at,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# --- lister les alertes (safe pour SQLite/Postgres + sérialisation manuelle) --
@router.get("")  # volontairement sans response_model pour éviter toute friction
def list_alerts(
    status: Optional[str] = Query(None, description="OPEN ou DONE"),
    kind: Optional[str] = Query(None, description="PERIME, BIENTOT, STOCK_BAS"),
    due_before: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(models.Alert)

        s = _to_status(status)
        if s is not None:
            q = q.filter(models.Alert.status == s)

        k = _to_kind(kind)
        if k is not None:
            q = q.filter(models.Alert.kind == k)

        if due_before is not None:
            q = q.filter(models.Alert.due_at.isnot(None), models.Alert.due_at <= due_before)

        # Tri compatible SQLite: place les NULL en dernier, puis date croissante
        q = q.order_by(models.Alert.due_at.is_(None), models.Alert.due_at.asc())

        rows = q.all()

        # Sérialisation manuelle -> dict (évite toute friction Pydantic/Enum)
        out = []
        for a in rows:
            out.append({
                "id": a.id,
                "product_id": a.product_id,
                "kind": a.kind.value if isinstance(a.kind, enum.Enum) else str(a.kind),
                "status": a.status.value if isinstance(a.status, enum.Enum) else str(a.status),
                "due_at": a.due_at.isoformat() if a.due_at else None,
            })
        return out

    except SQLAlchemyError as e:
        # Message d’erreur clair au lieu d’un 500 silencieux
        raise HTTPException(500, detail=f"Erreur base de données: {e.__class__.__name__}")
