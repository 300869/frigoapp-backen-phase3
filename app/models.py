from datetime import date, datetime   # ✅ types Python pour annotations
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
from app.database import Base

class AlertKind(str, enum.Enum):
    PERIME = "PERIME"
    BIENTOT = "BIENTOT"
    STOCK_BAS = "STOCK_BAS"

class AlertStatus(str, enum.Enum):
    OPEN = "OPEN"
    DONE = "DONE"

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    products = relationship("Product", back_populates="category", cascade="all, delete")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    location: Mapped[str] = mapped_column(String(80))

    # ✅ Correction : annotation = date/datetime (Python), colonne = Date/DateTime (SQLAlchemy)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="products")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete")

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    kind: Mapped[AlertKind] = mapped_column(Enum(AlertKind), index=True)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.OPEN, index=True)

    # ✅ Même correction ici
    due_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="alerts")
