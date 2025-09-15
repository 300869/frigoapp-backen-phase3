import os

from fastapi.testclient import TestClient

# Forcer SQLite en CI/local test
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

from freshkeeper.main import freshkeeper  # doit exister et créer l'app FastAPI

client = TestClient(app)


def test_app_starts():
    r = client.get("/")
    assert r.status_code in (200, 404)  # selon si tu as une route /

