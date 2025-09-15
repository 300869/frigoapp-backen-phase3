# freshkeeper/main.py

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from freshkeeper.api.suggest import (
    router as suggest_router,  # expose "/suggest" que l'on prefixe en "/products"
)
from freshkeeper.api.suggest import (
    suggest_product,
)

# --- Routeurs FreshKeeper
from freshkeeper.routers.products import router as products_router
from routers.alerts import router as alerts_router
from routers.lots import router as lots_router
from routers.maintenance import router as admin_router
from routers.status import router as status_router

# --- Routeurs internes au projet (déjà présents chez toi)
from routers.storage_locations import router as storage_router

# ------------------------------------------------------------------------------
# App & Config
# ------------------------------------------------------------------------------
APP_NAME = os.getenv("FRESHKEEPER_APP_NAME", "FreshKeeper API")
APP_VERSION = os.getenv("FRESHKEEPER_VERSION", "0.1.0")

# generate_unique_id_function -> évite les warnings "Duplicate Operation ID"
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    generate_unique_id_function=lambda route: f"{route.name}_{route.path.replace('/', '_')}",
)

# CORS large par défaut (à resserrer si besoin via CORS_ALLOW_ORIGINS="https://ton-site.com,https://autre.com")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api_route(
    "/products/suggest",
    suggest_product,
    methods=["GET"],
    tags=["products"],
    name="products_suggest",
)


# ------------------------------------------------------------------------------
# Health & Root
# ------------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": f"{APP_NAME} is running", "version": APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# Montage des routeurs (chacun UNE SEULE FOIS)
# ------------------------------------------------------------------------------
# NB: ces routeurs fournissent déjà leurs propres préfixes/paths.
# Surtout ne pas re-déclarer les mêmes endpoints dans ce fichier.

app.include_router(storage_router)
app.include_router(lots_router)
app.include_router(status_router)
app.include_router(admin_router)
app.include_router(alerts_router)

# /products (CRUD via base SQL)
app.include_router(products_router)

# /products/suggest (défini dans freshkeeper/api/suggest.py comme "/suggest")
# On lui donne le préfixe "/products" ici -> endpoint final = "/products/suggest"
app.include_router(suggest_router, prefix="/products")


# ------------------------------------------------------------------------------
# (Optionnel) Hooks de démarrage / arrêt si nécessaire
# ------------------------------------------------------------------------------
# from freshkeeper.database import init_db  # exemple si tu as un init spécifique
# @app.on_event("startup")
# def on_startup():
#     init_db()
#     pass
#
# @app.on_event("shutdown")
# def on_shutdown():
#     pass
