from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from database import SessionLocal
except ImportError:
    from .database import SessionLocal  # fallback if project layout differs

router = APIRouter(prefix="/storage_locations", tags=["storage_locations"])


class StorageLocation(BaseModel):
    id: int
    name: str
    kind: str
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[StorageLocation])
def list_locations(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            text(
                "SELECT id, name, kind, parent_id FROM storage_locations ORDER BY kind, name"
            )
        )
        .mappings()
        .all()
    )
    return rows
