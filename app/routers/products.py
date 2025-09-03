import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.alerts_service import close_alerts, compute_kind, ensure_open_alert

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=schemas.ProductRead, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Vérifie la catégorie
    cat = db.get(models.Category, payload.category_id)
    if not cat:
        raise HTTPException(422, detail="category_id invalide")

    # Crée le produit
    obj = models.Product(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    # Auto-alerte (mode SAFE)
    try:
        kind = compute_kind(obj.expiry_date, obj.quantity)
        if kind:
            due_at = obj.expiry_date if kind in ("PERIME", "BIENTOT") else None
            ensure_open_alert(db, product_id=obj.id, kind=kind, due_at=due_at)
    except Exception as e:
        logging.exception("Échec auto-alerte à la création du produit: %s", e)

    return obj


@router.get("", response_model=list[schemas.ProductRead])
def list_products(db: Session = Depends(get_db)):
    # Pydantic v2 + from_attributes=True dans schemas -> sérialisation ORM OK
    return db.query(models.Product).order_by(models.Product.id.asc()).all()


@router.put("/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, detail="Produit introuvable")

    data = payload.model_dump(exclude_unset=True)

    # Si on change de catégorie, valider la nouvelle
    if "category_id" in data and data["category_id"] is not None:
        cat = db.get(models.Category, data["category_id"])
        if not cat:
            raise HTTPException(422, detail="category_id invalide")

    for k, v in data.items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

    # --- Logique d'alerte robuste (SAFE) ---
    try:
        # 1) Si le stock repasse > 0 -> fermer STOCK_BAS immédiatement
        if obj.quantity is not None and obj.quantity > 0:
            close_alerts(db, product_id=obj.id, kinds=["STOCK_BAS"])

        # 2) Calculer l'état lié à la péremption
        kind = compute_kind(obj.expiry_date, obj.quantity)

        if kind in ("PERIME", "BIENTOT"):
            due_at = obj.expiry_date
            ensure_open_alert(db, product_id=obj.id, kind=kind, due_at=due_at)
        elif kind is None:
            # Plus d'alerte de péremption nécessaire -> fermer celles restantes
            close_alerts(db, product_id=obj.id, kinds=["PERIME", "BIENTOT"])

    except Exception as e:
        logging.exception("Échec auto-alerte à la mise à jour du produit: %s", e)

    return obj


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, detail="Produit introuvable")
    db.delete(obj)
    db.commit()
