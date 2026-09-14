from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SyncTask - Kanban Task Board API")

@app.post("/projects", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.post("/projects/{id}/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db_task = models.Task(**task.model_dump(), project_id=id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/projects/{id}/tasks")
def get_project_tasks(id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    tasks = db.query(models.Task).filter(models.Task.project_id == id).all()
    grouped_tasks = {
        "todo": [],
        "doing": [],
        "done": []
    }
    for task in tasks:
        # Pydantic conversion for response
        task_data = schemas.TaskResponse.model_validate(task).model_dump()
        grouped_tasks[task.status.value].append(task_data)
        
    return grouped_tasks

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task_status(task_id: int, update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Bonus: Prevent invalid status transitions
    # Example valid: todo -> doing -> done
    # Invalid: done -> todo, done -> doing
    if task.status == models.StatusEnum.done and update.status != models.StatusEnum.done:
        raise HTTPException(status_code=400, detail="Cannot transition from done")
    if task.status == models.StatusEnum.todo and update.status == models.StatusEnum.done:
        raise HTTPException(status_code=400, detail="Cannot skip doing stage")
        
    task.status = update.status
    db.commit()
    db.refresh(task)
    return task

@app.delete("/projects/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(project)
    db.commit()
    return None

