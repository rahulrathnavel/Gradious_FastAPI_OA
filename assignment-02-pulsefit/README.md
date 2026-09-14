# PulseFit — Fitness & Workout Tracker API

## Objective
Build a FastAPI-based Fitness & Workout Tracker API where users can log workouts, track their fitness activity, and view only their own workout data.

## Features
- JWT Authentication
- Dependency Injection (`get_current_user`, `calculate_workout_stats`)
- Enum validation (Workout types, Fitness levels)
- Datetime handling with UTC
- Pagination for listing workouts
- Data isolation (Users can only view and delete their own workouts)
- Statistics calculation

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- bcrypt
- pytest

## Project Structure
```
assignment-02-pulsefit/
├── auth.py         # Authentication logic (JWT, password hashing, dependencies)
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
2. **Signup**: Go to `POST /users/signup`. Send:
   ```json
   {
     "email": "user@test.com",
     "password": "password123",
     "fitness_level": "beginner"
   }
   ```
3. **Login**: Go to `POST /users/login`. Send `username=user@test.com` and `password=password123`.
4. **Authorize**: Copy the returned `access_token` and click "Authorize" at the top of Swagger. Enter the token.
5. **Log Workout**: Go to `POST /workouts`. Send:
   ```json
   {
     "type": "cardio",
     "duration": 30,
     "calories_burned": 250
   }
   ```
6. **View Workouts**: Go to `GET /workouts`. It automatically uses the `limit=10` and `offset=0` defaults.
7. **View Stats**: Go to `GET /workouts/stats` to see the total calories burned (calculated using dependency injection).
8. **Delete Workout**: Go to `DELETE /workouts/{id}` using the ID returned in step 5.

## Automated Testing
Run tests using:
```bash
python -m pytest
```

## Requirement Compliance
- **JWT Auth / get_current_user**: PASS
- **Dependency Injection (Stats)**: PASS
- **Enums & Pydantic Validation**: PASS
- **Pagination (limit/offset)**: PASS
- **Data Access Isolation**: PASS

## Submission
Ready to be packaged as `StudentName_PulseFit.zip`.

