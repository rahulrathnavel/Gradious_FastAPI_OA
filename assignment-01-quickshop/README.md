# QuickShop — E-Commerce Catalog API

## Objective
Build a FastAPI-based E-Commerce Catalog API where users can browse products and admins can manage products and stock.

## Features
- JWT Authentication (`OAuth2PasswordBearer`)
- Role-Based Access Control (Admin/User)
- Pydantic Validation & Enums
- Route Grouping (`APIRouter`)
- SQLite database with SQLAlchemy ORM

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- bcrypt
- pytest

## Project Structure
```
assignment-01-quickshop/
├── auth.py         # Authentication logic (JWT, password hashing)
├── database.py     # SQLite and SQLAlchemy session configuration
├── main.py         # FastAPI application and routing
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
2. **Register an Admin**: Go to `POST /auth/register`. Send:
   ```json
   {
     "email": "admin@test.com",
     "password": "password123",
     "role": "admin"
   }
   ```
3. **Login**: Go to `POST /auth/token`. Send `username=admin@test.com` and `password=password123`.
4. **Authorize**: Copy the returned `access_token` and click the "Authorize" button at the top of Swagger. Enter the token.
5. **Create Product (Admin Only)**: Go to `POST /products`. Send:
   ```json
   {
     "name": "Laptop",
     "description": "High-end laptop",
     "price": 1200.0,
     "stock": 10,
     "category": "electronics"
   }
   ```
6. **Browse Products**: Go to `GET /products`. Test the optional filters (`min_price`, `max_price`, `category`).
7. **Test User Role**: Register a regular user (`role: user`), authenticate, and try to call `POST /products`. It will return a 403 Forbidden error.

## Automated Testing
Run tests using:
```bash
python -m pytest
```

## Requirement Compliance
- **FastAPI/SQLAlchemy/SQLite**: PASS
- **JWT Auth / bcrypt**: PASS
- **Role-Based Access Control**: PASS
- **Pydantic Schemas / Enums**: PASS
- **Endpoints (/auth/register, /auth/token, /products)**: PASS

## Submission
Ready to be packaged as `StudentName_QuickShop.zip`.

