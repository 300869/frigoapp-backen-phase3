from datetime import timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.inventory import InventoryItem
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryRead

router = APIRouter()

# Helper: compute expires_at if missing
async def _compute_expiry(session: AsyncSession, product_id: int, provided: date | None) -> date | None:
    if provided:
        return provided
    # sinon, cherche default_shelf_life_days
    res = await session.execute(select(Product).where(Product.id == product_id))
    prod = res.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    if prod.default_shelf_life_days:
        from datetime import date as d, timedelta
        return d.today() + timedelta(days=prod.default_shelf_life_days)
    return None

# CREATE
@router.post("", response_model=InventoryRead, status_code=201)
async def create_item(
    payload: InventoryCreate,
    current=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_id = current.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # vérifier que le produit existe
    res = await session.execute(select(Product).where(Product.id == payload.product_id))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    expires_at = await _compute_expiry(session, payload.product_id, payload.expires_at)

    obj = InventoryItem(
        user_id=user_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        expires_at=expires_at,
        note=payload.note,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

# LIST (filtres optionnels : expirés / bientôt expirés)
@router.get("", response_model=list[InventoryRead])
async def list_items(
    expired: bool | None = Query(default=None, description="true=seulement expirés, false=seulement non expirés"),
    expiring_in_days: int | None = Query(default=None, ge=1, description="Afficher ceux qui expirent dans N jours"),
    current=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_id = current.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    stmt = select(InventoryItem).where(InventoryItem.user_id == user_id).order_by(InventoryItem.id.desc())

    # Appliquer filtres
    if expired is not None:
        from datetime import date as d
        today = d.today()
        if expired:
            stmt = stmt.where(InventoryItem.expires_at.is_not(None), InventoryItem.expires_at < today)
        else:
            stmt = stmt.where((InventoryItem.expires_at.is_(None)) | (InventoryItem.expires_at >= today))

    if expiring_in_days is not None:
        from datetime import date as d, timedelta
        today = d.today()
        limit = today + timedelta(days=expiring_in_days)
        stmt = stmt.where(InventoryItem.expires_at.is_not(None), InventoryItem.expires_at <= limit)

    result = await session.execute(stmt)
    return list(result.scalars().all())

# READ ONE
@router.get("/{item_id}", response_model=InventoryRead)
async def get_item(
    item_id: int,
    current=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_id = current.get("id")
    result = await session.execute(
        select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.user_id == user_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return obj

# UPDATE (partial)
@router.patch("/{item_id}", response_model=InventoryRead)
async def update_item(
    item_id: int,
    payload: InventoryUpdate,
    current=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_id = current.get("id")
    result = await session.execute(
        select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.user_id == user_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    data = payload.model_dump(exclude_unset=True)
    # si quantity tombe à 0 → on laisse (ça peut signifier “bientôt supprimé”)
    for k, v in data.items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return obj

# DELETE
@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    current=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_id = current.get("id")
    result = await session.execute(
        select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.user_id == user_id)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    await session.delete(obj)
    await session.commit()
    return None
