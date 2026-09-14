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

def test_signup_and_login():
    resp = client.post("/users/signup", json={"email": "u1@t.com", "password": "pass", "fitness_level": "beginner"})
    assert resp.status_code == 201
    
    # invalid enum
    resp2 = client.post("/users/signup", json={"email": "u2@t.com", "password": "pass", "fitness_level": "pro"})
    assert resp2.status_code == 422
    
    login_resp = client.post("/users/login", data={"username": "u1@t.com", "password": "pass"})
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

def test_create_workout():
    client.post("/users/signup", json={"email": "u1@t.com", "password": "pass", "fitness_level": "beginner"})
    token = client.post("/users/login", data={"username": "u1@t.com", "password": "pass"}).json()["access_token"]
    
    resp = client.post("/workouts", json={"type": "cardio", "duration": 30, "calories_burned": 200}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["type"] == "cardio"

    # invalid duration
    resp2 = client.post("/workouts", json={"type": "cardio", "duration": 0, "calories_burned": 200}, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 422

    # invalid type
    resp3 = client.post("/workouts", json={"type": "running", "duration": 30, "calories_burned": 200}, headers={"Authorization": f"Bearer {token}"})
    assert resp3.status_code == 422

def test_get_workouts_pagination():
    client.post("/users/signup", json={"email": "u1@t.com", "password": "pass", "fitness_level": "beginner"})
    token = client.post("/users/login", data={"username": "u1@t.com", "password": "pass"}).json()["access_token"]
    
    for _ in range(15):
        client.post("/workouts", json={"type": "yoga", "duration": 60, "calories_burned": 100}, headers={"Authorization": f"Bearer {token}"})
        
    resp1 = client.get("/workouts", headers={"Authorization": f"Bearer {token}"})
    assert len(resp1.json()) == 10 # default limit
    
    resp2 = client.get("/workouts?limit=5&offset=10", headers={"Authorization": f"Bearer {token}"})
    assert len(resp2.json()) == 5

def test_stats_and_isolation():
    client.post("/users/signup", json={"email": "u1@t.com", "password": "pass", "fitness_level": "beginner"})
    token1 = client.post("/users/login", data={"username": "u1@t.com", "password": "pass"}).json()["access_token"]
    
    client.post("/users/signup", json={"email": "u2@t.com", "password": "pass", "fitness_level": "advanced"})
    token2 = client.post("/users/login", data={"username": "u2@t.com", "password": "pass"}).json()["access_token"]
    
    client.post("/workouts", json={"type": "cardio", "duration": 30, "calories_burned": 200}, headers={"Authorization": f"Bearer {token1}"})
    
    client.post("/workouts", json={"type": "hiit", "duration": 20, "calories_burned": 300}, headers={"Authorization": f"Bearer {token2}"})
    
    # stats check
    stats1 = client.get("/workouts/stats", headers={"Authorization": f"Bearer {token1}"})
    assert stats1.json()["total_calories_burned"] == 200.0
    
    # isolation check
    w1 = client.get("/workouts", headers={"Authorization": f"Bearer {token1}"}).json()
    assert len(w1) == 1
    
    # delete check cross user
    w1_id = w1[0]["id"]
    del_resp = client.delete(f"/workouts/{w1_id}", headers={"Authorization": f"Bearer {token2}"})
    assert del_resp.status_code == 403
    
    # delete check own
    del_resp2 = client.delete(f"/workouts/{w1_id}", headers={"Authorization": f"Bearer {token1}"})
    assert del_resp2.status_code == 204

def test_invalid_token():
    resp = client.get("/workouts", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401

