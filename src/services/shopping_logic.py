from collections import defaultdict
from datetime import date
from typing import Any, Dict, List

from .alerts_logic import days_to_expire


def build_base_courses(db, Product, History) -> Dict[str, Dict[str, Any]]:
    # Base de suggestions: stock manquant + historique.
    # Règle simple: si un produit a < 1 en stock mais existe en historique -> suggérer 1.
    suggestions: Dict[str, Dict[str, Any]] = {}
    hist_names = {h.name for h in db.query(History).all()}
    stock = db.query(Product).all()
    by_name_qty = defaultdict(float)
    for p in stock:
        by_name_qty[p.name] += float(p.quantity or 0)
    for name in hist_names:
        if by_name_qty[name] < 1:
            suggestions[name] = {"suggested_qty": 1.0}
    return suggestions


def merge_user_inputs(
    base: Dict[str, Dict[str, Any]], user_rows: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    out = dict(base)
    for r in user_rows:
        name = r["name"]
        qty = float(r.get("qty", 0) or 0)
        if name in out:
            out[name]["suggested_qty"] = max(out[name]["suggested_qty"], qty)
        else:
            out[name] = {"suggested_qty": qty}
    return out


def group_lots_by_name_and_expiry(
    db, Product, items: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    lots: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for name in items.keys():
        lots[name] = {"rouge": [], "jaune": [], "vert": []}
        same = db.query(Product).filter(Product.name == name).all()
        for p in same:
            d = days_to_expire(p.expiry_date)
            bucket = "rouge" if d <= 3 else ("jaune" if d <= 10 else "vert")
            lots[name][bucket].append(
                {
                    "id": p.id,
                    "qty": float(p.quantity or 0),
                    "expiry_date": p.expiry_date,
                    "days_left": d,
                }
            )
        for b in ("rouge", "jaune", "vert"):
            lots[name][b].sort(key=lambda x: x["days_left"], reverse=True)
    return lots


def validate_aa(items: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for name, meta in items.items():
        qty = float(meta.get("suggested_qty", 0) or 0)
        if qty > 0:
            meta["status"] = "to_buy"
            out[name] = meta
    return out


def checkout_to_bb(
    aa: Dict[str, Dict[str, Any]], purchases: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    bb = []
    for r in purchases:
        name = r["name"]
        qty = float(r.get("qty", 0) or 0)
        if qty <= 0:
            continue
        expiry_date = r.get("expiry_date")
        bb.append(
            {
                "name": name,
                "qty": qty,
                "date_purchase": date.today(),
                "expiry_date": expiry_date,
            }
        )
    return bb


def classify_bb_to_cc(
    bb: List[Dict[str, Any]], placements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    place_map = {p["name"]: p["place"] for p in placements}
    cc = []
    for item in bb:
        place = place_map.get(item["name"])
        if place not in {
            "Frigo",
            "Congelateur",
            "MiniPharmacie",
            "Toilette",
            "Cuisine",
        }:
            continue
        cc.append(
            {
                "name": item["name"],
                "qty": item["qty"],
                "expiry_date": item["expiry_date"],
                "location": place,
            }
        )
    return cc
