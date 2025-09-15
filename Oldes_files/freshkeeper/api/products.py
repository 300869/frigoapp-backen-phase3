from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from freshkeeper.core.security import get_current_user
from freshkeeper.db.session import get_session
from freshkeeper.models.product import Product
from freshkeeper.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


@router.post("", response_model=ProductRead, status_code=201)
async def create_product(
    payload: ProductCreate,
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    obj = Product(
        name=payload.name,
        category_id=payload.category_id,
        barcode=payload.barcode,
        default_shelf_life_days=payload.default_shelf_life_days,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("", response_model=list[ProductRead])
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * page_size
    result = await session.execute(
        select(Product).order_by(Product.id).offset(offset).limit(page_size)
    )
    return list(result.scalars().all())


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)

    await session.commit()
    await session.refresh(obj)
    return obj


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")

    await session.delete(obj)
    await session.commit()
    return None

