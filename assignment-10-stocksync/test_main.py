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

def test_roles_and_filtering():
    client.post("/auth/register", json={"email": "admin@t.com", "password": "pass", "role": "admin"})
    client.post("/auth/register", json={"email": "mgr@t.com", "password": "pass", "role": "manager"})
    
    t_a = client.post("/auth/token", data={"username": "admin@t.com", "password": "pass"}).json()["access_token"]
    t_m = client.post("/auth/token", data={"username": "mgr@t.com", "password": "pass"}).json()["access_token"]
    
    h_a = {"Authorization": f"Bearer {t_a}"}
    h_m = {"Authorization": f"Bearer {t_m}"}
    
    # Validation test
    resp1 = client.post("/items", json={"name": "A", "unit_cost": 10, "selling_price": 5, "quantity": 10}, headers=h_a)
    assert resp1.status_code == 422
    
    resp2 = client.post("/items", json={"name": "A", "unit_cost": 5, "selling_price": 10, "quantity": 10}, headers=h_a)
    assert resp2.status_code == 201
    assert "unit_cost" in resp2.json() # admin gets unit_cost
    i_id = resp2.json()["id"]
    
    # Manager response filtering
    mgr_get = client.get(f"/items/{i_id}", headers=h_m)
    assert mgr_get.status_code == 200
    assert "unit_cost" not in mgr_get.json()
    
    # Valuation (admin only)
    val_mgr = client.get("/inventory/valuation", headers=h_m)
    assert val_mgr.status_code == 403
    
    val_admin = client.get("/inventory/valuation", headers=h_a)
    assert val_admin.status_code == 200
    assert val_admin.json()["total_inventory_value"] == 50.0

def test_stock_update_and_low_stock():
    client.post("/auth/register", json={"email": "admin@t.com", "password": "pass", "role": "admin"})
    t_a = client.post("/auth/token", data={"username": "admin@t.com", "password": "pass"}).json()["access_token"]
    h_a = {"Authorization": f"Bearer {t_a}"}
    
    r = client.post("/items", json={"name": "A", "unit_cost": 5, "selling_price": 10, "quantity": 10}, headers=h_a).json()
    i_id = r["id"]
    
    # Decrease stock
    upd1 = client.patch(f"/items/{i_id}/stock", json={"change": -5}, headers=h_a)
    assert upd1.status_code == 200
    assert upd1.json()["quantity"] == 5
    
    # Prevent negative
    upd2 = client.patch(f"/items/{i_id}/stock", json={"change": -10}, headers=h_a)
    assert upd2.status_code == 400
    
    # Low stock
    ls1 = client.get("/inventory/low-stock?threshold=10", headers=h_a)
    assert len(ls1.json()) == 1
    
    ls2 = client.get("/inventory/low-stock?threshold=5", headers=h_a)
    assert len(ls2.json()) == 0

