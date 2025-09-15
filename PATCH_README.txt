FrigoApp — Phase 3 READY FILES
==================================
Généré le 2025-09-05 14:19:38

Contenu (Phase 3 uniquement) :
- app/dependencies.py
- app/routers/alerts.py
- app/routers/consumptions.py
- app/schemas/alerts.py
- app/schemas/consumption.py
- app/services/alerts.py
- app/services/consumption.py
- app/models/alert.py
- app/models/consumption.py
- __init__.py pour app/*

Intégration :
1) Copie ces fichiers dans ton projet en remplaçant ceux de la Phase 3.
2) Dans app/main.py :
     from freshkeeper.routers import alerts as alerts_router
     from freshkeeper.routers import consumptions as consumptions_router
     app.include_router(alerts_router.router)
     app.include_router(consumptions_router.router)
3) DB :
     - Alembic : alembic revision --autogenerate -m "phase3 alerts+consumption" && alembic upgrade head
     - Sans Alembic (dev) : exécuter Base.metadata.create_all(bind=engine) en s'assurant que
       app.models.alert et app.models.consumption sont importés avant.
4) Lancer :
     uvicorn app.main:app --reload
   Ouvrir http://127.0.0.1:8000/docs

