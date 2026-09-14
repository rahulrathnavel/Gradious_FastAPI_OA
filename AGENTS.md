# AGENTS.md - Persistent Engineering & Compliance Contract

## 1. Mission
Produce independent, clean, simple, professional, production-quality FastAPI codebases that satisfy the exact assignment requirements and are directly suitable for submission. The primary interactive API interface is FastAPI Swagger at `/docs`, along with automated tests. No frontend code is allowed.

## 2. Source-of-Truth Rules
The assignment PDFs are the PRIMARY AND AUTHORITATIVE SOURCE OF TRUTH. Do not rely on memory, do not invent requirements, and do not silently alter required behavior. When a PDF explicitly requires a FastAPI mechanism, that actual mechanism must be implemented exactly.

## 3. All Assignment Names
- Assignment 1: QuickShop — E-Commerce Catalog API
- Assignment 2: PulseFit — Fitness & Workout Tracker
- Assignment 3: LibraFlow — Digital Library System
- Assignment 4: PennyWise — Personal Finance Tracker
- Assignment 5: GatherUp — Event Management API
- Assignment 6: EduStream — Course Learning Platform
- Assignment 7: SyncTask — Kanban Task Board
- Assignment 8: Domos — Smart Home IoT Manager
- Assignment 9: ChefPalette — Recipe Sharing API
- Assignment 10: StockSync — Warehouse Inventory

## 4. Workspace Structure
Each assignment is an independent project. Do not tightly couple assignments. Do not create a giant shared framework.
```
/
├── AGENTS.md
├── assignment-01-quickshop/
├── assignment-02-pulsefit/
├── assignment-03-libraflow/
├── assignment-04-pennywise/
├── assignment-05-gatherup/
├── assignment-06-edustream/
├── assignment-07-synctask/
├── assignment-08-domos/
├── assignment-09-chefpalette/
└── assignment-10-stocksync/
```
Each project contains its own `requirements.txt`, `README.md`, source code, tests, and (where applicable) local Alembic migrations.

## 5. Assignment-Specific Mandatory Requirements
- **Ass 1**: FastAPI, SQLAlchemy, password hashing, JWT Auth (OAuth2PasswordBearer), RBAC, Pydantic/Enum validation, APIRouter grouping.
- **Ass 2**: JWT Auth, Depends(get_current_user), dependency injection, Enums, datetime.utcnow(), pagination, user-specific data access, API stats dependency.
- **Ass 3**: Nested Pydantic schemas, custom middleware (execution time), RBAC, query search, PATCH, ISBN string validation.
- **Ass 4**: Global exception handlers, OAuth2 scopes, default timestamp factories, user-specific access, filtering, soft delete, strict mode.
- **Ass 5**: Async database CRUD, regex email validation, date validation, capacity management, user-specific authorization.
- **Ass 6**: RBAC, class-based dependencies, nested schemas, path parameters, enrollment validation.
- **Ass 7**: Pydantic Field validation, SQLAlchemy relationships (1-to-N), Enum, cascade delete, task status management/grouping.
- **Ass 8**: Custom response headers, middleware logging, Enum, device state management (latest 10 logs), query filtering.
- **Ass 9**: List-based Pydantic schemas, dependency injection for DB, complex query filters, partial matching, like aggregation.
- **Ass 10**: OAuth2PasswordRequestForm, RBAC, response model filtering, stock management, query filtering, Alembic migrations.

## 6. Confirmed Decisions from Clarification
- **Python Version**: Python 3.11 for all projects (use modern readable syntax).
- **Alembic Scope**: Initialize Alembic locally *inside* the `assignment-10-stocksync` project.
- **Async Database Library**: Async SQLAlchemy for Assignment 5.

## 7. Database Decisions
- **Engine**: SQLite will be used for all assignments (unless a specific external database is strictly mandated by a PDF).
- **Driver**: standard `sqlite3` for synchronous assignments, and `aiosqlite` for asynchronous assignments.
- **Constraints**: Use database constraints (Primary Keys, Foreign Keys, UNIQUE, CASCADE) to enforce critical business rules.

