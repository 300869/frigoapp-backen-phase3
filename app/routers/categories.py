from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=schemas.CategoryRead, status_code=201)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Category).filter(models.Category.name == payload.name).first()
    if exists:
        raise HTTPException(422, detail="La catégorie existe déjà")
    obj = models.Category(name=payload.name)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=list[schemas.CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()
