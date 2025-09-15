from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Lot
from ..schemas.lots import LotOut

router = APIRouter()


@router.get("/lots", response_model=List[LotOut])
def get_lots(db: Session = Depends(get_db)):
    lots = db.query(Lot).all()
    return [LotOut.from_orm_with_delay(l) for l in lots]


class LotOut(BaseModel):
    id: int
    product_name: str
    quantity: float
    expiry_date: Optional[date]
    location: str
    created_at: date
    delai_restant: Optional[int]

    @classmethod
    def from_orm_with_delay(cls, lot):
        return cls(
            id=lot.id,
            product_name=lot.product.name,
            quantity=lot.quantity,
            expiry_date=lot.expiry_date,
            location=lot.location,
            created_at=lot.created_at,
            delai_restant=(
                (lot.expiry_date - lot.created_at).days if lot.expiry_date else None
            ),
        )

    class Config:
        orm_mode = True
