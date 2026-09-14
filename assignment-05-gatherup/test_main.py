import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app, init_db
from database import Base, get_db
from datetime import datetime, timedelta, timezone

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingAsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingAsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def run_around_tests():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_create_event():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        resp = await ac.post("/events", json={
            "title": "Party",
            "event_date": future_date,
            "max_attendees": 10
        }, headers={"X-User-Id": "1"})
        assert resp.status_code == 201

@pytest.mark.asyncio
async def test_invalid_event_date_and_capacity():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        resp = await ac.post("/events", json={
            "title": "Party",
            "event_date": past_date,
            "max_attendees": 10
        }, headers={"X-User-Id": "1"})
        assert resp.status_code == 422 # Pydantic validation fails

        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        resp2 = await ac.post("/events", json={
            "title": "Party",
            "event_date": future_date,
            "max_attendees": 0
        }, headers={"X-User-Id": "1"})
        assert resp2.status_code == 422

@pytest.mark.asyncio
async def test_rsvp_and_capacity():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        event_resp = await ac.post("/events", json={
            "title": "Party",
            "event_date": future_date,
            "max_attendees": 1
        }, headers={"X-User-Id": "1"})
        event_id = event_resp.json()["id"]

        # Valid RSVP
        rsvp_resp1 = await ac.post(f"/events/{event_id}/rsvp", json={"email": "a@test.com"}, headers={"X-User-Id": "2"})
        assert rsvp_resp1.status_code == 201

        # Duplicate
        rsvp_resp_dup = await ac.post(f"/events/{event_id}/rsvp", json={"email": "b@test.com"}, headers={"X-User-Id": "2"})
        assert rsvp_resp_dup.status_code == 400

        # Full capacity
        rsvp_resp_full = await ac.post(f"/events/{event_id}/rsvp", json={"email": "c@test.com"}, headers={"X-User-Id": "3"})
        assert rsvp_resp_full.status_code == 400

        # Invalid Email
        rsvp_resp_email = await ac.post(f"/events/{event_id}/rsvp", json={"email": "invalid"}, headers={"X-User-Id": "4"})
        assert rsvp_resp_email.status_code == 422

@pytest.mark.asyncio
async def test_cancel_event():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        event_resp = await ac.post("/events", json={
            "title": "Party",
            "event_date": future_date,
            "max_attendees": 10
        }, headers={"X-User-Id": "1"})
        event_id = event_resp.json()["id"]

        # Unauthorized cancel
        del_resp = await ac.delete(f"/events/{event_id}", headers={"X-User-Id": "2"})
        assert del_resp.status_code == 403

        # Authorized cancel
        del_resp2 = await ac.delete(f"/events/{event_id}", headers={"X-User-Id": "1"})
        assert del_resp2.status_code == 204

        # Cannot RSVP to cancelled
        rsvp_resp = await ac.post(f"/events/{event_id}/rsvp", json={"email": "a@test.com"}, headers={"X-User-Id": "2"})
        assert rsvp_resp.status_code == 400

        # Cancelled events hidden
        list_resp = await ac.get("/events")
        assert len(list_resp.json()) == 0

