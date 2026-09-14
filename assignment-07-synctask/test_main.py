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

def test_create_project_and_tasks():
    # Create project
    proj_resp = client.post("/projects", json={"name": "Project 1", "description": "Desc"})
    assert proj_resp.status_code == 201
    proj_id = proj_resp.json()["id"]

    # Create task
    task_resp = client.post(f"/projects/{proj_id}/tasks", json={
        "title": "Task 1",
        "description": "Task desc",
        "priority": 3
    })
    assert task_resp.status_code == 201
    assert task_resp.json()["title"] == "Task 1"
    assert task_resp.json()["status"] == "todo"
    
    # Invalid priority
    task_resp2 = client.post(f"/projects/{proj_id}/tasks", json={
        "title": "Task 2",
        "priority": 6
    })
    assert task_resp2.status_code == 422
    
    # Invalid title length
    task_resp3 = client.post(f"/projects/{proj_id}/tasks", json={
        "title": "Ta",
        "priority": 3
    })
    assert task_resp3.status_code == 422

def test_get_project_tasks_grouped():
    proj_resp = client.post("/projects", json={"name": "Project 1"})
    proj_id = proj_resp.json()["id"]
    
    t1 = client.post(f"/projects/{proj_id}/tasks", json={"title": "Task 1", "priority": 1})
    t2 = client.post(f"/projects/{proj_id}/tasks", json={"title": "Task 2", "priority": 2, "status": "doing"})
    
    resp = client.get(f"/projects/{proj_id}/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["todo"]) == 1
    assert len(data["doing"]) == 1
    assert len(data["done"]) == 0
    
    assert data["todo"][0]["title"] == "Task 1"

def test_task_status_updates():
    proj_resp = client.post("/projects", json={"name": "Project 1"})
    proj_id = proj_resp.json()["id"]
    
    t1 = client.post(f"/projects/{proj_id}/tasks", json={"title": "Task 1", "priority": 1}).json()
    t_id = t1["id"]
    
    # todo -> doing
    u1 = client.patch(f"/tasks/{t_id}", json={"status": "doing"})
    assert u1.status_code == 200
    
    # doing -> done
    u2 = client.patch(f"/tasks/{t_id}", json={"status": "done"})
    assert u2.status_code == 200
    
    # done -> todo (invalid)
    u3 = client.patch(f"/tasks/{t_id}", json={"status": "todo"})
    assert u3.status_code == 400

def test_cascade_delete():
    proj_resp = client.post("/projects", json={"name": "Project 1"})
    proj_id = proj_resp.json()["id"]
    
    client.post(f"/projects/{proj_id}/tasks", json={"title": "Task 1", "priority": 1})
    
    # Delete project
    del_resp = client.delete(f"/projects/{proj_id}")
    assert del_resp.status_code == 204
    
    # Try fetching tasks
    get_resp = client.get(f"/projects/{proj_id}/tasks")
    assert get_resp.status_code == 404

