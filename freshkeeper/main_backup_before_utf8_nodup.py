import os
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="FreshKeeper API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------- Utils ----------------------
def today_str() -> str:
    return date.today().isoformat()


def normalize_name(name: str) -> str:
    n = (name or "").strip().lower()
    if n.endswith("es"):
        n = n[:-2]
    elif n.endswith("s"):
        n = n[:-1]
    return n.capitalize()


# ---------------------- ModÃ¨les ----------------------
class ProductIn(BaseModel):
    name: str


class ProductOut(BaseModel):
    id: int
    name: str


class ProductUpdateIn(BaseModel):
    name: str


class AlertKind(str, Enum):
    EXPIRED = "EXPIRED"
    SOON = "SOON"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    CRITICAL = "CRITICAL"


class AlertOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    kind: AlertKind
    due_date: Optional[str] = None


class LotIn(BaseModel):
    name: Optional[str] = None
    product_id: Optional[int] = None
    quantity: float = 1
    unit: str = "pcs"
    purchased_at: Optional[str] = None  # YYYY-MM-DD
    shelf_life_days: Optional[int] = 4
    expiry_date: Optional[str] = None
    location: Optional[str] = None


class LotConsumeIn(BaseModel):
    quantity: float


class LotMoveIn(BaseModel):
    location: str


class LotOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: float
    consumed: float
    unit: str
    purchased_at: Optional[str] = None
    shelf_life_days: Optional[int] = None
    expiry_date: Optional[str] = None
    location: Optional[str] = None


ShoppingStatus = Literal["open", "pending", "done"]


class ShoppingItemIn(BaseModel):
    name: str
    quantity: float = 1
    unit: str = "pcs"


class ShoppingItemOut(BaseModel):
    id: int
    product_id: Optional[int] = None
    product_name: str
    quantity: float
    unit: str
    status: ShoppingStatus
    created_at: str


class ClassifyIn(BaseModel):
    location: str  # FRIDGE, FREEZER, PANTRY1..5


class InventoryItemOut(BaseModel):
    product_id: int
    product_name: str
    location: str
    total: float
    unit: str


# ---------------------- DB mÃ©moire ----------------------
_PRODUCTS_DB: List[ProductOut] = []
_LOTS_DB: List[LotOut] = []
_ALERTS_DB: List[AlertOut] = []
_SHOPPING_DB: List[ShoppingItemOut] = []
_HISTORY_DB: List[Dict[str, Any]] = []  # simple historique

_NEXT_IDS = {"product": 1, "lot": 1, "alert": 1, "shopping": 1, "history": 1}
_STORAGE_LOCATIONS = [
    "FRIDGE",
    "FREEZER",
    "PANTRY1",
    "PANTRY2",
    "PANTRY3",
    "PANTRY4",
    "PANTRY5",
]


def _get_or_create_product(name: str) -> ProductOut:
    global _NEXT_IDS
    norm = normalize_name(name)
    for p in _PRODUCTS_DB:
        if normalize_name(p.name) == norm:
            return p
    p = ProductOut(id=_NEXT_IDS["product"], name=norm)
    _NEXT_IDS["product"] += 1
    _PRODUCTS_DB.append(p)
    return p


def _add_lot(
    product: ProductOut,
    qty: float,
    unit: str,
    purchased: Optional[str],
    shelf: Optional[int],
    location: Optional[str],
    expiry_date: Optional[str] = None,
) -> LotOut:
    global _NEXT_IDS
    if not purchased:
        purchased = today_str()
    exp = expiry_date
    if exp is None and shelf is not None:
        try:
            d = datetime.strptime(purchased, "%Y-%m-%d").date()
            exp = (d + timedelta(days=shelf)).isoformat()
        except Exception:
            exp = None
    lot = LotOut(
        id=_NEXT_IDS["lot"],
        product_id=product.id,
        product_name=product.name,
        quantity=qty,
        consumed=0,
        unit=unit or "pcs",
        purchased_at=purchased,
        shelf_life_days=shelf,
        expiry_date=exp,
        location=location,
    )
    _NEXT_IDS["lot"] += 1
    _LOTS_DB.append(lot)
    return lot


