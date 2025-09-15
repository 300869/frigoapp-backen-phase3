from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from freshkeeper.models.alert import Alert
from freshkeeper.schemas.alerts import (
    AlertAckOut,
    AlertCreate,
    AlertKind,
    AlertOut,
)


def _as_str_kind(v) -> str:
    # Tolère Enum ou str
    try:
        return v.value  # Enum -> "SOON"
    except AttributeError:
        return str(v)


def list_alerts(
    db: Session,
    *,
    kind: AlertKind | str | None = None,
    ack: bool | None = None,
) -> list[AlertOut]:
    stmt = select(Alert)
    if kind is not None:
        stmt = stmt.where(Alert.kind == _as_str_kind(kind))
    if ack is not None:
        stmt = stmt.where(Alert.is_ack == ack)

    # Barrière anti-données foireuses (sécurité)
    stmt = stmt.where(Alert.message.isnot(None), Alert.message != "")

    rows = db.execute(stmt).scalars().all()

    # Normalise en Pydantic -> évite toute surprise à la sérialisation
    out: list[AlertOut] = []
    for a in rows:
        try:
            out.append(AlertOut.model_validate(a))
        except Exception:
            # on ignore la ligne problématique plutôt que de planter tout le GET
            continue
    return out


def create_alert(db: Session, payload: AlertCreate) -> AlertOut:
    alert = Alert(
        product_id=payload.product_id,
        kind=_as_str_kind(payload.kind),
        message=payload.message,
        due_date=payload.due_date,
        is_ack=False,
    )
    db.add(alert)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(alert)
    return AlertOut.model_validate(alert)


def ack_alert(db: Session, alert_id: int) -> AlertAckOut:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise ValueError("Alert not found")
    alert.is_ack = True
    db.add(alert)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(alert)
    return AlertAckOut.model_validate(alert)
