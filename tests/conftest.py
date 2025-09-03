import os

import pytest

# Utilise SQLite en test
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

try:
    from app.database import Base, engine
except Exception:
    Base = engine = None


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    if Base and engine:
        Base.metadata.create_all(bind=engine)
    yield
    if Base and engine:
        Base.metadata.drop_all(bind=engine)


import os

import pytest
from fastapi.testclient import TestClient

# Forcer une base SQLite locale pour les tests CI/local
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

# Import de l'app FastAPI
from app.main import app  # doit exposer "app = FastAPI(...)"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
