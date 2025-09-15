from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
except ImportError:
    from .database import SessionLocal

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/alerts/scan")
def scan_alerts(db: Session = Depends(get_db)):
    # 1) Expirés (red)
    sql_expired = text(
        """
        INSERT INTO alerts (product_id, lot_id, kind, due_date, message, is_active)
        SELECT p.id, l.id, 'expiry', l.expiry_date,
               'Périmé: ' || p.name || ' le ' || to_char(l.expiry_date,'YYYY-MM-DD'),
               TRUE
        FROM lots l
        JOIN products p ON p.id = l.product_id
        WHERE l.expiry_date IS NOT NULL
          AND l.expiry_date < CURRENT_DATE
          AND l.quantity > 0
        ON CONFLICT (product_id, kind, due_date)
        DO UPDATE SET is_active = EXCLUDED.is_active,
                      message   = EXCLUDED.message,
                      updated_at = now();
    """
    )
    db.execute(sql_expired)

    # 2) Bientôt (yellow) J0..J+3
    sql_soon = text(
        """
        INSERT INTO alerts (product_id, lot_id, kind, due_date, message, is_active)
        SELECT p.id, l.id, 'soon', l.expiry_date,
               'Bientôt: ' || p.name || ' le ' || to_char(l.expiry_date,'YYYY-MM-DD'),
               TRUE
        FROM lots l
        JOIN products p ON p.id = l.product_id
        WHERE l.expiry_date IS NOT NULL
          AND l.expiry_date >= CURRENT_DATE
          AND l.expiry_date <= CURRENT_DATE + INTERVAL '3 days'
          AND l.quantity > 0
        ON CONFLICT (product_id, kind, due_date)
        DO UPDATE SET is_active = EXCLUDED.is_active,
                      message   = EXCLUDED.message,
                      updated_at = now();
    """
    )
    db.execute(sql_soon)

    # 3) Désactivation des alertes qui ne sont plus valides
    sql_cleanup = text(
        """
        UPDATE alerts a
        SET is_active = FALSE, updated_at = now()
        WHERE a.kind IN ('expiry','soon')
          AND NOT EXISTS (
            SELECT 1
            FROM lots l
            WHERE l.product_id = a.product_id
              AND l.id = COALESCE(a.lot_id, l.id)
              AND l.quantity > 0
              AND (
                    (a.kind = 'expiry' AND l.expiry_date IS NOT NULL AND l.expiry_date < CURRENT_DATE)
                 OR (a.kind = 'soon'   AND l.expiry_date IS NOT NULL AND l.expiry_date >= CURRENT_DATE
                                        AND l.expiry_date <= CURRENT_DATE + INTERVAL '3 days')
              )
          );
    """
    )
    res = db.execute(sql_cleanup)
    db.commit()
    return {"ok": True}


@router.post("/reco/refresh")
def refresh_recos(db: Session = Depends(get_db)):
    # Non CONCURRENTLY pour rester universel
    db.execute(text("REFRESH MATERIALIZED VIEW mv_suggested_purchases;"))
    db.commit()
    return {"ok": True}
