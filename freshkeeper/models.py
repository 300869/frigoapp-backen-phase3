from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

from .database import Base

# If your project already defines Base elsewhere, import it instead
Base = declarative_base()


# ---------- USER ----------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


# ---------- CATEGORY ----------
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)


# ---------- PRODUCT ----------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", lazy="joined")


# ---------- INVENTORY ----------
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    expiration_date = Column(Date, nullable=True)

    user = relationship("User", lazy="joined")
    product = relationship("Product", lazy="joined")


# ---------- CONSUMPTION ----------
class Consumption(Base):
    __tablename__ = "consumptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    consumed_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    note = Column(Text, nullable=True)

    user = relationship("User", lazy="joined")
    product = relationship("Product", lazy="joined")


# -------- LOTS ------------
class Lot(Base):
    __tablename__ = "lots"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    expiry_date = Column(Date, nullable=True)
    location = Column(String, nullable=False)
    created_at = Column(Date, nullable=False, default=date.today)

    product = relationship("Product")


# ---------- ALERT ----------
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # PostgreSQL enums exist in DB; we use strings compatible with those values:
    # kind: PERIME | BIENTOT | STOCK_BAS
    # status: OPEN | DONE
    kind = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)

    severity = Column(String(16), nullable=False, default="LOW")
    message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    due_at = Column(Date, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    product = relationship("Product", lazy="joined")
    user = relationship("User", lazy="joined")
