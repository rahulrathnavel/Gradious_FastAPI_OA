from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduStream - Course Learning Platform")

auth_router = APIRouter(prefix="/auth", tags=["auth"])
courses_router = APIRouter(prefix="/courses", tags=["courses"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# Dependency instances
allow_teachers = auth.RoleChecker([models.RoleEnum.teacher])
allow_students = auth.RoleChecker([models.RoleEnum.student])

class EnrollmentChecker:
    def __call__(self, id: int, current_user: models.User = Depends(allow_students), db: Session = Depends(get_db)):
        enrollment = db.query(models.Enrollment).filter(
            models.Enrollment.user_id == current_user.id,
            models.Enrollment.course_id == id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Student not enrolled in this course")
        return current_user

check_enrollment = EnrollmentChecker()

@courses_router.post("", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: schemas.CourseCreate,
    current_user: models.User = Depends(allow_teachers),
    db: Session = Depends(get_db)
):
    db_course = models.Course(
        title=course.title,
        description=course.description,
        price=course.price,
        instructor_id=current_user.id
    )
    db.add(db_course)
    db.flush() # flush to get course.id
    
    for mod in course.modules:
        db_mod = models.Module(
            course_id=db_course.id,
            title=mod.title,
            content=mod.content,
            order_index=mod.order_index
        )
        db.add(db_mod)
        
    db.commit()
    db.refresh(db_course)
    return db_course

@courses_router.get("", response_model=list[schemas.CourseResponse])
def get_courses(instructor_name: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Course)
    if instructor_name:
        query = query.join(models.User).filter(models.User.email.ilike(f"%{instructor_name}%"))
    return query.all()

@courses_router.post("/{id}/enroll", status_code=status.HTTP_201_CREATED)
def enroll_course(
    id: int,
    current_user: models.User = Depends(allow_students),
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.course_id == id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Duplicate enrollment")
        
    enrollment = models.Enrollment(user_id=current_user.id, course_id=id)
    db.add(enrollment)
    db.commit()
    return {"message": "Enrolled successfully"}

@courses_router.get("/{id}/content", response_model=schemas.CourseWithModulesResponse)
def get_course_content(
    id: int,
    db: Session = Depends(get_db),
    enrolled_user: models.User = Depends(check_enrollment)
):
    course = db.query(models.Course).filter(models.Course.id == id).first()
    return course

@courses_router.patch("/{id}", response_model=schemas.CourseResponse)
def update_course(
    id: int,
    course_update: schemas.CourseUpdate,
    current_user: models.User = Depends(allow_teachers),
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this course")
        
    update_data = course_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
        
    db.commit()
    db.refresh(course)
    return course

app.include_router(auth_router)
app.include_router(courses_router)

