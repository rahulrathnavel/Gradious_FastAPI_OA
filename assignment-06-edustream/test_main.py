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

def test_roles_and_auth():
    client.post("/auth/register", json={"email": "teacher@t.com", "password": "pass", "role": "teacher"})
    client.post("/auth/register", json={"email": "student@t.com", "password": "pass", "role": "student"})
    
    t_token = client.post("/auth/token", data={"username": "teacher@t.com", "password": "pass"}).json()["access_token"]
    s_token = client.post("/auth/token", data={"username": "student@t.com", "password": "pass"}).json()["access_token"]
    
    course_data = {
        "title": "Python 101",
        "description": "Learn Python",
        "price": 99.99,
        "modules": [
            {"title": "Intro", "content": "Hello World", "order_index": 1}
        ]
    }
    
    # Student cannot create
    resp_s = client.post("/courses", json=course_data, headers={"Authorization": f"Bearer {s_token}"})
    assert resp_s.status_code == 403
    
    # Teacher can create
    resp_t = client.post("/courses", json=course_data, headers={"Authorization": f"Bearer {t_token}"})
    assert resp_t.status_code == 201
    course_id = resp_t.json()["id"]
    
    # Teacher cannot enroll
    resp_e_t = client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {t_token}"})
    assert resp_e_t.status_code == 403
    
    # Student can enroll
    resp_e_s = client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {s_token}"})
    assert resp_e_s.status_code == 201
    
    # Student cannot duplicate enroll
    resp_e_s2 = client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {s_token}"})
    assert resp_e_s2.status_code == 400

def test_course_content_access():
    client.post("/auth/register", json={"email": "t@t.com", "password": "pass", "role": "teacher"})
    client.post("/auth/register", json={"email": "s1@t.com", "password": "pass", "role": "student"})
    client.post("/auth/register", json={"email": "s2@t.com", "password": "pass", "role": "student"})
    
    t_token = client.post("/auth/token", data={"username": "t@t.com", "password": "pass"}).json()["access_token"]
    s1_token = client.post("/auth/token", data={"username": "s1@t.com", "password": "pass"}).json()["access_token"]
    s2_token = client.post("/auth/token", data={"username": "s2@t.com", "password": "pass"}).json()["access_token"]
    
    course_resp = client.post("/courses", json={"title": "Go", "price": 0, "modules": [{"title": "1", "content": "1", "order_index": 1}]}, headers={"Authorization": f"Bearer {t_token}"})
    course_id = course_resp.json()["id"]
    
    client.post(f"/courses/{course_id}/enroll", headers={"Authorization": f"Bearer {s1_token}"})
    
    # s1 can access
    content1 = client.get(f"/courses/{course_id}/content", headers={"Authorization": f"Bearer {s1_token}"})
    assert content1.status_code == 200
    assert len(content1.json()["modules"]) == 1
    
    # s2 cannot access
    content2 = client.get(f"/courses/{course_id}/content", headers={"Authorization": f"Bearer {s2_token}"})
    assert content2.status_code == 403

def test_get_courses_and_update():
    client.post("/auth/register", json={"email": "t@t.com", "password": "pass", "role": "teacher"})
    t_token = client.post("/auth/token", data={"username": "t@t.com", "password": "pass"}).json()["access_token"]
    
    c_resp = client.post("/courses", json={"title": "Rust", "price": 50}, headers={"Authorization": f"Bearer {t_token}"})
    course_id = c_resp.json()["id"]
    
    list_resp = client.get("/courses?instructor_name=t@t.com")
    assert len(list_resp.json()) == 1
    
    # update course
    up_resp = client.patch(f"/courses/{course_id}", json={"price": 25}, headers={"Authorization": f"Bearer {t_token}"})
    assert up_resp.status_code == 200
    assert up_resp.json()["price"] == 25.0

