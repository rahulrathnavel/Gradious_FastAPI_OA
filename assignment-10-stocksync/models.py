import enum
from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    manager = "manager"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit_cost = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, nullable=False)

class Inventory(Base):
    __tablename__ = "inventory"

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), primary_key=True)
    quantity = Column(Integer, default=0, nullable=False)

