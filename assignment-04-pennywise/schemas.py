from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from models import TransactionTypeEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)
    strict_mode: bool = False
    scope: str = "read_transactions write_transactions"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    strict_mode: bool
    scope: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []

class TransactionCreate(BaseModel):
    amount: float
    category: str = Field(..., min_length=1)
    description: str | None = None
    type: TransactionTypeEnum
    
    @field_validator('amount')
    def amount_must_not_be_zero(cls, v):
        if v == 0:
            raise ValueError('amount must not be 0')
        return v

class TransactionUpdate(BaseModel):
    amount: float | None = None
    category: str | None = Field(None, min_length=1)
    description: str | None = None
    type: TransactionTypeEnum | None = None

    @field_validator('amount')
    def amount_must_not_be_zero(cls, v):
        if v is not None and v == 0:
            raise ValueError('amount must not be 0')
        return v

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    category: str
    description: str | None = None
    type: TransactionTypeEnum
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool

    class Config:
        from_attributes = True

class FinancialSummary(BaseModel):
    total_income: float
    total_expense: float
    current_balance: float

