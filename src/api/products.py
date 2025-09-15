import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, future=True)


class Product(BaseModel):
    id: int
    name: str
    location: str | None = None
    quantity: int
    expiry_date: str | None = None


router = APIRouter(tags=["products"])


@router.get("/products", response_model=list[Product])
def list_products():
    try:
        with engine.connect() as conn:
            rows = (
                conn.execute(
                    text(
                        "SELECT id, name, location, quantity, expiry_date FROM products ORDER BY id"
                    )
                )
                .mappings()
                .all()
            )
        return [Product(**dict(r)) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
