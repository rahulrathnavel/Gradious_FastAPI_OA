# GatherUp — Event Management API

## Objective
Build an Async FastAPI-based Event Management API where users can create events, RSVP to events, view attendees, and cancel events.

## Features
- Asynchronous Database CRUD Operations
- Async SQLAlchemy engine
- Regex validation for email invites
- Future-date validation for event scheduling
- Event Capacity management (Blocking RSVPs when full)
- Prevention of duplicate RSVPs
- User-specific authorization for event cancellation
- Dynamic state updates (cancelled events cannot be RSVP'd to and are hidden from upcoming lists)

## Tech Stack
- FastAPI
- Async SQLAlchemy (`ext.asyncio`)
- `aiosqlite` (Async SQLite driver)
- `pytest` & `pytest-asyncio`

## Project Structure
```
assignment-05-gatherup/
├── database.py     # Async SQLite and Async SQLAlchemy session config
├── main.py         # FastAPI application and routing
├── models.py       # SQLAlchemy ORM models (Event, RSVP)
├── pytest.ini      # Pytest config for async mode
├── requirements.txt# Project dependencies
├── schemas.py      # Pydantic schemas for regex and date validation
└── test_main.py    # Pytest automated tests (async)
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
2. **Create Event**: Go to `POST /events`.
   - Set the custom header `x-user-id` to `1` (simulating user 1).
   - Send payload with a future date:
     ```json
     {
       "title": "Summer Party",
       "description": "Fun in the sun",
       "event_date": "2030-07-01T12:00:00Z",
       "max_attendees": 2
     }
     ```
   - Attempting to send a past date will yield a `422 Unprocessable Entity`.
3. **View Upcoming Events**: Go to `GET /events`. You will see your newly created event.
4. **RSVP**: Go to `POST /events/{id}/rsvp`.
   - Set `x-user-id` to `2`.
   - Provide an email: `{"email": "valid@email.com"}`. 
   - An invalid email will return `422`. 
   - Trying to RSVP again with user 2 will return `400 Duplicate RSVP`.
5. **Capacity Check**: RSVP with a third user (`x-user-id`: `3`). If capacity is reached, it will return `400 Event already full`.
6. **View Attendees**: Go to `GET /events/{id}/attendees` to list all RSVPs for the event.
7. **Cancel Event**: Go to `DELETE /events/{id}`. 
   - A user other than the creator (e.g., `x-user-id`: `2`) will get a `403 Forbidden`.
   - The creator (`x-user-id`: `1`) will successfully cancel it. The event will no longer appear in `GET /events`.

## Automated Testing
Run tests using:
```bash
python -m pytest
```

## Requirement Compliance
- **Async DB CRUD / Async SQLAlchemy**: PASS
- **Regex Email Validation**: PASS
- **Date Validation (Future date)**: PASS
- **Capacity Management**: PASS
- **User-Specific Auth (Cancellation)**: PASS

## Submission
Ready to be packaged as `StudentName_GatherUp.zip`.

