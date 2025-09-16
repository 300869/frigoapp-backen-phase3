import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1) Charger .env TÔT pour que DATABASE_URL soit dispo à l'import des routeurs
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass  # Si python-dotenv absent, variables déjà dans l'env

def _try_import(router_path: str):
    """Importe prudemment un router 'module:attr' et retourne l'objet ou None."""
    try:
        module_path, attr = router_path.split(":", 1)
    except ValueError:
        module_path, attr = router_path, "router"
    try:
        mod = __import__(module_path, fromlist=[attr])
        return getattr(mod, attr)
    except Exception:
        return None

APP_NAME = os.getenv("FRESHKEEPER_APP_NAME", "FreshKeeper API")
APP_VERSION = os.getenv("FRESHKEEPER_VERSION", "0.1.0")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# CORS (par défaut permissif; resserrer avec CORS_ALLOW_ORIGINS="http://192.168.1.18:19000,http://192.168.1.18:19006")
allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & root
@app.get("/")
def root():
    return {"message": f"{APP_NAME} is running", "version": APP_VERSION}

@app.get("/health")
def health():
    return {"status": "ok"}

# Monter les routeurs S'ILS EXISTENT (tous via freshkeeper.routers.*)
for path in [
    "freshkeeper.routers.storage_locations:router",
    "freshkeeper.routers.status:router",
    "freshkeeper.routers.maintenance:router",
    "freshkeeper.routers.lots:router",
    "freshkeeper.routers.alerts:router",
    "freshkeeper.routers.products:router",
]:
    r = _try_import(path)
    if r:
        app.include_router(r)

# /products/suggest (optionnel)
try:
    from freshkeeper.api.suggest import router as suggest_router  # type: ignore
    app.include_router(suggest_router, prefix="/products")
except Exception:
    pass
# --- Compatibilité pour clients mobiles qui appellent /api/* ---
try:
    from freshkeeper.routers import products as _prod
    from freshkeeper.routers import alerts as _alerts
    from freshkeeper.routers import lots as _lots
    app.include_router(_prod.router, prefix="/api")
    app.include_router(_alerts.router, prefix="/api")
    app.include_router(_lots.router, prefix="/api")
except Exception:
    pass

# (Optionnel) /api/products/suggest si dispo
try:
    from freshkeeper.api import suggest as _suggest
    app.include_router(_suggest.router, prefix="/api/products")
except Exception:
    pass
# --- Compatibilité clients mobiles: exposer aussi /api/* et /api/v1/* ---
try:
    from freshkeeper.routers import products as _prod
    from freshkeeper.routers import alerts as _alerts
    from freshkeeper.routers import lots as _lots
    for _prefix in ("/api", "/api/v1"):
        app.include_router(_prod.router,   prefix=_prefix)
        app.include_router(_alerts.router, prefix=_prefix)
        app.include_router(_lots.router,   prefix=_prefix)
except Exception:
    pass

# Miroir du /health sous /api et /api/v1
try:
    app.add_api_route("/api/health", health, methods=["GET"])
    app.add_api_route("/api/v1/health", health, methods=["GET"])
except Exception:
    pass
# --- ALIAS directs pour /api/products et /api/v1/products ---
try:
    from freshkeeper.routers import products as _prod

    # Liste
    app.add_api_route("/api/products", _prod.list_products, methods=["GET"], tags=["products"])
    app.add_api_route("/api/products/", _prod.list_products, methods=["GET"], tags=["products"])
    app.add_api_route("/api/v1/products", _prod.list_products, methods=["GET"], tags=["products"])
    app.add_api_route("/api/v1/products/", _prod.list_products, methods=["GET"], tags=["products"])

    # Détail
    app.add_api_route("/api/products/{product_id}", _prod.get_product, methods=["GET"], tags=["products"])
    app.add_api_route("/api/v1/products/{product_id}", _prod.get_product, methods=["GET"], tags=["products"])
except Exception:
    pass
from fastapi import Request
from starlette.responses import RedirectResponse

