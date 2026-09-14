import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DeviceTypeEnum(str, enum.Enum):
    light = "light"
    thermostat = "thermostat"
    fan = "fan"
    camera = "camera"
    lock = "lock"

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(DeviceTypeEnum), nullable=False)
    room = Column(String, nullable=False)
    state = Column(String, nullable=False)

    logs = relationship("DeviceLog", back_populates="device", cascade="all, delete-orphan", order_by="desc(DeviceLog.timestamp)")

class DeviceLog(Base):
    __tablename__ = "device_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    old_state = Column(String, nullable=True)
    new_state = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    device = relationship("Device", back_populates="logs")

