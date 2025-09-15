# app/services/alerts.py
from sqlalchemy import select
from sqlalchemy.orm import Session

from freshkeeper.models.alert import Alert
from freshkeeper.schemas.alerts import AlertCreate, AlertKind


def list_alerts(db: Session, *, kind: AlertKind | None = None, ack: bool | None = None):
    stmt = select(Alert)
    if kind is not None:
        stmt = stmt.where(Alert.kind == kind.value)  # stored as string
    if ack is not None:
        stmt = stmt.where(Alert.is_ack == ack)
    return list(db.execute(stmt).scalars().all())


def create_alert(db: Session, payload: AlertCreate) -> Alert:
    alert = Alert(
        product_id=payload.product_id,
        kind=payload.kind.value,  # stored as string
        message=payload.message,
        due_date=payload.due_date,
        is_ack=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def ack_alert(db: Session, alert_id: int) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise ValueError("Alert not found")
    alert.is_ack = True
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
