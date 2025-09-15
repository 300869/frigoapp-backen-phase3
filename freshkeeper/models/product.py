from sqlalchemy import Column, ForeignKey, Integer, String

from freshkeeper.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=True, index=True
    )
    default_shelf_life_days = Column(Integer, nullable=True)
