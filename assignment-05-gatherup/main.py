from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timezone
import models, schemas, database

app = FastAPI(title="GatherUp - Event Management API")

async def init_db():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_db()

def get_current_user_id(x_user_id: int = Header(...)):
    return x_user_id

@app.post("/events", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: schemas.EventCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(database.get_db)
):
    # The Pydantic model handles future date and max_attendees > 0
    event_date_utc = event.event_date
    if event_date_utc.tzinfo is None:
        event_date_utc = event_date_utc.replace(tzinfo=timezone.utc)
        
    db_event = models.Event(
        title=event.title,
        description=event.description,
        event_date=event_date_utc.replace(tzinfo=None), # SQLite stores naive
        max_attendees=event.max_attendees,
        creator_id=user_id
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

@app.get("/events", response_model=list[schemas.EventResponse])
async def get_events(db: AsyncSession = Depends(database.get_db)):
    now = datetime.utcnow()
    result = await db.execute(
        select(models.Event).where(
            models.Event.status == models.EventStatusEnum.upcoming,
            models.Event.event_date > now
        )
    )
    return result.scalars().all()

@app.post("/events/{id}/rsvp", response_model=schemas.RSVPResponse, status_code=status.HTTP_201_CREATED)
async def rsvp_event(
    id: int,
    rsvp: schemas.RSVPMake,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(select(models.Event).where(models.Event.id == id))
    event = result.scalars().first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.status == models.EventStatusEnum.cancelled:
        raise HTTPException(status_code=400, detail="Cannot RSVP to cancelled event")

    # Check for duplicate RSVP
    dup_check = await db.execute(select(models.RSVP).where(models.RSVP.event_id == id, models.RSVP.user_id == user_id))
    if dup_check.scalars().first():
        raise HTTPException(status_code=400, detail="Duplicate RSVP")
        
    # Check capacity
    count_result = await db.execute(select(func.count(models.RSVP.id)).where(models.RSVP.event_id == id))
    current_attendees = count_result.scalar() or 0
    if current_attendees >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event already full")

    new_rsvp = models.RSVP(event_id=id, user_id=user_id, email=rsvp.email)
    db.add(new_rsvp)
    await db.commit()
    await db.refresh(new_rsvp)
    return new_rsvp

@app.get("/events/{id}/attendees", response_model=list[schemas.RSVPResponse])
async def get_attendees(id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Event).where(models.Event.id == id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Event not found")
        
    attendees = await db.execute(select(models.RSVP).where(models.RSVP.event_id == id))
    return attendees.scalars().all()

@app.delete("/events/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_event(
    id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(select(models.Event).where(models.Event.id == id))
    event = result.scalars().first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized event cancellation")
        
    event.status = models.EventStatusEnum.cancelled
    await db.commit()
    return None

