# scripts/seed_products.py
"""
Usage (PowerShell):
  $env:DATABASE_URL="postgresql+psycopg2://frigo_user:VOTRE_MDP@localhost/freshkeeper"
  python scripts/seed_products.py data/seed_products.json
"""
import json
import os
import sys
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Try both layouts
try:
    from freshkeeper.db import get_db  # not strictly needed here
    from freshkeeper.models import Base, Category, Product
except Exception:
    from src.models import Base, Category, Product  # type: ignore


def get_engine():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("ERROR: set DATABASE_URL env var.", file=sys.stderr)
        sys.exit(1)
    return create_engine(url, future=True)


def upsert_category(sess, name: str, shelf_life: Optional[dict] = None):
    c = sess.query(Category).filter(Category.name == name).first()
    if not c:
        c = Category(name=name, shelf_life=shelf_life or None)
        sess.add(c)
        sess.flush()
    else:
        # update shelf_life if provided
        if shelf_life:
            c.shelf_life = shelf_life
    return c


def upsert_product(
    sess,
    name: str,
    category: Optional[Category],
    shelf_life: Optional[dict],
    aliases: Optional[list],
):
    p = sess.query(Product).filter(Product.name == name).first()
    if not p:
        p = Product(name=name)
        sess.add(p)
        sess.flush()
    if category:
        p.category_id = category.id
    if shelf_life:
        p.shelf_life = shelf_life
    if aliases:
        p.aliases = [a for a in aliases]
    return p


def main(path_json: str):
    if not os.path.exists(path_json):
        print(f"File not found: {path_json}", file=sys.stderr)
        sys.exit(1)

    data = json.load(open(path_json, "r", encoding="utf-8"))
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    sess = SessionLocal()

    try:
        # Ensure tables exist (no-op if already via Alembic)
        Base.metadata.create_all(bind=engine)

        # categories
        cat_index = {}
        for c in data.get("categories", []):
            cat = upsert_category(sess, c["name"], c.get("shelf_life"))
            cat_index[c["name"]] = cat

        # products
        for p in data.get("products", []):
            cat = cat_index.get(p.get("category")) if p.get("category") else None
            upsert_product(sess, p["name"], cat, p.get("shelf_life"), p.get("aliases"))

        sess.commit()
        print("Seed OK.")
    except Exception as e:
        sess.rollback()
        raise
    finally:
        sess.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_products.py data/seed_products.json")
        sys.exit(1)
    main(sys.argv[1])
