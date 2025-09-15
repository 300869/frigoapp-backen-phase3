import datetime
import re
import unicodedata
from typing import Dict, Optional


def normalize_name(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9 ]+", " ", s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    if s.endswith("s") and len(s) > 3:
        s = s[:-1]
    return s


def pick_shelf_life(
    product_shelf: Optional[Dict], category_shelf: Optional[Dict], location: str
) -> int:
    if (
        product_shelf
        and isinstance(product_shelf, dict)
        and product_shelf.get(location) is not None
    ):
        return int(product_shelf[location])
    if (
        category_shelf
        and isinstance(category_shelf, dict)
        and category_shelf.get(location) is not None
    ):
        return int(category_shelf[location])
    return {"pantry": 5, "fridge": 7, "freezer": 90}.get(location, 5)


def add_days_iso(days: int) -> str:
    base = datetime.date.today()
    dt = base + datetime.timedelta(days=int(days))
    return dt.isoformat()


_KEYWORDS = {
    "fruit": [
        "banane",
        "pomme",
        "orange",
        "mangue",
        "papaye",
        "fraise",
        "raisin",
        "poire",
        "peche",
        "melon",
        "pasteque",
    ],
    "legume": [
        "salade",
        "laitue",
        "carotte",
        "tomate",
        "oignon",
        "ail",
        "pomme de terre",
        "courgette",
        "poivron",
    ],
    "viande": ["poulet", "boeuf", "steak", "dinde", "porc", "agneau"],
    "boisson": ["lait", "jus", "soda", "eau", "yaourt", "kefir"],
    "conserve": ["thon", "mais", "haricot", "sauce tomate", "olives"],
    "laitage": ["yaourt", "fromage", "lait", "beurre", "creme"],
    "boulangerie": ["pain", "baguette", "brioche", "croissant", "tortilla"],
}


def guess_category_by_keywords(n: str) -> Optional[str]:
    for cat, words in _KEYWORDS.items():
        for w in words:
            if w in n:
                return cat
    return None
