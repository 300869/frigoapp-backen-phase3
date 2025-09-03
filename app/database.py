import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lis l'URL depuis l'environnement (sinon SQLite de secours)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# 🔧 Sécurise le driver PostgreSQL : force psycopg3 (pas psycopg2)
# - "postgresql://"        -> "postgresql+psycopg://"
# - "postgresql+psycopg2://" -> "postgresql+psycopg://"
if DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DB_URL.startswith("postgresql+psycopg2://"):
    DB_URL = DB_URL.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)

engine = create_engine(DB_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