def _add_shopping(
    name: str, qty: float, unit: str, status: ShoppingStatus
) -> ShoppingItemOut:
    global _NEXT_IDS
    item = ShoppingItemOut(
        id=_NEXT_IDS["shopping"],
        product_id=None,
        product_name=normalize_name(name),
        quantity=qty,
        unit=unit or "pcs",
        status=status,
        created_at=datetime.utcnow().isoformat(),
    )
    _NEXT_IDS["shopping"] += 1
    _SHOPPING_DB.append(item)
    return item


def _days_to_expiry(expiry: Optional[str]) -> Optional[int]:
    if not expiry:
        return None
    try:
        d = datetime.strptime(expiry, "%Y-%m-%d").date()
        return (d - date.today()).days
    except Exception:
        return None


def _move_expired_to_history() -> int:
    global _LOTS_DB, _HISTORY_DB, _NEXT_IDS, _ALERTS_DB
    kept = []
    moved = 0
    for l in _LOTS_DB:
        days = _days_to_expiry(l.expiry_date)
        if days is not None and days < 0:
            _HISTORY_DB.append(
                {
                    "id": _NEXT_IDS["history"],
                    "product_id": l.product_id,
                    "product_name": l.product_name,
                    "quantity": l.quantity,
                    "unit": l.unit,
                    "expired_at": l.expiry_date,
                    "moved_at": today_str(),
                    "location": l.location,
                }
            )
            _NEXT_IDS["history"] += 1
            _ALERTS_DB.append(
                AlertOut(
                    id=_NEXT_IDS["alert"],
                    product_id=l.product_id,
                    product_name=l.product_name,
                    kind=AlertKind.EXPIRED,
                    due_date=l.expiry_date,
                )
            )
            _NEXT_IDS["alert"] += 1
            moved += 1
        else:
            kept.append(l)
    _LOTS_DB = kept
    return moved


def _refresh_alerts() -> int:
    global _ALERTS_DB, _NEXT_IDS
    count = 0
    for l in _LOTS_DB:
        d = _days_to_expiry(l.expiry_date)
        if d is None:
            continue
        if d <= 3:
            _ALERTS_DB.append(
                AlertOut(
                    id=_NEXT_IDS["alert"],
                    product_id=l.product_id,
                    product_name=l.product_name,
                    kind=AlertKind.CRITICAL,
                    due_date=l.expiry_date,
                )
            )
            _NEXT_IDS["alert"] += 1
            count += 1
        elif d <= 10:
            _ALERTS_DB.append(
                AlertOut(
                    id=_NEXT_IDS["alert"],
                    product_id=l.product_id,
                    product_name=l.product_name,
                    kind=AlertKind.SOON,
                    due_date=l.expiry_date,
                )
            )
            _NEXT_IDS["alert"] += 1
            count += 1
    return count


# ---------------------- Seed (dev) ----------------------
ENV = os.getenv("FRESHKEEPER_ENV", "prod").lower()


def _seed_if_empty():
    global _ALERTS_DB, _NEXT_IDS
    if not _PRODUCTS_DB:
        p1 = _get_or_create_product("Banane")
        p2 = _get_or_create_product("Pomme")
        p3 = _get_or_create_product("Lait")
        _add_lot(p1, 6, "pcs", today_str(), 4, "PANTRY1")
        _add_lot(p2, 4, "pcs", today_str(), 7, "FRIDGE")
        _ALERTS_DB.append(
            AlertOut(
                id=_NEXT_IDS["alert"],
                product_id=p1.id,
                product_name=p1.name,
                kind=AlertKind.SOON,
                due_date=(date.today() + timedelta(days=2)).isoformat(),
            )
        )
        _NEXT_IDS["alert"] += 1
        _add_shopping("Riz", 1, "kg", "open")


@app.on_event("startup")
def _on_startup():
    if ENV == "dev":
        _seed_if_empty()


# ---------------------- Health ----------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------- Produits ----------------------
@app.get("/products", response_model=List[ProductOut])
def list_products():
    return _PRODUCTS_DB


@app.post("/products", response_model=ProductOut)
def create_product(data: ProductIn):
    return _get_or_create_product(data.name)


