import asyncio
import importlib
import os
import sys
from pathlib import Path

# --- Ajouter la racine du projet au sys.path ---
HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[1]  # ...\freshkeeper-backend-phase3
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- Import via 'freshkeeper', fallback 'app' si besoin ---
pkg_name = "freshkeeper"
try:
    database = importlib.import_module(f"{pkg_name}.database")
    alert_runner = importlib.import_module(f"{pkg_name}.services.alert_runner")
except ModuleNotFoundError:
    pkg_name = "app"
    database = importlib.import_module(f"{pkg_name}.database")
    alert_runner = importlib.import_module(f"{pkg_name}.services.alert_runner")

run_scan = getattr(alert_runner, "run_scan")


def main():
    result = run_scan()
    if asyncio.iscoroutine(result):
        asyncio.run(result)


if __name__ == "__main__":
    main()
