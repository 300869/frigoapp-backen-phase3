
# FreshKeeper — Phase 4: Alert Engine & Scheduler (Clean Pack)
Date: 2025-09-06

## What this pack contains
- `freshkeeper/services/alert_rules.py` — Pure functions to classify product status (OK, BIENTOT_PERIME, PERIME, STOCK_EPUISÉ).
- `freshkeeper/services/alert_runner.py` — Runner that scans products and upserts alerts (idempotent).
- `freshkeeper/jobs/scheduler.py` — APScheduler setup (runs once at startup then every N minutes).
- `APPEND_TO_MAIN.md` — How to wire this into your existing `freshkeeper/main.py` without breaking things.
- `.env.example` — Environment variables used by the scheduler.

## One-time install
```
pip install apscheduler python-dotenv
```

## How to integrate (short)
1) Add the env vars from `.env.example` to your `.env`.
2) Open `APPEND_TO_MAIN.md` and apply the small code patch to `freshkeeper/main.py`.
3) Start the API as usual (`uvicorn freshkeeper.main:app --reload`). You should see scheduler logs.

## Safety
- The runner is **idempotent**: it avoids duplicate alerts for the same product & day.
- Pure business rules live in `alert_rules.py` so you can test them easily.
- Nothing here changes your DB schema; it only **reads Products** and **upserts Alerts** assumed to exist.
- If your model/table names differ, adjust the imports in `alert_runner.py`.

## Definition of Done (Phase 4)
- [ ] Alerts generated on startup.
- [ ] Alerts regenerated on the defined interval.
- [ ] No duplicate alerts for the same product/status/day.
- [ ] Logs visible in console with counts of scanned products & upserted alerts.
- [ ] Status colors consistent with Excel (OK=VERT, BIENTOT=ROSE, PERIME=ROUGE, STOCK_EPUISÉ=GRIS).
