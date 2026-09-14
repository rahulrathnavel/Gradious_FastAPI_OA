from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from models import WorkoutTypeEnum, FitnessLevelEnum

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)
    fitness_level: FitnessLevelEnum

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    fitness_level: FitnessLevelEnum

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class WorkoutCreate(BaseModel):
    type: WorkoutTypeEnum
    duration: int = Field(..., gt=0)
    calories_burned: float = Field(..., ge=0)

class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    type: WorkoutTypeEnum
    duration: int
    calories_burned: float
    created_at: datetime

    class Config:
        from_attributes = True

class WorkoutStats(BaseModel):
    total_calories_burned: float

