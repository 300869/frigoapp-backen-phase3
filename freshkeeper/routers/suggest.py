# freshkeeper/routers/suggest.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import (  # utile si tu fais des cast() sur des colonnes JSON -> String
    String,
)
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Product  # adapte si tes modÃ¨les sont scindÃ©s
from ..utils.utils_detection import add_days_iso, norm, pick_shelf_life

# PrÃ©fixe pour Ã©viter le conflit /products/{product_id}
router = APIRouter(prefix="/suggest", tags=["suggest"])


@router.get("/product")
def suggest_product(
    name: str = Query(..., min_length=1),
    location: str = Query("pantry", pattern="^(pantry|fridge|freezer)$"),
    db: Session = Depends(get_db),
):
    n = norm(name)

    # 1) match exact
    product = db.query(Product).filter(Product.name.ilike(n)).first()

    # 2) fallback: contient
    if not product:
        product = db.query(Product).filter(Product.name.ilike(f"%{n}%")).first()

    # 3) catÃ©gorie (si product trouvÃ©)
    cat = None
    if product and getattr(product, "category_id", None):
        cat = db.query(Category).get(product.category_id)

    # 4) durÃ©e & date proposÃ©es
    p_dict = {"shelf_life": getattr(product, "shelf_life", None)} if product else None
    c_dict = {"shelf_life": getattr(cat, "shelf_life", None)} if cat else None
    days = pick_shelf_life(p_dict, c_dict, location)
    expiry = add_days_iso(days)

    return {
        "match": getattr(product, "id", None) if product else None,
        "product": {
            "id": getattr(product, "id", None) if product else None,
            "name": getattr(product, "name", None) if product else name,
            "category": getattr(cat, "name", None) if cat else None,
        },
        "suggested_expiry_date": expiry,
        "days": days,
        "source": "product" if product else "fallback",
    }
