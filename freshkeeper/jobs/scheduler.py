from __future__ import annotations

import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
_SCHEDULER_SINGLETON: BackgroundScheduler | None = None  # singleton local


def is_scheduler_enabled() -> bool:
    return os.getenv("ENABLE_SCHEDULER", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "y",
        "on",
    )


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def _get_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in (
        "1",
        "true",
        "yes",
        "y",
        "on",
    )


def build_scheduler() -> BackgroundScheduler:
    """
    Construit un BackgroundScheduler avec le job run_scan.
    """
    global _SCHEDULER_SINGLETON
    if _SCHEDULER_SINGLETON:
        return _SCHEDULER_SINGLETON

    # import tardif pour éviter les cycles
    from freshkeeper.services.alert_runner import run_scan

    interval_minutes = _get_int("SCAN_INTERVAL_MINUTES", 15)
    run_at_startup = _get_bool("SCAN_RUN_AT_STARTUP", True)
    tz = os.getenv("TZ", "UTC")

    scheduler = BackgroundScheduler(timezone=tz)
    scheduler.add_job(
        func=run_scan,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="alerts_scan_job",
        name=f"Scan alerts every {interval_minutes} min",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    if run_at_startup:
        try:
            logger.info("Exécution run_scan au démarrage…")
            logger.setLevel(logging.INFO)
            run_scan()
            logger.info("run_scan exécuté au démarrage")
        except Exception:
            logger.exception("Erreur lors de run_scan au démarrage")

    _SCHEDULER_SINGLETON = scheduler
    return scheduler


def get_scheduler() -> BackgroundScheduler | None:
    return _SCHEDULER_SINGLETON
