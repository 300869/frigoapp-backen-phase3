from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from freshkeeper.database import get_db
from freshkeeper.models import Category
from freshkeeper.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryRead])
def list_categories(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Category)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Category.name.ilike(like)) | (Category.description.ilike(like))
        )
    return query.order_by(Category.name.asc()).all()


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="La catÃ©gorie existe dÃ©jÃ .")
    obj = Category(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CatÃ©gorie introuvable.")
    return obj


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)
):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CatÃ©gorie introuvable.")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CatÃ©gorie introuvable.")
    db.delete(obj)
    db.commit()
    return None