# Redirige /api/<tout> -> /<tout>
@app.api_route("/api_compat_disabled/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def _api_compat(path: str, request: Request):
    return RedirectResponse(url=f"/{path}", status_code=307)

# Redirige /api/v1/<tout> -> /<tout>
@app.api_route("/api_v1_compat_disabled/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def _api_v1_compat(path: str, request: Request):
    return RedirectResponse(url=f"/{path}", status_code=307)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime

def _plain(v):
    if isinstance(v, Decimal):
        try: return float(v)
        except Exception: return str(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v

def _fetch_all_sql(table: str, columns: str):
    url = os.getenv("DATABASE_URL")
    if not url:
        return []
    eng = create_engine(url, future=True)
    rows = []
    with eng.connect() as c:
        for r in c.execute(text(f"SELECT {columns} FROM {table} ORDER BY id")).mappings():
            rows.append({k: _plain(v) for k, v in r.items()})
    return rows

# ---------- ALERTS ----------
@app.get("/api/alerts", tags=["alerts"])
@app.get("/api/v1/alerts", tags=["alerts"])
def _api_alerts_list():
    try:
        items = _fetch_all_sql(
            "alerts",
            "id, product_id, kind, due_date, message, is_active, created_at, updated_at, lot_id"
        )
    except Exception:
        items = []
    return JSONResponse(content=jsonable_encoder(items or []), status_code=200)

# ---------- LOTS ----------
@app.get("/api/lots", tags=["lots"])
@app.get("/api/v1/lots", tags=["lots"])
def _api_lots_list():
    try:
        items = _fetch_all_sql(
            "lots",
            "id, product_id, quantity, unit, expiry_date, storage_location_id"
        )
    except Exception:
        items = []
    return JSONResponse(content=jsonable_encoder(items or []), status_code=200)

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime
import os

def _plain(v):
    if isinstance(v, Decimal):
        try: return float(v)
        except Exception: return str(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v

def _fetch_all_sql(table: str, columns: str):
    url = os.getenv("DATABASE_URL")
    if not url:
        return []
    eng = create_engine(url, future=True)
    rows = []
    with eng.connect() as c:
        for r in c.execute(text(f"SELECT {columns} FROM {table} ORDER BY id")).mappings():
            rows.append({k: _plain(v) for k, v in r.items()})
    return rows

# ---------- ALERTS ----------
@app.get("/api/alerts", tags=["alerts"])
@app.get("/api/v1/alerts", tags=["alerts"])
def _api_alerts_list():
    try:
        items = _fetch_all_sql(
            "alerts",
            "id, product_id, kind, due_date, message, is_active, created_at, updated_at, lot_id"
        )
    except Exception:
        items = []
    return JSONResponse(content=jsonable_encoder(items or []), status_code=200)

# ---------- LOTS ----------
@app.get("/api/lots", tags=["lots"])
@app.get("/api/v1/lots", tags=["lots"])
def _api_lots_list():
    try:
        items = _fetch_all_sql(
            "lots",
            "id, product_id, quantity, unit, expiry_date, storage_location_id"
        )
    except Exception:
        items = []
    return JSONResponse(content=jsonable_encoder(items or []), status_code=200)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime
import os

def _plain(v):
    if isinstance(v, Decimal):
        try: return float(v)
        except Exception: return str(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v

def _engine():
    url = os.getenv("DATABASE_URL")
    if not url: return None
    from sqlalchemy import create_engine
    return create_engine(url, future=True)

# ---------- STATUS ----------
@app.get("/api/status")
@app.get("/api/v1/status")
def _api_status():
    return {"api":"ok","version": os.getenv("FRESHKEEPER_VERSION","0.1.0")}

# ---------- CATEGORIES (dérivées de products.category) ----------
@app.get("/api/categories")
@app.get("/api/v1/categories")
def _api_categories():
    eng = _engine()
    items = []
    if eng is not None:
        sql = text("SELECT category, COUNT(*) AS product_count FROM products WHERE category IS NOT NULL GROUP BY category ORDER BY category")
        with eng.connect() as c:
            for r in c.execute(sql).mappings():
                items.append({"name": r["category"], "product_count": int(r["product_count"] or 0)})
    return JSONResponse(content=jsonable_encoder(items), status_code=200)

# ---------- STORAGE LOCATIONS (si la table existe : id, name) ----------
@app.get("/api/storage-locations")
@app.get("/api/v1/storage-locations")
def _api_storage_locations():
    eng = _engine()
    items = []
    if eng is not None:
        try:
            sql = text("SELECT id, name FROM storage_locations ORDER BY id")
            with eng.connect() as c:
                for r in c.execute(sql).mappings():
                    items.append({"id": r.get("id"), "name": r.get("name")})
        except Exception:
            # table absente -> liste vide
            items = []
    return JSONResponse(content=jsonable_encoder(items), status_code=200)
from fastapi import Request
from fastapi.responses import JSONResponse

# Catch-all placé en DERNIER : loggue tout chemin /api/* inconnu
@app.api_route("/api/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def _api_unknown(path: str, request: Request):
    print(f"UNKNOWN /api PATH -> /api/{path}  method={request.method}")
    return JSONResponse({"detail":"Not Found","path": f"/api/{path}","method": request.method}, status_code=404)

@app.api_route("/api/v1/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def _apiv1_unknown(path: str, request: Request):
    print(f"UNKNOWN /api/v1 PATH -> /api/v1/{path}  method={request.method}")
    return JSONResponse({"detail":"Not Found","path": f"/api/v1/{path}","method": request.method}, status_code=404)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, text
import os

@app.get("/api/missing-expiry", tags=["lots"])
@app.get("/api/v1/missing-expiry", tags=["lots"])
def _api_missing_expiry():
    url = os.getenv("DATABASE_URL")
    items = []
    if url:
        eng = create_engine(url, future=True)
        sql = text("""
            SELECT l.id AS lot_id,
                   l.product_id,
                   p.name AS product_name,
                   l.quantity,
                   l.unit,
                   l.expiry_date,
                   l.storage_location_id
            FROM lots l
            LEFT JOIN products p ON p.id = l.product_id
            WHERE l.expiry_date IS NULL
            ORDER BY l.id
        """)
        with eng.connect() as c:
            for r in c.execute(sql).mappings():
                items.append(dict(r))
    return JSONResponse(content=jsonable_encoder(items), status_code=200)
# --- ALIAS pack pour /api et /api/v1 chemins mobiles usuels ---
try:
    from freshkeeper.routers import products as _prod

    # LIST & DETAILS
    app.add_api_route("/api/products/list", _prod.list_products, methods=["GET"], tags=["products"])
    app.add_api_route("/api/v1/products/list", _prod.list_products, methods=["GET"], tags=["products"])
    app.add_api_route("/api/products/{product_id}/details", _prod.get_product, methods=["GET"], tags=["products"])
    app.add_api_route("/api/v1/products/{product_id}/details", _prod.get_product, methods=["GET"], tags=["products"])
except Exception as e:
    print("Alias products failed:", e)

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime
import os

def _plain(v):
    if isinstance(v, Decimal):
        try: return float(v)
        except Exception: return str(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v

def _sql_all(query: str):
    url = os.getenv("DATABASE_URL")
    if not url: return []
    eng = create_engine(url, future=True)
    rows=[]
    with eng.connect() as c:
        for r in c.execute(text(query)).mappings():
            rows.append({k:_plain(v) for k,v in r.items()})
    return rows

# ALERTS /active
@app.get("/api/alerts/active", tags=["alerts"])
@app.get("/api/v1/alerts/active", tags=["alerts"])
def _alerts_active_alias():
    rows = _sql_all("SELECT id, product_id, kind, due_date, message, is_active, created_at, updated_at, lot_id FROM alerts ORDER BY id")
    items = [r for r in rows if r.get("is_active")]
    return JSONResponse(content=jsonable_encoder(items or []), status_code=200)

# LOTS /grouped
@app.get("/api/lots/grouped", tags=["lots"])
@app.get("/api/v1/lots/grouped", tags=["lots"])
def _lots_grouped_alias():
    rows = _sql_all("SELECT id, product_id, quantity, unit, expiry_date, storage_location_id FROM lots ORDER BY id")
    grouped = {}
    for r in rows:
        pid = r.get("product_id")
        grouped.setdefault(pid, []).append(r)
    payload = [{"product_id": pid, "lots": lots} for pid, lots in grouped.items()]
    return JSONResponse(content=jsonable_encoder(payload or []), status_code=200)
