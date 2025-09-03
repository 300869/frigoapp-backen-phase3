import os
import pytest
from fastapi.testclient import TestClient

# Forcer une base SQLite locale pour les tests CI/local
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

# Import de l'app FastAPI (package 'app' OU fichier 'main.py' à la racine)
try:
    from app.main import app  # app/main.py
except ModuleNotFoundError:
    from main import app      # main.py à la racine

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def category_id(client):
    # Essaie plusieurs endpoints/payloads
    endpoints = ["/categories", "/api/categories"]
    payloads = [
        {"name": "Test"},
        {"name": "Test", "description": "Test"},
        {"label": "Test"},
        {"title": "Test"},
    ]

    last_resp = None
    for url in endpoints:
        for body in payloads:
            r = client.post(url, json=body)
            if r.status_code in (200, 201):
                data = r.json()
                return data.get("id") or data.get("category", {}).get("id")
            last_resp = r

    try:
        detail = last_resp.json()
    except Exception:
        detail = last_resp.text
    pytest.fail(
        f"Impossible de créer une catégorie (status={last_resp.status_code}, body={detail})"
    )
