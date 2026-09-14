import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
import models
from datetime import datetime, timedelta

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

def test_auth_and_scopes():
    client.post("/auth/register", json={"email": "s@t.com", "password": "pass", "scope": "read_transactions"})
    token = client.post("/auth/token", data={"username": "s@t.com", "password": "pass", "scope": "read_transactions write_transactions"}).json()["access_token"]
    
    # Write should fail due to missing scope (user only has read)
    resp = client.post("/transactions", json={"amount": 100, "category": "Salary", "type": "income"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

def test_transaction_crud_and_strict_mode():
    client.post("/auth/register", json={"email": "u@t.com", "password": "pass", "strict_mode": True, "scope": "read_transactions write_transactions"})
    token = client.post("/auth/token", data={"username": "u@t.com", "password": "pass"}).json()["access_token"]
    
    # 1. Strict mode prevents expense > balance
    resp_exp = client.post("/transactions", json={"amount": 100, "category": "Food", "type": "expense"}, headers={"Authorization": f"Bearer {token}"})
    assert resp_exp.status_code == 400
    assert resp_exp.json()["detail"] == "Insufficient balance"
    
    # 2. Add income
    client.post("/transactions", json={"amount": 500, "category": "Salary", "type": "income"}, headers={"Authorization": f"Bearer {token}"})
    
    # 3. Add expense now succeeds
    resp_exp2 = client.post("/transactions", json={"amount": 100, "category": "Food", "type": "expense"}, headers={"Authorization": f"Bearer {token}"})
    assert resp_exp2.status_code == 201
    
    # 4. Summary
    summary = client.get("/transactions/summary", headers={"Authorization": f"Bearer {token}"})
    assert summary.json()["current_balance"] == 400
    
    # 5. Soft delete expense
    t_id = resp_exp2.json()["id"]
    client.delete(f"/transactions/{t_id}", headers={"Authorization": f"Bearer {token}"})
    
    # 6. Check summary again (expense removed)
    summary2 = client.get("/transactions/summary", headers={"Authorization": f"Bearer {token}"})
    assert summary2.json()["current_balance"] == 500
    
    # 7. Soft deleted item doesn't appear in list
    t_list = client.get("/transactions", headers={"Authorization": f"Bearer {token}"})
    assert len(t_list.json()) == 1

def test_update_24h_restriction():
    client.post("/auth/register", json={"email": "u2@t.com", "password": "pass", "strict_mode": False, "scope": "read_transactions write_transactions"})
    token = client.post("/auth/token", data={"username": "u2@t.com", "password": "pass"}).json()["access_token"]
    
    # Manually insert old transaction
    db = TestingSessionLocal()
    user = db.query(models.User).filter(models.User.email == "u2@t.com").first()
    old_t = models.Transaction(user_id=user.id, amount=10, category="old", type="expense", created_at=datetime.utcnow() - timedelta(days=2))
    db.add(old_t)
    db.commit()
    t_id = old_t.id
    db.close()
    
    resp = client.put(f"/transactions/{t_id}", json={"amount": 20}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert "24 hours" in resp.json()["detail"]

