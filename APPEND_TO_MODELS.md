    # Ajout aux modèles SQLAlchemy (app/models.py)

    Copie/colle ce bloc **en bas de ton fichier `app/models.py`** après `from .database import Base` :

    ```python
    # --------- ADD THESE MODELS IF NOT PRESENT ---------
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime

# Category used by products (one-to-many)
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # If you already have a Product model, you can uncomment this to enable reverse relation:
    # products = relationship("Product", back_populates="category", cascade="all,delete", passive_deletes=True)

# Track what a user consumes from their stock
class Consumption(Base):
    __tablename__ = "consumptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    consumed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

# Alerts generated for expiring / out-of-stock items
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False, index=True)  # "OK" | "Bientôt périmé" | "Périmé" | "Stock épuisé"
    message = Column(Text, nullable=True)
    expires_at = Column(Date, nullable=True)
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    ```

    > Si tu utilises Alembic: lance `alembic revision --autogenerate -m "add categories/consumptions/alerts"` puis `alembic upgrade head`.
