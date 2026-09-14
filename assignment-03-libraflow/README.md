# LibraFlow — Digital Library System API

## Objective
Build a FastAPI-based Digital Library System to manage books, authors, and book availability.

## Features
- Nested Pydantic Models (`Author` inside `Book`)
- Custom Middleware (Logs request processing time in milliseconds)
- Role-Based Access Control (Only `staff` users can add books via custom header)
- Query Parameter Search (`title` and `author`)
- ISBN String Validation (10 to 13 characters)
- Partial Updates using `PATCH` for borrowing books
- Error Handling for missing/duplicate data

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- pytest

## Project Structure
```
assignment-03-libraflow/
├── database.py     # SQLite and SQLAlchemy session configuration
├── main.py         # FastAPI application and routing
├── middleware.py   # Custom timing middleware
├── models.py       # SQLAlchemy ORM models
├── requirements.txt# Project dependencies
├── schemas.py      # Pydantic schemas for request/response validation
└── test_main.py    # Pytest automated tests
```

## Setup & Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Swagger Testing Guide
1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
2. **Add a Book (Staff Only)**: Go to `POST /books`. 
   - Click "Try it out".
   - In the parameters, provide the custom header `x-role`: `staff`.
   - Send:
     ```json
     {
       "isbn": "1234567890123",
       "title": "FastAPI Essentials",
       "author": {
         "name": "John Smith",
         "biography": "Technical author",
         "birth_year": 1980
       },
       "published_year": 2026,
       "is_available": true
     }
     ```
3. **Browse Books**: Go to `GET /books`. Test the optional query filters (`title`, `author`).
4. **Borrow a Book**: Go to `PATCH /books/{isbn}/borrow`. Use the ISBN you created. It will mark the book as `is_available: false`. If you try again, it will return `400 Book already borrowed`.
5. **Author Book Count**: Go to `GET /authors` to see the total number of books written by each author.

## Automated Testing
Run tests using:
```bash
python -m pytest
```

## Requirement Compliance
- **Nested Pydantic Models**: PASS
- **Custom Middleware**: PASS
- **Role-Based Access (Staff only)**: PASS
- **Query Parameter Search**: PASS
- **Partial Updates (PATCH)**: PASS
- **ISBN Validation**: PASS

## Submission
Ready to be packaged as `StudentName_LibraFlow.zip`.

