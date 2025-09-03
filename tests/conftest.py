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
