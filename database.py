from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connexion PostgreSQL locale
DATABASE_URL = "postgresql+psycopg2://frigo_user:Henry12345@localhost:5432/freshkeeper"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
