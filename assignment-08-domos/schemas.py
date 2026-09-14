from pydantic import BaseModel, Field
from datetime import datetime
from models import DeviceTypeEnum

class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: DeviceTypeEnum
    room: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)

class DeviceStateUpdate(BaseModel):
    state: str = Field(..., min_length=1)

class DeviceResponse(BaseModel):
    id: int
    name: str
    type: DeviceTypeEnum
    room: str
    state: str

    class Config:
        from_attributes = True

class DeviceLogResponse(BaseModel):
    id: int
    device_id: int
    old_state: str | None = None
    new_state: str
    timestamp: datetime

    class Config:
        from_attributes = True

