import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from freshkeeper.database import get_db
from freshkeeper.services.detection import (
    add_days_iso,
    guess_category_by_keywords,
    normalize_name,
    pick_shelf_life,
)

router = APIRouter()


def row_to_dict(row) -> Dict[str, Any]:
    return dict(row._mapping) if row is not None else {}


def fetch_one(db: Session, sql: str, params: Dict[str, Any]):
    return db.execute(text(sql), params).fetchone()


@router.get("/suggest")
def suggest_product(
    name: str = Query(
        ..., min_length=1, description="Nom libre saisi par l'utilisateur"
    ),
    location: str = Query("pantry", pattern="^(pantry|fridge|freezer)$"),
    db: Session = Depends(get_db),
):
    n = normalize_name(name)

    # 1) exact match (name)
    row = fetch_one(
        db,
        """
        SELECT id, name, category_id, aliases, shelf_life
        FROM products
        WHERE LOWER(name) = LOWER(:n)
        LIMIT 1
    """,
        {"n": n},
    )

    # 2) alias JSONB exact
    if not row:
        row = fetch_one(
            db,
            """
            SELECT id, name, category_id, aliases, shelf_life
            FROM products
            WHERE aliases IS NOT NULL
              AND EXISTS (
                SELECT 1 FROM jsonb_array_elements_text(aliases) AS a(value)
                WHERE LOWER(a.value) = LOWER(:n)
              )
            LIMIT 1
        """,
            {"n": n},
        )

    # 3) contient dans le nom
    if not row:
        row = fetch_one(
            db,
            """
            SELECT id, name, category_id, aliases, shelf_life
            FROM products
            WHERE name ILIKE :pat
            LIMIT 1
        """,
            {"pat": f"%{n}%"},
        )

    product: Optional[Dict[str, Any]] = row_to_dict(row) if row else None

    # Catégorie depuis product_categories (PAS "categories")
    cat = None
    if product and product.get("category_id"):
        cat_row = fetch_one(
            db,
            """
            SELECT id, name, shelf_life
            FROM product_categories
            WHERE id = :cid
        """,
            {"cid": product["category_id"]},
        )
        cat = row_to_dict(cat_row) if cat_row else None

    # Catégorie devinée si pas trouvée via produit
    guessed_category = None
    if not cat:
        guessed_category = guess_category_by_keywords(n)

        # Renfort: mapping simple mots-clés -> catégories
        kw = n.lower()

        def any_in(s, arr):
            return any(a in s for a in arr)

        if any_in(kw, ["carotte", "carottes"]):
            guessed_category = guessed_category or "legume"
        if any_in(kw, ["poulet", "volaille", "canard", "coq", "pigeon", "chicken"]):
            guessed_category = guessed_category or "volaille"
        if any_in(
            kw, ["thon boite", "thon boîte", "boite", "boîte", "conserve", "canned"]
        ):
            guessed_category = guessed_category or "conserve"

        # Charger la durée de la catégorie devinée depuis la base
        if guessed_category:
            cat_row = fetch_one(
                db,
                """
                SELECT id, name, shelf_life
                FROM product_categories
                WHERE LOWER(name) = LOWER(:cname)
                LIMIT 1
            """,
                {"cname": guessed_category},
            )
            if cat_row:
                cat = row_to_dict(cat_row)

    # Parse JSONB -> dict (si SQLAlchemy renvoie déjà un dict pour JSONB, on le garde)
    def _to_dict(v):
        if not v:
            return None
        if isinstance(v, dict):
            return v
        try:
            return json.loads(v)
        except Exception:
            return None

    prod_shelf = _to_dict(product.get("shelf_life")) if product else None
    cat_shelf = _to_dict(cat.get("shelf_life")) if cat else None

    days = pick_shelf_life(prod_shelf, cat_shelf, location)
    expiry = add_days_iso(days)

    return {
        "match": product["id"] if product else None,
        "product": {
            "id": product["id"] if product else None,
            "name": product["name"] if product else name,
            "category": (cat["name"] if cat else guessed_category),
        },
        "suggested_expiry_date": expiry,
        "days": days,
    }
