import os

import pytest
from fastapi.testclient import TestClient

# Base de test = SQLite locale (pas de Postgres requis en CI)
os.environ["DATABASE_URL"] = "sqlite:///./test_ci.db"

from app import models
from app.database import SessionLocal
from app.main import app  # après l'override de DATABASE_URL


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def category_id():
    # Seed d'une catégorie pour les tests
    db = SessionLocal()
    try:
        cat = db.query(models.Category).first()
        if not cat:
            cat = models.Category(name="TestCat")
            db.add(cat)  # ✅ on ajoute bien
            db.commit()
            db.refresh(cat)
        return cat.id
    finally:
        db.close()  # ✅ toujours exécuté
