from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from freshkeeper.database import get_db
from freshkeeper.models import User
from freshkeeper.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
def list_users(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if q:
        like = f"%{q}%"
        query = query.filter((User.email.ilike(like)) | (User.full_name.ilike(like)))
    return query.order_by(User.id.asc()).all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(
            status_code=409, detail="Un utilisateur avec cet email existe dÃ©jÃ ."
        )
    obj = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=payload.hashed_password,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return obj


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    db.delete(obj)
    db.commit()
    return None
