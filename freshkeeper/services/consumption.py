from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from freshkeeper.models.consumption import Consumption
from freshkeeper.schemas.consumption import ConsumptionCreate


def create_consumption(db: Session, payload: ConsumptionCreate) -> Consumption:
    obj = Consumption(
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit=payload.unit,
        consumed_at=payload.consumed_at or datetime.now(timezone.utc),
    )
    db.add(obj)
    try:
        db.commit()
    except (IntegrityError, SQLAlchemyError):
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def list_consumptions(db: Session, product_id: int | None = None) -> list[Consumption]:
    stmt = select(Consumption)
    if product_id is not None:
        stmt = stmt.where(Consumption.product_id == product_id)
    return list(db.execute(stmt).scalars().all())
