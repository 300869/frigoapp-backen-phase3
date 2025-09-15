from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from freshkeeper.dependencies import get_db
from freshkeeper.schemas.consumption import ConsumptionCreate, ConsumptionOut
from freshkeeper.services.consumption import create_consumption, list_consumptions

router = APIRouter(prefix="/consumptions", tags=["consumptions"])


@router.get("/", response_model=list[ConsumptionOut])
def get_consumptions(
    product_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        return list_consumptions(db, product_id=product_id)
    except SQLAlchemyError as e:
        msg = getattr(e, "orig", None) or str(e)
        raise HTTPException(status_code=500, detail=f"Erreur DB: {msg}")


@router.post("/", response_model=ConsumptionOut, status_code=201)
def post_consumption(payload: ConsumptionCreate, db: Session = Depends(get_db)):
    try:
        return create_consumption(db, payload)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail=f"Violation de contrainte: {str(e.orig)}"
        )
    except SQLAlchemyError as e:
        msg = getattr(e, "orig", None) or str(e)
        raise HTTPException(status_code=500, detail=f"Erreur DB: {msg}")
