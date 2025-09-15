# freshkeeper/api/suggest.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

# Imports 100% sur le package 'freshkeeper'
from freshkeeper.db import get_db
from freshkeeper.models import Category, Product
from freshkeeper.services.detection import (
    add_days_iso,
    guess_category_by_keywords,
    normalize_name,
    pick_shelf_life,
)

router = APIRouter()


@router.get("/products/suggest")
def suggest_product(
    name: str = Query(
        ..., min_length=1, description="Nom libre saisi par l'utilisateur"
    ),
    location: str = Query("pantry", pattern="^(pantry|fridge|freezer)$"),
    db: Session = Depends(get_db),
):
    n = normalize_name(name)

    product: Optional[Product] = None
    # 1) Exact match on normalized name
    product = db.query(Product).filter(Product.name.ilike(n)).first()

    # 2) Match on aliases (JSON contains string)
    if not product:
        try:
            product = (
                db.query(Product)
                .filter(cast(Product.aliases, String).ilike(f'%"{n}"%'))
                .first()
            )
        except Exception:
            product = None  # aliases peut ne pas exister encore

    # 3) Fallback "contains" on product name
    if not product:
        product = db.query(Product).filter(Product.name.ilike(f"%{n}%")).first()

    cat = None
    if product and getattr(product, "category_id", None):
        cat = db.query(Category).get(product.category_id)

    # Keyword-based category guess si pas de catégorie
    guessed_category = None
    if not cat:
        guessed_category = guess_category_by_keywords(n)

    days = pick_shelf_life(
        getattr(product, "shelf_life", None),
        getattr(cat, "shelf_life", None) if cat else None,
        location,
    )
    expiry = add_days_iso(days)

    return {
        "match": getattr(product, "id", None),
        "product": {
            "id": getattr(product, "id", None),
            "name": getattr(product, "name", name),
            "category": getattr(cat, "name", None) if cat else guessed_category,
        },
        "suggested_expiry_date": expiry,
        "days": days,
    }
