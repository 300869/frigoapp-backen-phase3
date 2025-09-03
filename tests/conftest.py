import os

import pytest
from fastapi.testclient import TestClient

# Forcer une base SQLite locale pour les tests CI/local
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

# Import de l'app FastAPI (package 'app' ou fichier 'main.py' à la racine)
try:
    from app.main import app  # app/main.py
except ModuleNotFoundError:
    from main import app  # main.py à la racine


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def category_id(client):
    # Adapte si ton API utilise un autre schéma/endpoint
    r = client.post("/categories", json={"name": "Test"})
    assert r.status_code in (200, 201)
    data = r.json()
    return data.get("id") or data.get("category", {}).get("id")
