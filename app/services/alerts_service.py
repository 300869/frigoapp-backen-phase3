import enum
from datetime import date, timedelta

from app import models


def compute_kind(
    expiry_date: date | None,
    quantity: int,
    soon_days: int = 3,
    low_stock_threshold: int = 1,
):
    if quantity <= low_stock_threshold:
        return "STOCK_BAS"
    if expiry_date is None:
        return None
    today = date.today()
    if expiry_date < today:
        return "PERIME"
    if expiry_date <= today + timedelta(days=soon_days):
        return "BIENTOT"
    return None


def _to_kind_enum(kind) -> models.AlertKind:
    if isinstance(kind, models.AlertKind):
        return kind
    if isinstance(kind, enum.Enum):
        return models.AlertKind(kind.value)
    if isinstance(kind, str):
        return models.AlertKind(kind)
    raise ValueError("kind invalide")


def ensure_open_alert(db, *, product_id: int, kind, due_at: date | None = None):
    kind_enum = _to_kind_enum(kind)

    existing = (
        db.query(models.Alert)
        .filter(
            models.Alert.product_id == product_id,
            models.Alert.kind == kind_enum,
            models.Alert.status == models.AlertStatus.OPEN,
        )
        .first()
    )
    if existing:
        if due_at is not None:
            existing.due_at = due_at
        db.commit()
        db.refresh(existing)
        return existing

    obj = models.Alert(
        product_id=product_id,
        kind=kind_enum,
        status=models.AlertStatus.OPEN,
        due_at=due_at,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def close_alerts(db, *, product_id: int, kinds: list[str] | list[models.AlertKind]):
    to_close = []
    for k in kinds:
        try:
            to_close.append(_to_kind_enum(k))
        except Exception:
            continue
    if not to_close:
        return 0
    q = db.query(models.Alert).filter(
        models.Alert.product_id == product_id,
        models.Alert.kind.in_(to_close),
        models.Alert.status == models.AlertStatus.OPEN,
    )
    n = 0
    for a in q:
        a.status = models.AlertStatus.DONE
        n += 1
    db.commit()
    return n


from typing import Iterable

from app import models


def close_alerts(
    db, *, product_id: int, kinds: Iterable[str] | Iterable[models.AlertKind]
):
    """Passe à DONE toutes les alertes OPEN du produit pour les kinds donnés."""
    # normalise en enums
    normalized: list[models.AlertKind] = []
    for k in kinds:
        try:
            if isinstance(k, models.AlertKind):
                normalized.append(k)
            else:
                normalized.append(
                    models.AlertKind[k]
                    if isinstance(k, str) and k in models.AlertKind.__members__
                    else models.AlertKind(k)
                )
        except Exception:
            continue
    if not normalized:
        return 0

    q = db.query(models.Alert).filter(
        models.Alert.product_id == product_id,
        models.Alert.kind.in_(normalized),
        models.Alert.status == models.AlertStatus.OPEN,
    )
    n = 0
    for a in q:
        a.status = models.AlertStatus.DONE
        n += 1
    db.commit()
    return n


from typing import Iterable

from app import models


def close_alerts(
    db, *, product_id: int, kinds: Iterable[str] | Iterable[models.AlertKind]
):
    """Passe à DONE toutes les alertes OPEN du produit pour les kinds donnés."""
    # normalise en enums
    normalized: list[models.AlertKind] = []
    for k in kinds:
        try:
            if isinstance(k, models.AlertKind):
                normalized.append(k)
            else:
                normalized.append(
                    models.AlertKind[k]
                    if isinstance(k, str) and k in models.AlertKind.__members__
                    else models.AlertKind(k)
                )
        except Exception:
            continue
    if not normalized:
        return 0

    q = db.query(models.Alert).filter(
        models.Alert.product_id == product_id,
        models.Alert.kind.in_(normalized),
        models.Alert.status == models.AlertStatus.OPEN,
    )
    n = 0
    for a in q:
        a.status = models.AlertStatus.DONE
        n += 1
    db.commit()
    return n
