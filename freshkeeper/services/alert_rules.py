
# freshkeeper/services/alert_rules.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# Public statuses
OK = "OK"
BIENTOT_PERIME = "BIENTOT_PERIME"
PERIME = "PERIME"
STOCK_EPUISÃ‰ = "STOCK_EPUISÃ‰"

@dataclass(frozen=True)
class ProductLite:
    id: int
    name: str
    expiry_date: date | None
    quantity: float | int
    soon_threshold_days: int = 3  # configurable if needed

def compute_status(p: ProductLite, today: date | None = None) -> str:
    """Compute product status based on expiry_date and quantity.
    Rules:
      - If quantity <= 0 -> STOCK_EPUISÃ‰
      - If no expiry date -> OK (based on stock only)
      - If expiry_date < today -> PERIME
      - If 0 <= (expiry_date - today).days <= soon_threshold_days -> BIENTOT_PERIME
      - Else OK
    """
    today = today or date.today()

    if p.quantity is None or float(p.quantity) <= 0:
        return STOCK_EPUISÃ‰

    if p.expiry_date is None:
        return OK

    delta = (p.expiry_date - today).days
    if delta < 0:
        return PERIME
    if 0 <= delta <= p.soon_threshold_days:
        return BIENTOT_PERIME
    return OK


