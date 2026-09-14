import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class WorkoutTypeEnum(str, enum.Enum):
    cardio = "cardio"
    strength = "strength"
    yoga = "yoga"
    hiit = "hiit"
    sports = "sports"

class FitnessLevelEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    fitness_level = Column(SQLEnum(FitnessLevelEnum), nullable=False)

    workouts = relationship("Workout", back_populates="owner")

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(WorkoutTypeEnum), nullable=False)
    duration = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="workouts")