## 8. Authentication Decisions
- Real authentication only. Never fake authentication or hardcode tokens/passwords.
- Use secure password hashing (bcrypt/passlib). Never store plain-text passwords.
- Implement exactly what is requested (JWT, OAuth2PasswordBearer, OAuth2PasswordRequestForm).

## 9. Engineering Standards
- Simple, explicit, production-quality code.
- Prioritize correctness, clarity, maintainability, testability, security, and exact PDF compliance over complexity, abstraction, or fancy patterns.
- Follow the exact API contract: preserve HTTP methods, URL paths, path parameter names, query parameter names, and expected JSON field names.

## 10. Testing Standards
- Testing is a first-class phase. Use `pytest`.
- Test happy paths, validation failures, 404s, auth failures, ownership violations, duplicate data, business rule failures, boundary values.
- Verify startup, database setup, and `/docs` availability manually/automatically.

## 11. Error-Handling Standards
- Return proper HTTP status codes (200, 201, 400, 401, 403, 404, 422). Never return 200 for errors.
- Error messages must be meaningful. Implement global exception handlers exactly when requested (Ass 4).

## 12. Validation Standards
- Pydantic validation via `Field(...)`, Enums, nested models, and optional fields where appropriate.
- Database/business logic must validate uniqueness, state transitions, existence, and ownership.

## 13. Security Standards
- Server-side authorization enforcement. Do not trust client-provided `user_id`s for user-owned resources; use the authenticated token payload.
- Hide sensitive fields (e.g., `unit_cost` in Ass 10) completely using response models.
- No hardcoded secrets. Use environment variables/`.env` when useful.

## 14. Anti-AI-Slop Rules
- The code MUST NOT look like generic AI-generated boilerplate.
- NO unnecessary factories, generic repositories, unused imports, dead code, placeholder functions, fake comments, or excessive wrapping.
- Simple router -> dependency -> service/logic -> DB flow unless assignment demands more.

## 15. Planning Rules
- A detailed implementation plan MUST be created and approved before any application code is written.
- The plan must sequence: structure -> models -> schemas -> auth -> logic -> routes -> tests -> audit -> package.

## 16. Execution Rules
- Execute the approved plan autonomously from start to finish for an assignment. Do not wait for manual instruction for every coding step.
- Only pause for blocking ambiguities, required external resources, risk of requirement violations, or manual approval stops.

## 17. Requirement Audit Rules
- Perform a manual requirement-by-requirement audit after passing tests.
- Status is only PASS or FAIL. No vague statuses. If FAIL, fix, retest, re-audit.

## 18. Submission Rules
- Every assignment ends in a clean ZIP matching the PDF requested format.
- ZIP must contain: source code, `requirements.txt`, `README.md`, migrations (if any).
- Exclude: `venv`, `.venv`, `__pycache__`, unneeded artifacts.

## 19. Assignment-by-assignment Definition of Done
1. Requirements documented.
2. Code implemented (models, schemas, auth, logic, routes).
3. Automated tests written and PASS.
4. Swagger tested manually (walkthrough in README).
5. Code statically reviewed (no slop, unused imports).
6. Requirement audit 100% PASS.
7. Submission ZIP created and clean-room verified.

## 20. Final Project Audit Checklist (Clean Room)
- [ ] Can I install requirements?
- [ ] Can I run the application?
- [ ] Can I open `/docs`?
- [ ] Can I authenticate/authorize?
- [ ] Do all required routes exist and match the PDF?
- [ ] Do request/response schemas match exactly?
- [ ] Are all explicit business rules and RBAC enforced?
- [ ] Is the ZIP structure clean and named correctly?

## 21. Forbidden Unnecessary Technologies
- NO frontend frameworks (React, Vue, HTML dashboards, etc.).
- NO microservices, Kafka, Redis, Celery, GraphQL, or over-engineered abstractions.

## 22. Current Implementation Progress
- Assignment 1: QuickShop [PASS]
- Assignment 2: PulseFit [PASS]
- Assignment 3: LibraFlow [PASS]
- Assignment 4: PennyWise [PASS]
- Assignment 5: GatherUp [PASS]
- Assignment 6: EduStream [PASS]
- Assignment 7: SyncTask [PASS]
- Assignment 8: Domos [PASS]
- Assignment 9: ChefPalette [PASS]
- Assignment 10: StockSync [PASS]
