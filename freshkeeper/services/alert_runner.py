# freshkeeper/services/alert_runner.py
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Kinds (doivent correspondre au CHECK de la table alerts)
ALERT_EXPIRED = "EXPIRED"
ALERT_SOON = "SOON"
ALERT_OUT_OF_STOCK = "OUT_OF_STOCK"

# Fenêtre "bientôt expiré"
EXPIRE_SOON_DAYS = 3


def run_scan() -> Dict[str, Any]:
    """
    Scan les produits et UPSERT des alertes en base.

    Règles:
      - OUT_OF_STOCK : quantity <= 0            -> due_date = today (UTC)
      - EXPIRED      : expiry_date <= today     -> due_date = expiry_date
      - SOON         : today < expiry_date <= today + EXPIRE_SOON_DAYS -> due_date = expiry_date

    Retourne un récap dict: {"status","created","updated","errors","checked"}.
    """
    try:
        # On utilise la Session SQLAlchemy déjà configurée par l'app
        from sqlalchemy import text
        from sqlalchemy.exc import SQLAlchemyError

        from freshkeeper.database import SessionLocal
    except Exception as e:
        logger.exception(
            "Imports indispensables introuvables (database/SQLAlchemy): %s", e
        )
        return {
            "status": "error",
            "errors": 1,
            "reason": "imports",
            "checked": 0,
            "created": 0,
            "updated": 0,
        }

    today_utc: date = datetime.utcnow().date()
    soon_threshold: date = today_utc + timedelta(days=EXPIRE_SOON_DAYS)

    created = 0
    updated = 0
    errors = 0
    checked = 0

    logger.info(
        "alert-runner v4 (full-raw-sql) chargé depuis: %s",
        __file__,
    )

    with SessionLocal() as db:
        try:
            # Récupération minimale (évite les soucis d'ORM)
            rows = db.execute(
                text("SELECT id, quantity, expiry_date FROM products ORDER BY id")
            ).all()
            products: List[Tuple[int, Optional[int], Optional[date]]] = [
                (r[0], r[1], r[2]) for r in rows
            ]
        except SQLAlchemyError as e:
            logger.exception("Échec du chargement des produits: %s", e)
            return {
                "status": "error",
                "errors": 1,
                "checked": 0,
                "created": 0,
                "updated": 0,
            }

        logger.info(
            "SCAN start: %s products (today=%s, soon<=%s)",
            len(products),
            today_utc,
            soon_threshold,
        )

        # SQL préparés
        insert_sql = text(
            """
            INSERT INTO alerts (product_id, kind, due_date, message, is_active)
            VALUES (:pid, :kind, :due_date, :message, TRUE)
            ON CONFLICT (product_id, kind, due_date) DO NOTHING
            RETURNING id;
        """
        )

        update_sql = text(
            """
            UPDATE alerts
               SET message    = :message,
                   is_active  = TRUE,
                   updated_at = now()
             WHERE product_id = :pid
               AND kind       = :kind
               AND due_date   = :due_date
            RETURNING id;
        """
        )

        # Optionnel : on désactive d'anciennes versions du même "kind" si la due_date a changé
        # (utile si une date d'expiration évolue)
        deactivate_others_sql = text(
            """
            UPDATE alerts
               SET is_active  = FALSE,
                   updated_at = now()
             WHERE product_id = :pid
               AND kind       = :kind
               AND due_date  <> :due_date
               AND is_active  = TRUE;
        """
        )

        for pid, qty, exp in products:
            checked += 1
            # Normalisation types
            try:
                qty_val = int(qty) if qty is not None else None
            except Exception:
                qty_val = None

            exp_val: Optional[date] = exp  # déjà un date en SQL

            alerts: List[Tuple[str, date]] = []

            # OUT_OF_STOCK
            if qty_val is not None and qty_val <= 0:
                alerts.append((ALERT_OUT_OF_STOCK, today_utc))

            # EXPIRED / SOON
            if exp_val is not None:
                if exp_val <= today_utc:
                    alerts.append((ALERT_EXPIRED, exp_val))
                elif today_utc < exp_val <= soon_threshold:
                    alerts.append((ALERT_SOON, exp_val))

            logger.info(
                "SCAN p_id=%s qty=%s exp=%s -> alerts=%s", pid, qty_val, exp_val, alerts
            )

            for kind, due_date in alerts:
                try:
                    message = f"{kind} for product #{pid} on {due_date}"

                    # 1) tentative INSERT
                    new_id = db.execute(
                        insert_sql,
                        {
                            "pid": pid,
                            "kind": kind,
                            "due_date": due_date,
                            "message": message,
                        },
                    ).scalar_one_or_none()

                    if new_id is not None:
                        created += 1
                        logger.info(
                            "CREATED alert product_id=%s kind=%s due_date=%s (id=%s)",
                            pid,
                            kind,
                            due_date,
                            new_id,
                        )
                    else:
                        # 2) sinon UPDATE
                        upd_id = db.execute(
                            update_sql,
                            {
                                "pid": pid,
                                "kind": kind,
                                "due_date": due_date,
                                "message": message,
                            },
                        ).scalar_one_or_none()

                        if upd_id is not None:
                            updated += 1
                            logger.info(
                                "UPDATED alert product_id=%s kind=%s due_date=%s (id=%s)",
                                pid,
                                kind,
                                due_date,
                                upd_id,
                            )
                        else:
                            # Cas improbable si quelqu’un a modifié la contrainte pendant la course
                            errors += 1
                            logger.error(
                                "UPSERT manqué product_id=%s kind=%s due_date=%s (aucun row affecté)",
                                pid,
                                kind,
                                due_date,
                            )

                    # 3) (optionnel) désactiver les autres alertes actives du même kind pour ce produit
                    db.execute(
                        deactivate_others_sql,
                        {"pid": pid, "kind": kind, "due_date": due_date},
                    )

                except SQLAlchemyError:
                    errors += 1
                    logger.exception(
                        "Erreur sur alert UPSERT product_id=%s kind=%s due_date=%s",
                        pid,
                        kind,
                        due_date,
                    )

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Commit échoué — rollback effectué")
            return {
                "status": "error",
                "errors": errors + 1,
                "checked": checked,
                "created": created,
                "updated": updated,
            }

    status = "ok" if errors == 0 else "partial"
    return {
        "status": status,
        "created": created,
        "updated": updated,
        "errors": errors,
        "checked": checked,
    }
