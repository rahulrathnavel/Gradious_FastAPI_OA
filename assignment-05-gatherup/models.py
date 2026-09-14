import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from database import Base

class EventStatusEnum(str, enum.Enum):
    upcoming = "upcoming"
    completed = "completed"
    cancelled = "cancelled"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=False)
    max_attendees = Column(Integer, nullable=False)
    creator_id = Column(Integer, nullable=False)
    status = Column(SQLEnum(EventStatusEnum), default=EventStatusEnum.upcoming, nullable=False)

class RSVP(Base):
    __tablename__ = "rsvps"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    email = Column(String, nullable=False) # The invitation email

