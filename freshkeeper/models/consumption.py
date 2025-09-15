from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from freshkeeper.database import Base


class Consumption(Base):
    __tablename__ = "consumption"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(16), nullable=False)
    consumed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
