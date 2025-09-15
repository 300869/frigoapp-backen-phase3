import os

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, future=True)


class Alert(BaseModel):
    id: int
    product_id: int
    kind: str
    due_date: str
    message: str | None = None
    is_active: bool


router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[Alert])
def list_alerts(
    status: str | None = Query(None, alias="status"), only_active: bool = True
):
    try:
        conditions = []
        params = {}
        if status:
            conditions.append("kind = :k")
            params["k"] = status
        if only_active:
            conditions.append("is_active = TRUE")
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        sql = f"""
            SELECT id, product_id, kind, due_date, message, is_active
            FROM alerts
            {where}
            ORDER BY due_date DESC, id DESC
        """
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return [Alert(**dict(r)) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
