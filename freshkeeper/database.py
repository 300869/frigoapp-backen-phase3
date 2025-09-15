# app/database.py (avec alias DB_URL + get_db)
from dotenv import load_dotenv

load_dotenv()
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://frigo_user:Henry12345@127.0.0.1:5432/frigoapp",
)

DB_URL = DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Alias pour compat avec du code qui faisait `from freshkeeper.database import get_db`
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
