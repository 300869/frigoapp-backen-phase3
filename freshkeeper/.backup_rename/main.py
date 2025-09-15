import os

from fastapi import FastAPI

api = FastAPI()

if os.getenv("FRIGO_DEV_CREATE_ALL") == "1":
    import app.models.alert
    import app.models.category
    import app.models.consumption
    import app.models.product
    from app.database import Base, engine

    Base.metadata.create_all(bind=engine)

from app.routers import alerts as alerts_router
from app.routers import consumptions as consumptions_router

api.include_router(alerts_router.router)
api.include_router(consumptions_router.router)


@api.get("/health")
def health():
    return {"ok": True}


app = api