@app.put("/products/{pid}", response_model=ProductOut)
def rename_product(pid: int, data: ProductUpdateIn):
    for p in _PRODUCTS_DB:
        if p.id == pid:
            p.name = normalize_name(data.name)
            return p
    raise HTTPException(404, "Product not found")


@app.delete("/products/{pid}")
def delete_product(pid: int):
    global _PRODUCTS_DB, _LOTS_DB, _SHOPPING_DB
    if not any(p.id == pid for p in _PRODUCTS_DB):
        raise HTTPException(404, "Product not found")
    _PRODUCTS_DB = [p for p in _PRODUCTS_DB if p.id != pid]
    _LOTS_DB = [l for l in _LOTS_DB if l.product_id != pid]
    _SHOPPING_DB = [s for s in _SHOPPING_DB if s.product_id != pid]
    return {"ok": True}


# ---------------------- Lots ----------------------
@app.get("/lots", response_model=List[LotOut])
def list_lots():
    return _LOTS_DB


@app.post("/lots", response_model=LotOut)
def create_lot(data: LotIn):
    if not data.name and not data.product_id:
        raise HTTPException(400, "Must provide name or product_id")
    product = (
        _get_or_create_product(data.name)
        if data.name
        else next((p for p in _PRODUCTS_DB if p.id == data.product_id), None)
    )
    if not product:
        raise HTTPException(404, "Product not found")
    return _add_lot(
        product=product,
        qty=data.quantity or 1,
        unit=data.unit or "pcs",
        purchased=data.purchased_at or today_str(),
        shelf=(data.shelf_life_days if (data.expiry_date is None) else None),
        location=data.location,
        expiry_date=data.expiry_date,
    )


@app.post("/lots/{lid}/consume", response_model=LotOut)
def consume_lot(lid: int, data: LotConsumeIn):
    for l in _LOTS_DB:
        if l.id == lid:
            l.consumed = min(l.quantity, max(0, (l.consumed or 0) + data.quantity))
            return l
    raise HTTPException(404, "Lot not found")


@app.patch("/lots/{lid}/move", response_model=LotOut)
def move_lot(lid: int, data: LotMoveIn):
    if data.location not in _STORAGE_LOCATIONS:
        raise HTTPException(400, "Invalid location")
    for l in _LOTS_DB:
        if l.id == lid:
            l.location = data.location
            return l
    raise HTTPException(404, "Lot not found")


# ---------------------- Inventaire (par lieu + recherche) ----------------------
@app.get("/inventory", response_model=List[InventoryItemOut])
def inventory(location: Optional[str] = None, q: Optional[str] = None):
    if location and location not in _STORAGE_LOCATIONS:
        raise HTTPException(400, "Invalid location")
    qn = normalize_name(q or "")
    # agrÃ¨ge par (product_id, location)
    agg = {}
    for l in _LOTS_DB:
        rem = max(0, (l.quantity or 0) - (l.consumed or 0))
        if rem <= 0:
            continue
        loc = l.location or "PANTRY1"
        if location and loc != location:
            continue
        if q and qn not in normalize_name(l.product_name):
            continue
        key = (l.product_id, l.product_name, loc, l.unit or "pcs")
        agg[key] = agg.get(key, 0) + rem
    out: List[InventoryItemOut] = []
    for (pid, pname, loc, unit), total in agg.items():
        out.append(
            InventoryItemOut(
                product_id=pid, product_name=pname, location=loc, total=total, unit=unit
            )
        )
    # tri par nom
    out.sort(key=lambda x: (x.location, x.product_name))
    return out


# ---------------------- Alertes ----------------------
@app.get("/alerts", response_model=List[AlertOut])
def list_alerts():
    return _ALERTS_DB


@app.post("/alerts/{alert_id}/ack")
def ack_alert(alert_id: int):
    global _ALERTS_DB
    for i, a in enumerate(_ALERTS_DB):
        if a.id == alert_id:
            del _ALERTS_DB[i]
            return {"ok": True}
    raise HTTPException(404, "Alert not found")


# ---------------------- Emplacements ----------------------
@app.get("/storage_locations", response_model=List[str])
def list_storage_locations():
    return _STORAGE_LOCATIONS


