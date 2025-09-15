# app/routers/alerts.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from freshkeeper.dependencies import get_db
from freshkeeper.schemas.alerts import AlertAckOut, AlertCreate, AlertKind, AlertOut
from freshkeeper.services.alerts import ack_alert, create_alert, list_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertOut])
def get_alerts(
    kind: AlertKind | None = Query(default=None),
    ack: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_alerts(db, kind=kind, ack=ack)


@router.post("/", response_model=AlertOut, status_code=201)
def post_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    return create_alert(db, payload)


@router.post("/{alert_id}/ack", response_model=AlertAckOut)
def post_alert_ack(alert_id: int, db: Session = Depends(get_db)):
    try:
        alert = ack_alert(db, alert_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"id": alert.id, "is_ack": alert.is_ack}
