from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

RETENTION_DAYS_DEFAULT = 30  # ajuste si besoin


def ack_alerts(db: Session, alert_ids: Iterable[int]) -> int:
    """ACK en masse via SQL direct (pas d'accès au modèle)."""
    ids = list(alert_ids)
    if not ids:
        return 0
    now = datetime.now(timezone.utc)
    sql = text(
        """
        UPDATE alerts
           SET is_ack = TRUE,
               updated_at = :now
         WHERE id = ANY(:ids)
    """
    )
    res = db.execute(sql, {"now": now, "ids": ids})
    db.commit()
    return res.rowcount or 0


def ack_all_for_product(db: Session, product_id: int) -> int:
    now = datetime.now(timezone.utc)
    sql = text(
        """
        UPDATE alerts
           SET is_ack = TRUE,
               updated_at = :now
         WHERE product_id = :pid
    """
    )
    res = db.execute(sql, {"now": now, "pid": product_id})
    db.commit()
    return res.rowcount or 0


def soft_delete_old_alerts(db: Session, retention_days: Optional[int] = None) -> int:
    """
    'Soft delete' sans nouvelle colonne: on passe is_active = FALSE pour les alertes trop anciennes.
    Critère d'ancienneté: created_at < now - retention_days.
    """
    days = retention_days or RETENTION_DAYS_DEFAULT
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    sql = text(
        """
        UPDATE alerts
           SET is_active = FALSE,
               updated_at = :now
         WHERE due_date < :cutoff
           AND is_active = TRUE
    """
    )
    res = db.execute(sql, {"now": now, "cutoff": cutoff})
    db.commit()
    return res.rowcount or 0


def hard_purge_soft_deleted(db: Session, older_than_days: int = 7) -> int:
    """
    Purge physique (optionnelle) : supprime les alertes déjà inactives et très anciennes.
    Si tu ne veux jamais supprimer, retourne 0.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    sql = text(
        """
        DELETE FROM alerts
         WHERE is_active = FALSE
           AND created_at < :cutoff
    """
    )
    res = db.execute(sql, {"cutoff": cutoff})
    db.commit()
    return res.rowcount or 0


def run_retention(db: Session, retention_days: Optional[int] = None) -> dict:
    soft = soft_delete_old_alerts(db, retention_days=retention_days)
    purged = hard_purge_soft_deleted(db, older_than_days=7)
    return {"soft_deleted": soft, "purged": purged}