# ---------------------- Shopping list ----------------------
@app.get("/shopping_list", response_model=List[ShoppingItemOut])
def get_shopping_list(status: Optional[ShoppingStatus] = None):
    if status:
        return [s for s in _SHOPPING_DB if s.status == status]
    return _SHOPPING_DB


@app.post("/shopping_list", response_model=ShoppingItemOut)
def add_shopping_item(data: ShoppingItemIn):
    norm = normalize_name(data.name)
    for s in _SHOPPING_DB:
        if (
            s.status == "open"
            and normalize_name(s.product_name) == norm
            and s.unit == (data.unit or "pcs")
        ):
            s.quantity += data.quantity or 1
            return s
    return _add_shopping(norm, data.quantity or 1, data.unit or "pcs", "open")


@app.post("/shopping_list/{sid}/buy", response_model=ShoppingItemOut)
def buy_shopping_item(sid: int):
    for s in _SHOPPING_DB:
        if s.id == sid:
            s.status = "pending"
            return s
    raise HTTPException(404, "Shopping item not found")


@app.post("/shopping_list/{sid}/delete")
def delete_shopping_item(sid: int):
    global _SHOPPING_DB
    for i, s in enumerate(_SHOPPING_DB):
        if s.id == sid:
            del _SHOPPING_DB[i]
            return {"ok": True}
    raise HTTPException(404, "Shopping item not found")


@app.post("/shopping_list/{sid}/classify", response_model=LotOut)
def classify_shopping_item(sid: int, data: ClassifyIn):
    if data.location not in _STORAGE_LOCATIONS:
        raise HTTPException(400, "Invalid location")
    for i, s in enumerate(_SHOPPING_DB):
        if s.id == sid:
            product = _get_or_create_product(s.product_name)
            lot = _add_lot(product, s.quantity, s.unit, today_str(), 4, data.location)
            s.status = "done"
            return lot
    raise HTTPException(404, "Shopping item not found")


# ---------------------- Propositions ----------------------
@app.get("/suggested_purchases", response_model=List[ShoppingItemOut])
def suggested_purchases(threshold: int = 0):
    suggestions = []
    by_product = {}
    for l in _LOTS_DB:
        by_product.setdefault(l.product_id, 0)
        by_product[l.product_id] += max(0, l.quantity - l.consumed)
    for p in _PRODUCTS_DB:
        remaining = by_product.get(p.id, 0)
        if remaining <= threshold:
            suggestions.append(
                ShoppingItemOut(
                    id=0,
                    product_id=p.id,
                    product_name=p.name,
                    quantity=1,
                    unit="pcs",
                    status="open",
                    created_at=datetime.utcnow().isoformat(),
                )
            )
    return suggestions


@app.get("/recommendations", response_model=List[ShoppingItemOut])
def recommendations(days: int = 60):
    cutoff = date.today() - timedelta(days=days)
    counts = {}
    for l in _LOTS_DB:
        try:
            d = datetime.strptime(l.purchased_at or today_str(), "%Y-%m-%d").date()
        except Exception:
            d = date.today()
        if d >= cutoff:
            counts[l.product_name] = counts.get(l.product_name, 0) + l.quantity
    items = sorted(counts.items(), key=lambda x: -x[1])[:5]
    out = []
    for name, _ in items:
        out.append(
            ShoppingItemOut(
                id=0,
                product_id=None,
                product_name=name,
                quantity=1,
                unit="pcs",
                status="open",
                created_at=datetime.utcnow().isoformat(),
            )
        )
    return out


# ---------------------- Router SHOPPING (points 1â†’5) ----------------------
shopping_router = APIRouter(prefix="/shopping", tags=["shopping"])


