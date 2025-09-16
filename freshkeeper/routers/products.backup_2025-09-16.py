from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime
import os, inspect

from freshkeeper.database import get_db
from freshkeeper.models import Product
from freshkeeper.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductRead])
def list_products(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if q:
        like = f"%{q}%"
        query = query.filter(Product.name.ilike(like))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    return query.order_by(Product.created_at.desc()).all()


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    obj = Product(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    return obj


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    db.delete(obj)
    db.commit()
    return None
