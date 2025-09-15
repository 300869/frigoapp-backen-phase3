from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Adaptez ces imports à votre projet
from ..db import get_db
from ..models import Alert, History, Product, StorageLocation
from ..services.alerts_logic import move_expired_to_history, refresh_colors_and_alerts
from ..services.inventory_logic import (
    InventoryError,
    normalize_name,
    validate_new_product,
)
from ..services.shopping_logic import (
    build_base_courses,
    checkout_to_bb,
    classify_bb_to_cc,
    group_lots_by_name_and_expiry,
    merge_user_inputs,
    validate_aa,
)

router = APIRouter(prefix="/shopping", tags=["shopping"])


class ProductIn(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    expiry_date: date
    location_id: Optional[int] = None


@router.post("/inventory/create")
def create_product(item: ProductIn, db=Depends(get_db)):
    try:
        validate_new_product(item.name, item.quantity, item.expiry_date)
    except InventoryError as e:
        raise HTTPException(status_code=422, detail=str(e))
    name = normalize_name(item.name)
    p = Product(
        name=name,
        quantity=item.quantity,
        expiry_date=item.expiry_date,
        location_id=item.location_id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"ok": True, "product_id": p.id}


@router.post("/analyze/refresh")
def analyze_refresh(db=Depends(get_db)):
    moved = move_expired_to_history(db, Product, History, Alert)
    scanned = refresh_colors_and_alerts(db, Product, Alert)
    return {"expired_moved": moved, "products_scanned": scanned}


class AAUserRow(BaseModel):
    name: str
    qty: float = 0


class AABuildIn(BaseModel):
    rows: List[AAUserRow] = []


@router.post("/aa/build")
def build_aa(payload: AABuildIn, db=Depends(get_db)):
    base = build_base_courses(db, Product, History)
    merged = merge_user_inputs(base, [r.model_dump() for r in payload.rows])
    lots = group_lots_by_name_and_expiry(db, Product, merged)
    validated = validate_aa(merged)
    return {"aa": validated, "lots": lots}


class PurchaseRow(BaseModel):
    name: str
    qty: float
    expiry_date: Optional[date] = None


class CheckoutIn(BaseModel):
    purchases: List[PurchaseRow]


@router.post("/bb/checkout")
def checkout_bb(payload: CheckoutIn):
    bb = checkout_to_bb({}, [r.model_dump() for r in payload.purchases])
    return {"bb": bb}


class PlacementRow(BaseModel):
    name: str
    place: str  # Frigo | Congelateur | MiniPharmacie | Toilette | Cuisine


class ClassifyIn(BaseModel):
    bb: List[PurchaseRow]
    placements: List[PlacementRow]


@router.post("/cc/classify")
def classify_cc(payload: ClassifyIn, db=Depends(get_db)):
    bb = [r.model_dump() for r in payload.bb]
    placements = [r.model_dump() for r in payload.placements]
    cc = classify_bb_to_cc(bb, placements)

    loc_map = {}
    locs = db.query(StorageLocation).all()
    for l in locs:
        loc_map[l.name] = l.id

    created_ids = []
    for item in cc:
        loc_id = loc_map.get(item["location"])
        if loc_id is None:
            raise HTTPException(
                status_code=422, detail=f"Lieu invalide: {item['location']}"
            )
        p = Product(
            name=item["name"].lower(),
            quantity=item["qty"],
            expiry_date=item["expiry_date"],
            location_id=loc_id,
        )
        db.add(p)
        db.flush()
        created_ids.append(p.id)

    db.commit()
    return {"ok": True, "created_products": created_ids}
