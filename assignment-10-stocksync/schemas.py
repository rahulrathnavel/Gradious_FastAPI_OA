from pydantic import BaseModel, Field, EmailStr
from models import RoleEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)
    role: RoleEnum

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

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    unit_cost: float = Field(..., ge=0)
    selling_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)

class ItemAdminResponse(BaseModel):
    id: int
    name: str
    unit_cost: float
    selling_price: float
    quantity: int

    class Config:
        from_attributes = True

class ItemManagerResponse(BaseModel):
    id: int
    name: str
    selling_price: float
    quantity: int

    class Config:
        from_attributes = True

class StockUpdate(BaseModel):
    change: int

class ValuationResponse(BaseModel):
    total_inventory_value: float

