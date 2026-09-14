from pydantic import BaseModel, Field, EmailStr
from typing import Any

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1)
    ingredients: list[str] = Field(..., min_length=1)
    instructions: str = Field(..., min_length=1)
    prep_time: int = Field(..., gt=0)

class RecipeUpdate(BaseModel):
    ingredients: list[str] | None = Field(None, min_length=1)
    instructions: str | None = Field(None, min_length=1)

class RecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: list[str]
    instructions: str
    prep_time: int
    user_id: int

    class Config:
        from_attributes = True

class TrendingRecipeResponse(RecipeResponse):
    like_count: int

class LikeResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int

    class Config:
        from_attributes = True
