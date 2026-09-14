# Domos — Smart Home IoT Manager

## Objective
Build a FastAPI-based Smart Home IoT Manager to register smart devices, manage states, and maintain logs.

## Features
- Custom Response Headers (`X-Process-Time`) via Middleware
- Middleware logging of requested endpoints and execution time
- Device state management with Enums
- Case-insensitive room filtering
- Device Change Logs (latest 10 logs)
- State validation based on device type (Bonus)

## Setup & Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Swagger Testing
1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Register Device: `POST /devices`
3. Update State: `PATCH /devices/{id}/state`
4. List Logs: `GET /devices/{id}/logs`

## Testing
```bash
python -m pytest
```

