    # Intégration du CRUD (Phase 3)

    1) **Modèles** : ouvre `app/models.py` et colle **à la fin** le bloc fourni dans `APPEND_TO_MODELS.md`.
       - Si tu utilises Alembic : `alembic revision --autogenerate -m "add categories/consumptions/alerts"` puis `alembic upgrade head`.
    2) **Schemas** : copie le dossier `app/schemas` (ou fusionne les fichiers si tu en as déjà).
    3) **Routers** : copie le dossier `app/routers` et ajoute dans `app/main.py` :
       ```python
       # Ajoute ceci dans app/main.py (ou équivalent) après avoir créé your FastAPI() app:
from freshkeeper.routers.categories import router as categories_router
from freshkeeper.routers.consumptions import router as consumptions_router
from freshkeeper.routers.alerts import router as alerts_router

app.include_router(categories_router)
app.include_router(consumptions_router)
app.include_router(alerts_router)

       ```
    4) **Test rapide** (exemples):
       - `GET /categories`
       - `POST /categories` body: `{"name":"Frais","description":"Produits au frais"}`
       - `POST /consumptions` body: `{"user_id":1,"product_id":1,"quantity":1}`
       - `POST /alerts` body: `{"user_id":1,"product_id":1,"status":"Bientôt périmé","message":"Expire sous 3 jours"}`

    5) **Sécurité** : si tu as des dépendances d'auth (ex: `get_current_user`), ajoute-les dans chaque route.

