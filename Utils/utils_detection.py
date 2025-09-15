# utils_detection.py
import datetime
import re
import unicodedata
from typing import Dict, Optional


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9 ]+", " ", s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def pick_shelf_life(
    product: Optional[Dict], category: Optional[Dict], location: str
) -> int:
    # priorité: produit.shelf_life > catégorie.shelf_life > fallbacks
    if product and product.get("shelf_life") and product["shelf_life"].get(location):
        return int(product["shelf_life"][location])
    if category and category.get("shelf_life") and category["shelf_life"].get(location):
        return int(category["shelf_life"][location])
    # fallbacks génériques
    return {"pantry": 5, "fridge": 7, "freezer": 90}.get(location, 5)


def add_days_iso(days: int) -> str:
    base = datetime.date.today()
    dt = base + datetime.timedelta(days=days)
    return dt.isoformat()
