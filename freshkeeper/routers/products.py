from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime
import os

router = APIRouter()

def _plain(v):
    if isinstance(v, Decimal):
        try:
            return float(v)
        except Exception:
            return str(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v

def _fetch_all():
    url = os.getenv("DATABASE_URL")
    if not url:
        return []
    eng = create_engine(url, future=True)
    sql = text("""
        SELECT id, name, category, unit, quantity, expiry_date
        FROM products
        ORDER BY id
    """)
    rows = []
    with eng.connect() as c:
        for r in c.execute(sql).mappings():
            rows.append({k: _plain(v) for k, v in r.items()})
    return rows

def _fetch_one(pid: int):
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    eng = create_engine(url, future=True)
    sql = text("""
        SELECT id, name, category, unit, quantity, expiry_date
        FROM products
        WHERE id = :pid
    """)
    with eng.connect() as c:
        r = c.execute(sql, {"pid": pid}).mappings().first()
        return {k: _plain(v) for k, v in (r or {}).items()} if r else None

# ---- Liste : /products ET /products/ ----
@router.get("/products", include_in_schema=False)
@router.get("/products/", tags=["products"])
def list_products():
    try:
        items = _fetch_all()
    except Exception:
        items = []
    return JSONResponse(content=jsonable_encoder(items or []), status_code=200)

# ---- Détail : /products/{id} ----
@router.get("/products/{product_id}", tags=["products"])
def get_product(product_id: int):
    try:
        obj = _fetch_one(product_id)
    except Exception:
        obj = None
    if not obj:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    return JSONResponse(content=jsonable_encoder(obj), status_code=200)
