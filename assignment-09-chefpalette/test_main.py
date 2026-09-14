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

def test_recipe_crud_and_filters():
    # Register & Login
    client.post("/auth/register", json={"email": "chef@t.com", "password": "pass"})
    token = client.post("/auth/token", data={"username": "chef@t.com", "password": "pass"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Recipe
    r1 = client.post("/recipes", json={
        "title": "Pasta",
        "ingredients": ["pasta", "tomato sauce", "cheese"],
        "instructions": "Boil pasta",
        "prep_time": 20
    }, headers=headers).json()
    assert r1["title"] == "Pasta"
    assert "tomato sauce" in r1["ingredients"]
    
    r2 = client.post("/recipes", json={
        "title": "Salad",
        "ingredients": ["lettuce", "tomato"],
        "instructions": "Mix",
        "prep_time": 10
    }, headers=headers).json()
    
    # Validation: empty ingredients
    r3 = client.post("/recipes", json={
        "title": "Empty",
        "ingredients": [],
        "instructions": "Mix",
        "prep_time": 10
    }, headers=headers)
    assert r3.status_code == 422
    
    # Filter by ingredient partial match
    search1 = client.get("/recipes?ingredient=tom")
    assert len(search1.json()) == 2
    
    search2 = client.get("/recipes?ingredient=sauce")
    assert len(search2.json()) == 1
    
    # Filter by prep_time
    search3 = client.get("/recipes?max_prep_time=15")
    assert len(search3.json()) == 1
    assert search3.json()[0]["title"] == "Salad"
    
    # Update recipe
    r_id = r1["id"]
    u_resp = client.put(f"/recipes/{r_id}", json={
        "ingredients": ["pasta", "pesto"]
    }, headers=headers)
    assert u_resp.status_code == 200
    assert "pesto" in u_resp.json()["ingredients"]

def test_likes_and_trending():
    # Users
    client.post("/auth/register", json={"email": "u1@t.com", "password": "pass"})
    client.post("/auth/register", json={"email": "u2@t.com", "password": "pass"})
    t1 = client.post("/auth/token", data={"username": "u1@t.com", "password": "pass"}).json()["access_token"]
    t2 = client.post("/auth/token", data={"username": "u2@t.com", "password": "pass"}).json()["access_token"]
    
    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}
    
    # Recipes
    r1 = client.post("/recipes", json={"title": "R1", "ingredients": ["i1"], "instructions": "ins", "prep_time": 10}, headers=h1).json()
    r2 = client.post("/recipes", json={"title": "R2", "ingredients": ["i2"], "instructions": "ins", "prep_time": 10}, headers=h1).json()
    
    # Likes
    client.post(f"/recipes/{r1['id']}/like", headers=h1)
    client.post(f"/recipes/{r1['id']}/like", headers=h2) # R1 has 2 likes
    client.post(f"/recipes/{r2['id']}/like", headers=h1) # R2 has 1 like
    
    # Duplicate like
    dup = client.post(f"/recipes/{r1['id']}/like", headers=h1)
    assert dup.status_code == 400
    
    # Trending
    trend = client.get("/recipes/trending").json()
    assert len(trend) == 2
    assert trend[0]["id"] == r1["id"]
    assert trend[0]["like_count"] == 2
    assert trend[1]["id"] == r2["id"]
    assert trend[1]["like_count"] == 1