class ProductCreateIn(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    expiry_date: Optional[str] = None
    location: Optional[str] = None


@shopping_router.post("/inventory/create")
def create_inventory_item(item: ProductCreateIn):
    # Validation if/if not
    if (
        not item.name
        or item.quantity <= 0
        or (item.expiry_date is None and item.location is None)
    ):
        raise HTTPException(422, "DonnÃ©es invalides (nom/quantitÃ©/infos manquantes).")
    p = _get_or_create_product(item.name)
    if item.location and item.location not in _STORAGE_LOCATIONS:
        raise HTTPException(422, "Emplacement invalide.")
    _add_lot(
        p,
        item.quantity,
        "pcs",
        today_str(),
        None,
        item.location,
        expiry_date=item.expiry_date,
    )
    return {"ok": True, "product_id": p.id}


@shopping_router.post("/analyze/refresh")
def analyze_refresh():
    moved = _move_expired_to_history()
    scanned = _refresh_alerts()
    return {"expired_moved": moved, "alerts_added": scanned}


class AAUserRow(BaseModel):
    name: str
    qty: float = 0


class AABuildIn(BaseModel):
    rows: List[AAUserRow] = []


@shopping_router.post("/aa/build")
def build_aa(payload: AABuildIn):
    # Base: produits vus en historique mais presque absents du stock
    hist_names = {h["product_name"] for h in _HISTORY_DB}
    by_name_qty: Dict[str, float] = {}
    for l in _LOTS_DB:
        by_name_qty[l.product_name] = by_name_qty.get(l.product_name, 0) + max(
            0, (l.quantity or 0) - (l.consumed or 0)
        )

    aa: Dict[str, Dict[str, Any]] = {}
    for name in hist_names:
        if by_name_qty.get(name, 0) < 1:
            aa[name] = {"suggested_qty": 1.0}

    # Fusion avec saisies utilisateur
    for r in payload.rows:
        nm = normalize_name(r.name)
        if nm in aa:
            aa[nm]["suggested_qty"] = max(aa[nm]["suggested_qty"], float(r.qty or 0))
        else:
            aa[nm] = {"suggested_qty": float(r.qty or 0)}

    # Lots (rouge/jaune/vert) selon date d'expiration
    lots = {}
    for name in aa.keys():
        lots[name] = {"rouge": [], "jaune": [], "vert": []}
        for l in _LOTS_DB:
            if normalize_name(l.product_name) == name:
                d = _days_to_expiry(l.expiry_date)
                if d is None:
                    continue
                bucket = "rouge" if d <= 3 else ("jaune" if d <= 10 else "vert")
                lots[name][bucket].append(
                    {
                        "id": l.id,
                        "qty": l.quantity,
                        "days_left": d,
                        "expiry_date": l.expiry_date,
                    }
                )
        for b in ("rouge", "jaune", "vert"):
            lots[name][b].sort(key=lambda x: x["days_left"], reverse=True)

    # Valider: qty>0 => to_buy
    validated = {
        n: {**meta, "status": "to_buy"}
        for n, meta in aa.items()
        if float(meta.get("suggested_qty", 0)) > 0
    }
    return {"aa": validated, "lots": lots}


class PurchaseRow(BaseModel):
    name: str
    qty: float
    expiry_date: Optional[str] = None


class CheckoutIn(BaseModel):
    purchases: List[PurchaseRow]


@shopping_router.post("/bb/checkout")
def checkout_bb(payload: CheckoutIn):
    bb = []
    for r in payload.purchases:
        if r.qty <= 0:
            continue
        bb.append(
            {
                "name": normalize_name(r.name),
                "qty": r.qty,
                "date_purchase": today_str(),
                "expiry_date": r.expiry_date,
            }
        )
    return {"bb": bb}


class PlacementRow(BaseModel):
    name: str
    place: str


class ClassifyIn(BaseModel):
    bb: List[PurchaseRow]
    placements: List[PlacementRow]


@shopping_router.post("/cc/classify")
def classify_cc(payload: ClassifyIn):
    # Map placements
    place_by_name = {
        normalize_name(p.place and p.name): p.place for p in payload.placements
    }
    created_ids = []
    for it in payload.bb:
        nm = normalize_name(it.name)
        place = place_by_name.get(nm)
        if place not in _STORAGE_LOCATIONS:
            raise HTTPException(422, f"Lieu invalide: {place}")
        p = _get_or_create_product(nm)
        lot = _add_lot(
            p, it.qty, "pcs", today_str(), None, place, expiry_date=it.expiry_date
        )
        created_ids.append(lot.id)
    return {"ok": True, "created_lots": created_ids}


# Inclure le routeur shopping
app.include_router(shopping_router)
