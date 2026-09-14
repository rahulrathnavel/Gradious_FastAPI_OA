import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, DateTime, Table
from sqlalchemy.orm import relationship
from database import Base

class RoleEnum(str, enum.Enum):
    teacher = "teacher"
    student = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)

    course = relationship("Course", back_populates="modules")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    course = relationship("Course", back_populates="enrollments")

