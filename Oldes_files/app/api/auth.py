from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import get_session
from app.models.user import User

router = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
async def register(
    email: str,
    password: str,
    full_name: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    q = await session.execute(select(User).where(User.email == email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=pwd_ctx.hash(password),
        created_at=datetime.utcnow(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at,
    }


@router.post("/login")
def login(email: str, password: str):
    token = create_access_token(subject=email)
    return {"access_token": token, "token_type": "bearer", "expires_in": 3600}
