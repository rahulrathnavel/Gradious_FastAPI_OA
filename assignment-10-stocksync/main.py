from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Union
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth
from database import engine, get_db

# We don't call create_all because we are using Alembic
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockSync - Warehouse Inventory API")

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def check_admin(user: models.User = Depends(auth.get_current_user)):
    if user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return user


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if item.selling_price < item.unit_cost:
        raise HTTPException(status_code=422, detail="Selling price lower than unit cost")
        
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    if current_user.role == models.RoleEnum.admin:
        return schemas.ItemAdminResponse.model_validate(db_item)
    else:
        return schemas.ItemManagerResponse.model_validate(db_item)

@app.get("/items/{id}")
def get_item(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
) -> Union[schemas.ItemAdminResponse, schemas.ItemManagerResponse]:
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if current_user.role == models.RoleEnum.admin:
        return schemas.ItemAdminResponse.model_validate(item)
    else:
        return schemas.ItemManagerResponse.model_validate(item)

@app.patch("/items/{id}/stock")
def update_stock(
    id: int,
    update: schemas.StockUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    new_quantity = item.quantity + update.change
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Negative stock")
        
    item.quantity = new_quantity
    db.commit()
    db.refresh(item)
    
    if current_user.role == models.RoleEnum.admin:
        return schemas.ItemAdminResponse.model_validate(item)
    else:
        return schemas.ItemManagerResponse.model_validate(item)

@app.get("/inventory/low-stock")
def get_low_stock(
    threshold: int = 10,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if threshold < 0:
        raise HTTPException(status_code=422, detail="Invalid threshold")
        
    items = db.query(models.Item).filter(models.Item.quantity < threshold).all()
    if current_user.role == models.RoleEnum.admin:
        return [schemas.ItemAdminResponse.model_validate(item) for item in items]
    else:
        return [schemas.ItemManagerResponse.model_validate(item) for item in items]

@app.get("/inventory/valuation", response_model=schemas.ValuationResponse)
def get_valuation(
    current_user: models.User = Depends(check_admin),
    db: Session = Depends(get_db)
):
    # Inventory Value = unit_cost * quantity
    total = db.query(func.sum(models.Item.unit_cost * models.Item.quantity)).scalar()
    return schemas.ValuationResponse(total_inventory_value=total or 0.0)

app.include_router(auth_router)

