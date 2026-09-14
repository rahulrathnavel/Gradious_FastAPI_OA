from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PulseFit - Fitness & Workout Tracker API")

users_router = APIRouter(prefix="/users", tags=["users"])
workouts_router = APIRouter(prefix="/workouts", tags=["workouts"])

@users_router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserSignup, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password=hashed_password, fitness_level=user.fitness_level)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@users_router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@workouts_router.post("", response_model=schemas.WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: schemas.WorkoutCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_workout = models.Workout(**workout.model_dump(), user_id=current_user.id)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@workouts_router.get("", response_model=list[schemas.WorkoutResponse])
def get_workouts(
    limit: int = 10,
    offset: int = 0,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    workouts = db.query(models.Workout).filter(models.Workout.user_id == current_user.id).offset(offset).limit(limit).all()
    return workouts


def calculate_workout_stats(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    total_calories = db.query(func.sum(models.Workout.calories_burned)).filter(models.Workout.user_id == current_user.id).scalar()
    return schemas.WorkoutStats(total_calories_burned=total_calories or 0.0)

@workouts_router.get("/stats", response_model=schemas.WorkoutStats)
def get_workout_stats_route(stats: schemas.WorkoutStats = Depends(calculate_workout_stats)):
    return stats


@workouts_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.Workout).filter(models.Workout.id == id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    if workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workout")
        
    db.delete(workout)
    db.commit()
    return None


app.include_router(users_router)
app.include_router(workouts_router)

