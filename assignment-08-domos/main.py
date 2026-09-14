from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import models, schemas
from database import engine, get_db
from middleware import RequestTimeMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Domos - Smart Home IoT Manager")
app.add_middleware(RequestTimeMiddleware)

@app.post("/devices", response_model=schemas.DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = models.Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/devices", response_model=list[schemas.DeviceResponse])
def get_devices(room: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Device)
    if room:
        query = query.filter(func.lower(models.Device.room) == room.lower())
    return query.all()

def validate_state(device_type: models.DeviceTypeEnum, state: str):
    valid_states = {
        models.DeviceTypeEnum.light: ["on", "off"],
        models.DeviceTypeEnum.fan: ["on", "off"],
        models.DeviceTypeEnum.lock: ["locked", "unlocked"],
        models.DeviceTypeEnum.camera: ["on", "off"]
    }
    if device_type in valid_states:
        if state.lower() not in valid_states[device_type]:
            return False
    elif device_type == models.DeviceTypeEnum.thermostat:
        try:
            float(state)
        except ValueError:
            return False
    return True

@app.patch("/devices/{id}/state", response_model=schemas.DeviceResponse)
def update_device_state(id: int, state_update: schemas.DeviceStateUpdate, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    if not validate_state(device.type, state_update.state):
        raise HTTPException(status_code=422, detail="Invalid state for device type")
        
    old_state = device.state
    new_state = state_update.state
    
    device.state = new_state
    
    # Create log
    log = models.DeviceLog(device_id=device.id, old_state=old_state, new_state=new_state)
    db.add(log)
    
    db.commit()
    
    # Maintain only latest 10 logs
    logs = db.query(models.DeviceLog).filter(models.DeviceLog.device_id == id).order_by(models.DeviceLog.timestamp.desc()).all()
    if len(logs) > 10:
        for old_log in logs[10:]:
            db.delete(old_log)
        db.commit()
        
    db.refresh(device)
    return device

@app.get("/devices/{id}/logs", response_model=list[schemas.DeviceLogResponse])
def get_device_logs(id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    logs = db.query(models.DeviceLog).filter(models.DeviceLog.device_id == id).order_by(models.DeviceLog.timestamp.desc()).all()
    return logs

@app.delete("/devices/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    db.delete(device)
    db.commit()
    return None

