# freshkeeper/main.py — version corrigée (routers montés UNE seule fois)
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Routeurs API (utiliser UNIQUEMENT src.api.*)
from src.api.products import router as products_router
from src.api.alerts import router as alerts_router
from src.api.lots import router as lots_router

# --- Suggest (optionnel) — on l'importe de façon sûre
try:
    from freshkeeper.api.suggest import suggest_product
    HAS_SUGGEST = True
except Exception:
    suggest_product = None
    HAS_SUGGEST = False

APP_NAME = os.getenv("FRESHKEEPER_APP_NAME", "FreshKeeper API")
APP_VERSION = os.getenv("FRESHKEEPER_VERSION", "0.1.0")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    generate_unique_id_function=lambda route: f"{route.name}_{route.path.replace('/', '_')}",
)

# CORS (resserre via CORS_ALLOW_ORIGINS="http://192.168.1.18:19000,http://192.168.1.18:19006")
allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & Root
@app.get("/")
def root():
    return {"message": f"{APP_NAME} is running", "version": APP_VERSION}

@app.get("/health")
def health():
    return {"status": "ok"}

# Montage des routeurs (chacun UNE SEULE FOIS)
app.include_router(products_router)
app.include_router(alerts_router)
app.include_router(lots_router)

# Expose /products/suggest si disponible
if HAS_SUGGEST and suggest_product is not None:
    app.add_api_route(
        "/products/suggest",
        suggest_product,
        methods=["GET"],
        tags=["products"],
        name="products_suggest",
    )
