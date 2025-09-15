# Patch à appliquer à `app/main.py` (FastAPI)

1) Démarrer le scheduler au lancement de l'app :
```python
# app/main.py
from fastapi import FastAPI
from freshkeeper.jobs.scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
def _startup():
    start_scheduler()

@app.get("/health")
def health():
    return {"status": "ok"}
```

2) Vérifier que `app/database.py` expose `SessionLocal` (session factory) et que vos modèles incluent `Alert`.
Voir exemple minimal ci-dessous si besoin.

