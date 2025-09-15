from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from freshkeeper.core.security import get_current_user
from freshkeeper.db.session import get_session
from freshkeeper.models.user import User

router = APIRouter()


@router.get("/me")
async def get_me(
    current=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # current contient {"id": 1, "email": "<mail du token>"}
    email = current.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    q = await session.execute(select(User).where(User.email == email))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at,
    }

