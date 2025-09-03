
# FrigoApp Backend (squelette)

## Structure
app/
├─ main.py
├─ database.py
├─ models.py
├─ schemas.py
├─ routers/
│  ├─ products.py
│  └─ alerts.py
└─ services/
   └─ alerts_service.py

## Lancer en local (Windows PowerShell)
1) Crée un venv et installe les deps:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

2) Configure la base (par défaut DB_URL vise Postgres). Pour tester vite, tu peux poser une var d'env:
   $env:DATABASE_URL="sqlite:///./dev.db"

3) Démarre:
   uvicorn app.main:app --reload

4) Ouvre Swagger:
   http://127.0.0.1:8000/docs

## Alembic (optionnel)
   alembic revision -m "init"
   alembic upgrade head
## Roadmap

- [ ] Auth
- [x] Produits + Alertes

