import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
import models

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

def test_register_user():
    response = client.post("/auth/register", json={"email": "test@test.com", "password": "password123", "role": "user"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@test.com"

def test_register_duplicate_email():
    client.post("/auth/register", json={"email": "test@test.com", "password": "password123"})
    response = client.post("/auth/register", json={"email": "test@test.com", "password": "password123"})
    assert response.status_code == 400

def test_login():
    client.post("/auth/register", json={"email": "test@test.com", "password": "password123"})
    response = client.post("/auth/token", data={"username": "test@test.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_admin_create_product():
    client.post("/auth/register", json={"email": "admin@test.com", "password": "password123", "role": "admin"})
    login_resp = client.post("/auth/token", data={"username": "admin@test.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    prod_data = {"name": "Laptop", "price": 999.99, "stock": 10, "category": "electronics"}
    response = client.post("/products", json=prod_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "Laptop"

def test_user_cannot_create_product():
    client.post("/auth/register", json={"email": "user@test.com", "password": "password123", "role": "user"})
    login_resp = client.post("/auth/token", data={"username": "user@test.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    prod_data = {"name": "Laptop", "price": 999.99, "stock": 10, "category": "electronics"}
    response = client.post("/products", json=prod_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_get_products_with_filters():
    client.post("/auth/register", json={"email": "admin@test.com", "password": "password123", "role": "admin"})
    login_resp = client.post("/auth/token", data={"username": "admin@test.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    client.post("/products", json={"name": "Laptop", "price": 1000, "stock": 5, "category": "electronics"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/products", json={"name": "Shirt", "price": 50, "stock": 20, "category": "fashion"}, headers={"Authorization": f"Bearer {token}"})
    
    resp1 = client.get("/products?category=electronics")
    assert len(resp1.json()) == 1
    assert resp1.json()[0]["name"] == "Laptop"
    
    resp2 = client.get("/products?min_price=100")
    assert len(resp2.json()) == 1
    assert resp2.json()[0]["name"] == "Laptop"

def test_update_product():
    client.post("/auth/register", json={"email": "admin@test.com", "password": "password123", "role": "admin"})
    login_resp = client.post("/auth/token", data={"username": "admin@test.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    prod_resp = client.post("/products", json={"name": "Laptop", "price": 1000, "stock": 5, "category": "electronics"}, headers={"Authorization": f"Bearer {token}"})
    prod_id = prod_resp.json()["id"]
    
    update_resp = client.put(f"/products/{prod_id}", json={"price": 900}, headers={"Authorization": f"Bearer {token}"})
    assert update_resp.status_code == 200
    assert update_resp.json()["price"] == 900.0

def test_invalid_product_validation():
    client.post("/auth/register", json={"email": "admin@test.com", "password": "password123", "role": "admin"})
    login_resp = client.post("/auth/token", data={"username": "admin@test.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    # Negative price
    response = client.post("/products", json={"name": "Laptop", "price": -10, "stock": 5, "category": "electronics"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422
    
    # Invalid category
    response2 = client.post("/products", json={"name": "Laptop", "price": 100, "stock": 5, "category": "invalid_cat"}, headers={"Authorization": f"Bearer {token}"})
    assert response2.status_code == 422

