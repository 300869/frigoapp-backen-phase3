# FrigoApp Backend – Pack prêt à l'emploi (Phase 3 CRUD)

Contenu inclus :
- `app/models.py`
- `app/schemas/` : `user.py`, `category.py`, `product.py`, `consumption.py`, `alert.py`
- `app/routers/` : `users.py`, `categories.py`, `products.py`, `consumptions.py`, `alerts.py`
- `app/main.py`

Ce pack suppose `app/database.py` (Base, get_db) déjà présent.

## Démarrage
1. Copiez ces fichiers dans `app/`.
2. Migrations (si Alembic) :
   ```bash
   alembic revision --autogenerate -m "phase3 crud models"
   alembic upgrade head
   ```
3. Lancer :
   ```bash
   uvicorn app.main:app --reload
   ```
