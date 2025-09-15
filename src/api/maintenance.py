from fastapi import APIRouter

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/expire-now")
def maintenance_expire_now():
    return {"archived_from_trash": 0, "moved_to_trash": 0}
