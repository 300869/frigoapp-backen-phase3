from datetime import date
from typing import Literal

Color = Literal["rouge", "jaune", "vert"]


def days_to_expire(expiry_date: date, today: date | None = None) -> int:
    today = today or date.today()
    return (expiry_date - today).days


def color_for_expiry(expiry_date: date, today: date | None = None) -> Color:
    d = days_to_expire(expiry_date, today)
    if d <= 3:
        return "rouge"
    if d <= 10:
        return "jaune"
    return "vert"


def move_expired_to_history(db, Product, History, Alert) -> int:
    # Déplace produits expirés (expiry_date < today) vers l'historique et crée une alerte 'expired'
    today = date.today()
    q = db.query(Product).filter(Product.expiry_date < today)
    moved = 0
    for p in q.all():
        h = History(
            name=p.name,
            quantity=p.quantity,
            expiry_date=p.expiry_date,
            created_at=p.created_at,
            moved_at=today,
            location_id=p.location_id,
        )
        db.add(h)
        db.add(Alert(kind="expired", due_date=p.expiry_date, product_id=p.id))
        db.delete(p)
        moved += 1
    db.commit()
    return moved


def refresh_colors_and_alerts(db, Product, Alert) -> int:
    # Met à jour les alertes 'soon' (<=10j) et 'critical' (<=3j)
    today = date.today()
    items = db.query(Product).all()
    for p in items:
        d = (p.expiry_date - today).days
        if d <= 3:
            db.add(Alert(kind="critical", due_date=p.expiry_date, product_id=p.id))
        elif d <= 10:
            db.add(Alert(kind="soon", due_date=p.expiry_date, product_id=p.id))
        # Exemple si vous avez Product.color :
        # if d <= 3: p.color = "rouge"
        # elif d <= 10: p.color = "jaune"
        # else: p.color = "vert"
    db.commit()
    return len(items)
