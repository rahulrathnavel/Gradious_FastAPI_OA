import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_device_crud():
    resp = client.post("/devices", json={"name": "L1", "type": "light", "room": "Living Room", "state": "off"})
    assert resp.status_code == 201
    d_id = resp.json()["id"]
    
    get_resp = client.get("/devices?room=living room")
    assert len(get_resp.json()) == 1
    
    get_resp2 = client.get("/devices?room=LIVING ROOM")
    assert len(get_resp2.json()) == 1
    
    # State update
    patch_resp = client.patch(f"/devices/{d_id}/state", json={"state": "on"})
    assert patch_resp.status_code == 200
    assert patch_resp.headers.get("X-Process-Time") is not None
    
    # Logs
    log_resp = client.get(f"/devices/{d_id}/logs")
    assert len(log_resp.json()) == 1
    assert log_resp.json()[0]["new_state"] == "on"
    assert log_resp.json()[0]["old_state"] == "off"
    
    # Delete
    del_resp = client.delete(f"/devices/{d_id}")
    assert del_resp.status_code == 204
    assert client.get(f"/devices/{d_id}/logs").status_code == 404

def test_state_validation():
    # light: on/off
    d = client.post("/devices", json={"name": "L1", "type": "light", "room": "A", "state": "off"}).json()
    resp = client.patch(f"/devices/{d['id']}/state", json={"state": "dimmed"})
    assert resp.status_code == 422
    
    # thermostat: numeric
    d2 = client.post("/devices", json={"name": "T1", "type": "thermostat", "room": "A", "state": "70"}).json()
    resp2 = client.patch(f"/devices/{d2['id']}/state", json={"state": "72.5"})
    assert resp2.status_code == 200
    resp3 = client.patch(f"/devices/{d2['id']}/state", json={"state": "hot"})
    assert resp3.status_code == 422

def test_log_limit():
    d = client.post("/devices", json={"name": "L1", "type": "light", "room": "A", "state": "off"}).json()
    d_id = d["id"]
    
    # Create 15 state changes
    for i in range(15):
        client.patch(f"/devices/{d_id}/state", json={"state": "on" if i%2==0 else "off"})
        
    logs = client.get(f"/devices/{d_id}/logs").json()
    assert len(logs) == 10

