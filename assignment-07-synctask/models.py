import enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class StatusEnum(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.todo, nullable=False)
    priority = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("Project", back_populates="tasks")

