# EduStream — Course Learning Platform API

## Objective
Build a FastAPI-based E-Learning Platform API that manages users, courses, modules, and enrollments using Class-Based Dependencies for robust Access Control.

## Features
- JWT Authentication & RBAC (`teacher` vs `student`)
- Class-Based Dependencies (`RoleChecker`, `EnrollmentChecker`)
- Nested Data Storage (Creating a course along with its modules in one payload)
- Validation (`price >= 0`, minimum title lengths)
- Query Parameter Filtering (Filter courses by `instructor_name`)
- Access Control:
  - Teachers can create and update courses.
  - Students can enroll in courses.
  - Only enrolled students can access course module content.

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- bcrypt
- pytest

## Project Structure
```
assignment-06-edustream/
├── auth.py         # JWT logic and Class-Based Dependencies (RoleChecker)
├── database.py     # SQLite and SQLAlchemy session configuration
├── main.py         # FastAPI application and routing
├── models.py       # SQLAlchemy ORM models (User, Course, Module, Enrollment)
├── requirements.txt# Project dependencies
├── schemas.py      # Pydantic schemas (Nested ModuleCreate inside CourseCreate)
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
2. **Register a Teacher**: `POST /auth/register`
   - `email`: `teacher@test.com`, `password`: `pass`, `role`: `teacher`
3. **Register a Student**: `POST /auth/register`
   - `email`: `student@test.com`, `password`: `pass`, `role`: `student`
4. **Login as Teacher**: `POST /auth/token` -> Authorize in Swagger.
5. **Create Course (Teacher Only)**: `POST /courses`
   ```json
   {
     "title": "FastAPI Masterclass",
     "description": "Learn it all",
     "price": 49.99,
     "modules": [
       {"title": "Intro", "content": "Welcome", "order_index": 1}
     ]
   }
   ```
6. **Login as Student**: `POST /auth/token` (using student credentials) -> Authorize.
7. **Enroll in Course**: `POST /courses/{id}/enroll`. (Using the ID from step 5).
8. **View Course Content**: `GET /courses/{id}/content`. Because you are enrolled, you will see the full modules array.
9. **Filter Courses**: `GET /courses?instructor_name=teacher`.

## Automated Testing
Run tests using:
```bash
python -m pytest
```

## Requirement Compliance
- **Class-Based Dependencies (RBAC)**: PASS
- **Nested Data (Courses -> Modules)**: PASS
- **Enrolled Student Validation**: PASS
- **Validation Rules (Price >= 0)**: PASS
- **Filtering by Instructor Name**: PASS

## Submission
Ready to be packaged as `StudentName_EduStream.zip`.

