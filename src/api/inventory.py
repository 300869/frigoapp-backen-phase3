from fastapi import APIRouter

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/status")
def inventory_status():
    return [
        {
            "id": 1,
            "product_name": "Exemple",
            "quantity": 1,
            "expiry_date": "2025-09-30",
            "days_to_expire": 10,
            "status_color": "green",
            "location": "fridge",
        }
    ]
