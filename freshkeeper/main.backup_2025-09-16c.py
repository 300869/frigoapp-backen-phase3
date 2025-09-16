# freshkeeper/main.py — corrected: load .env BEFORE importing routers
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 1) Load .env early so modules that read env at import-time (e.g., products.py) see DATABASE_URL
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv missing is non-fatal if DATABASE_URL is already in the environment
    pass

# --- 2) Now import routers (they may read DATABASE_URL on import)
from src.api.products import router as products_router
from src.api.alerts import router as alerts_router
from src.api.lots import router as lots_router

# Optional suggest route (guarded)
try:
    from freshkeeper.api.suggest import suggest_product  # type: ignore
    HAS_SUGGEST = True
except Exception:
    suggest_product = None
    HAS_SUGGEST = False

APP_NAME = os.getenv("FRESHKEEPER_APP_NAME", "FreshKeeper API")
APP_VERSION = os.getenv("FRESHKEEPER_VERSION", "0.1.0")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# --- CORS (configure via CORS_ALLOW_ORIGINS or default *)
allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health endpoints
@app.get("/")
def root():
    return {"message": f"{APP_NAME} is running", "version": APP_VERSION}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Routers mounted exactly once
app.include_router(products_router)
app.include_router(alerts_router)
app.include_router(lots_router)

# --- Optional: /products/suggest if available
if HAS_SUGGEST and suggest_product is not None:
    app.add_api_route(
        "/products/suggest",
        suggest_product,
        methods=["GET"],
        tags=["products"],
        name="products_suggest",
    )
