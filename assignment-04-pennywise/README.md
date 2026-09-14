# PennyWise — Personal Finance Tracker API

## Objective
Build a FastAPI-based Personal Finance Tracker API where users can record income and expenses, view summaries, filter transactions, update entries, and perform soft deletes.

## Features
- Global Exception Handlers (`TransactionNotFoundError`, `InsufficientBalanceError`, etc.)
- OAuth2 Scopes (`read_transactions`, `write_transactions`)
- Strict Mode logic to prevent expenses greater than current balance
- Default factories for timestamps (`created_at`)
- User-specific transaction access
- Query parameter filtering by month and year
- Soft Delete functionality (`is_active = false`)
- 24-hour update restriction on transactions

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- bcrypt
- pytest

## Project Structure
```
assignment-04-pennywise/
├── auth.py         # OAuth2 scopes and JWT logic
├── database.py     # SQLite and SQLAlchemy session configuration
├── exceptions.py   # Global exception handlers
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
2. **Register**: Go to `POST /auth/register`. Send:
   ```json
   {
     "email": "user@test.com",
     "password": "password123",
     "strict_mode": true,
     "scope": "read_transactions write_transactions"
   }
   ```
3. **Login**: Go to `POST /auth/token`. Send `username=user@test.com`, `password=password123`, and enter `read_transactions write_transactions` in the Scope field (space separated).
4. **Authorize**: Copy the returned token, click the "Authorize" button, and paste it.
5. **Test Strict Mode**: Try to create an expense (`POST /transactions`) of `amount: 100` before adding any income. You will get a `400 Insufficient balance` error.
6. **Add Income**: Create an income transaction of `amount: 500`. Now you can add expenses up to 500.
7. **View Summary**: Go to `GET /transactions/summary` to view your total income, expense, and balance.
8. **Filter Transactions**: Go to `GET /transactions` and test the `month` and `year` query parameters.
9. **Soft Delete**: Go to `DELETE /transactions/{id}`. This marks it as inactive. Verify it no longer appears in the list or summary.

## Automated Testing
Run tests using:
```bash
python -m pytest
```

## Requirement Compliance
- **Global Exception Handlers**: PASS
- **OAuth2 Scopes**: PASS
- **Default Timestamp Factories**: PASS
- **Soft Delete / Strict Mode**: PASS
- **24-hour Update Restriction**: PASS

## Submission
Ready to be packaged as `StudentName_PennyWise.zip`.

