# StockSync — Warehouse Inventory API

## Objective
Build a FastAPI-based Warehouse Inventory API using OAuth2, Response Model Filtering, and Alembic migrations.

## Features
- OAuth2 Authentication (`OAuth2PasswordRequestForm`)
- Role-Based Access Control (Admin vs Manager)
- Response Model Filtering (hiding `unit_cost` from managers)
- Stock Management (quantity +/- adjustments, negative prevention)
- Inventory Valuation (`unit_cost * quantity`)
- Low Stock filtering with variable threshold
- Alembic database schema migrations

## Setup & Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Apply database migrations:
   ```bash
   python -m alembic upgrade head
   ```
3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Swagger Testing
1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Register an Admin: `POST /auth/register` (role: admin)
3. Register a Manager: `POST /auth/register` (role: manager)
4. Authenticate: Use the Authorize button for either user.
5. Create Item: `POST /items`
6. Get Item: `GET /items/{id}` (Observe `unit_cost` presence based on role)
7. Update Stock: `PATCH /items/{id}/stock` (Pass `change` to adjust)
8. Low Stock: `GET /inventory/low-stock?threshold=10`
9. Valuation: `GET /inventory/valuation` (Admin only)

## Testing
```bash
python -m pytest
```

