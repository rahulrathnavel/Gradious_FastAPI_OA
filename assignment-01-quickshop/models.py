import enum
from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum
from database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

class CategoryEnum(str, enum.Enum):
    electronics = "electronics"
    fashion = "fashion"
    grocery = "grocery"
    books = "books"
    home = "home"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.user, nullable=False)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(SQLEnum(CategoryEnum), nullable=False)

