import importlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import via freshkeeper, fallback app si besoin
pkg = "freshkeeper"
try:
    db_mod = importlib.import_module(f"{pkg}.database")
    maint = importlib.import_module(f"{pkg}.services.alert_maintenance")
except ModuleNotFoundError:
    pkg = "app"
    db_mod = importlib.import_module(f"{pkg}.database")
    maint = importlib.import_module(f"{pkg}.services.alert_maintenance")

SessionLocal = getattr(db_mod, "SessionLocal")
run_retention = getattr(maint, "run_retention")


def main():
    db = SessionLocal()
    try:
        out = run_retention(
            db, retention_days=None
        )  # None => valeur par défaut dans le service
        print("[retention]", out)
    finally:
        db.close()


if __name__ == "__main__":
    main()
