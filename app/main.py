﻿from fastapi import FastAPI
from app.database import Base, engine
from app import models  # important: charger les modèles avant create_all
from app.routers import products, alerts, categories

app = FastAPI(title="FrigoApp API", version="0.1.0")
Base.metadata.create_all(bind=engine)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(alerts.router)

@app.get("/health")
def health():
    return {"status": "ok"}
