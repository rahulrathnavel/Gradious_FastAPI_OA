from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from models import EventStatusEnum
import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    event_date: datetime
    max_attendees: int = Field(..., gt=0)

    @field_validator('event_date')
    def event_date_must_be_future(cls, v):
        # Allow naive datetimes by converting to UTC or assuming UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError('event_date must be in the future')
        return v

class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    event_date: datetime
    max_attendees: int
    creator_id: int
    status: EventStatusEnum

    class Config:
        from_attributes = True

class RSVPMake(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, v):
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

class RSVPResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    email: str

    class Config:
        from_attributes = True

