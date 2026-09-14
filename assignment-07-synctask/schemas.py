from pydantic import BaseModel, Field
from models import StatusEnum

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str | None = Field(None, max_length=500)
    status: StatusEnum = StatusEnum.todo
    priority: int = Field(..., ge=1, le=5)

class TaskUpdate(BaseModel):
    status: StatusEnum

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: StatusEnum
    priority: int
    project_id: int

    class Config:
        from_attributes = True

