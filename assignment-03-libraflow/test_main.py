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

def test_staff_create_book():
    book_data = {
        "isbn": "1234567890123",
        "title": "FastAPI Essentials",
        "author": {
            "name": "John Smith",
            "biography": "Technical author",
            "birth_year": 1980
        },
        "published_year": 2026,
        "is_available": True
    }
    resp = client.post("/books", json=book_data, headers={"X-Role": "staff"})
    assert resp.status_code == 201
    assert resp.json()["isbn"] == "1234567890123"
    assert resp.json()["author"]["name"] == "John Smith"

def test_non_staff_cannot_create_book():
    book_data = {
        "isbn": "1234567890123",
        "title": "FastAPI",
        "author": {"name": "Jane"},
        "published_year": 2026
    }
    resp = client.post("/books", json=book_data, headers={"X-Role": "user"})
    assert resp.status_code == 403

def test_isbn_validation():
    # length too short
    book_data = {
        "isbn": "123",
        "title": "FastAPI",
        "author": {"name": "Jane"},
        "published_year": 2026
    }
    resp = client.post("/books", json=book_data, headers={"X-Role": "staff"})
    assert resp.status_code == 422

def test_borrow_book():
    book_data = {
        "isbn": "1111111111111",
        "title": "Book 1",
        "author": {"name": "Author 1"},
        "published_year": 2020,
        "is_available": True
    }
    client.post("/books", json=book_data, headers={"X-Role": "staff"})
    
    borrow_resp = client.patch("/books/1111111111111/borrow")
    assert borrow_resp.status_code == 200
    assert borrow_resp.json()["is_available"] == False
    
    # Already borrowed
    borrow_resp2 = client.patch("/books/1111111111111/borrow")
    assert borrow_resp2.status_code == 400
    
    # 404
    borrow_resp3 = client.patch("/books/9999999999999/borrow")
    assert borrow_resp3.status_code == 404

def test_book_search():
    client.post("/books", json={"isbn": "1111111111", "title": "Python 101", "author": {"name": "Guido"}, "published_year": 1991}, headers={"X-Role": "staff"})
    client.post("/books", json={"isbn": "2222222222", "title": "FastAPI 101", "author": {"name": "Seb"}, "published_year": 2020}, headers={"X-Role": "staff"})
    
    resp = client.get("/books?title=Python")
    assert len(resp.json()) == 1
    assert resp.json()[0]["isbn"] == "1111111111"

def test_get_authors_count():
    client.post("/books", json={"isbn": "1111111111", "title": "A1 B1", "author": {"name": "A1"}, "published_year": 1991}, headers={"X-Role": "staff"})
    client.post("/books", json={"isbn": "2222222222", "title": "A1 B2", "author": {"name": "A1"}, "published_year": 1992}, headers={"X-Role": "staff"})
    client.post("/books", json={"isbn": "3333333333", "title": "A2 B1", "author": {"name": "A2"}, "published_year": 1993}, headers={"X-Role": "staff"})
    
    resp = client.get("/authors")
    assert resp.status_code == 200
    counts = {x["name"]: x["book_count"] for x in resp.json()}
    assert counts["A1"] == 2
    assert counts["A2"] == 1

