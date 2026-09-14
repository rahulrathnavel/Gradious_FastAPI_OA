# SyncTask — Kanban Task Board API

## Objective
Build a FastAPI-based Kanban Task Board API to manage projects and tasks with workflow stages.

## Features
- Pydantic Field Validation
- SQLAlchemy Relationship Mapping (One Project -> Many Tasks)
- Cascade Delete (Deleting Project deletes Tasks)
- Enum Validation (todo, doing, done)
- Task Status Transitions logic

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
2. Create Project: `POST /projects`
3. Create Task: `POST /projects/{id}/tasks`
4. Get Tasks: `GET /projects/{id}/tasks` (Tasks grouped by status)
5. Update Task: `PATCH /tasks/{task_id}`
6. Delete Project: `DELETE /projects/{id}`

## Testing
```bash
python -m pytest
```

