# freshkeeper/utils/utils_detection.py
import datetime
import re
import unicodedata
from typing import Dict, Optional


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9 ]+", " ", s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    # singulier trÃ¨s simple : enlÃ¨ve 's' final
    s = re.sub(r"s\b", "", s)
    return s


def pick_shelf_life(
    product: Optional[Dict], category: Optional[Dict], location: str
) -> int:
    # prioritÃ© produit > catÃ©gorie > defaults
    if product and (sl := product.get("shelf_life")) and (v := sl.get(location)):
        return int(v)
    if category and (sl := category.get("shelf_life")) and (v := sl.get(location)):
        return int(v)
    # fallbacks gÃ©nÃ©riques
    return {"pantry": 5, "fridge": 7, "freezer": 90}.get(location, 5)


def add_days_iso(days: int) -> str:
    base = datetime.date.today()
    return (base + datetime.timedelta(days=days)).isoformat()
