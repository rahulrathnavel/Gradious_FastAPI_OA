from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
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

class ModuleCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str
    order_index: int

class ModuleResponse(ModuleCreate):
    id: int

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    price: float = Field(..., ge=0)
    modules: list[ModuleCreate] = []

class CourseUpdate(BaseModel):
    description: str | None = None
    price: float | None = Field(None, ge=0)

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: float
    instructor_id: int

    class Config:
        from_attributes = True

class CourseWithModulesResponse(CourseResponse):
    modules: list[ModuleResponse]

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True

