#  FastAPI Online Assessment Solutions

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-black?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

##  Overview
This repository contains 10 fully implemented, production-ready backend API assignments built with FastAPI. These projects were developed strictly according to specific assessment requirements, demonstrating core backend engineering concepts, API design, validation, authentication, and database management.

##  Tech Stack
* **Framework:** FastAPI (Python 3.11+)
* **Database:** SQLite
* **ORM:** SQLAlchemy (Sync & Async) / Alembic for Migrations
* **Validation:** Pydantic V2
* **Authentication:** OAuth2 (JWT Bearer / Form), bcrypt, passlib
* **Testing:** Pytest, HTTPX

##  Projects Included
1. **QuickShop:** E-Commerce Catalog API (RBAC, JWT, CRUD)
2. **PulseFit:** Fitness Tracker (User Isolation, Pagination)
3. **LibraFlow:** Digital Library System (Custom Middleware, Nested Schemas)
4. **PennyWise:** Personal Finance Tracker (OAuth2 Scopes, Soft Delete)
5. **GatherUp:** Event Management API (Async CRUD, Capacity Limits)
6. **EduStream:** Course Learning Platform (Class-based Dependencies)
7. **SyncTask:** Kanban Task Board (1-to-N relationships, Cascade Deletion)
8. **Domos:** Smart Home IoT Manager (Custom Headers, Log Limits)
9. **ChefPalette:** Recipe Sharing API (Partial Matching, Aggregation)
10. **StockSync:** Warehouse Inventory (Alembic Migrations, OAuth2 Forms)

##  General Setup Instructions
Each project is completely isolated and runs independently. To run any of the assignments locally:

**1. Navigate to the project folder:**
\\ash
cd assignment-01-quickshop
\
**2. Create and activate a virtual environment (Optional but recommended):**
\\ash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
\
**3. Install dependencies:**
\\ash
pip install -r requirements.txt
\
**4. Run the application:**
\\ash
python -m uvicorn main:app --reload
\*(Note: For Assignment 10, run \python -m alembic upgrade head\ before starting the server).*

**5. Access Swagger Documentation:**
Open your browser and navigate to: http://127.0.0.1:8000/docs
