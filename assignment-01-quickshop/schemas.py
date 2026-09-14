from pydantic import BaseModel, EmailStr, Field
from models import RoleEnum, CategoryEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)
    role: RoleEnum = RoleEnum.user

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: CategoryEnum

class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category: CategoryEnum | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    category: CategoryEnum

    class Config:
        from_attributes = True

