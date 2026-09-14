from fastapi import FastAPI, Depends, HTTPException, status, Security, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import extract
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth, exceptions
from database import engine, get_db
from datetime import datetime, timezone

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PennyWise - Personal Finance Tracker")

app.add_exception_handler(exceptions.TransactionNotFoundError, exceptions.transaction_not_found_handler)
app.add_exception_handler(exceptions.InsufficientBalanceError, exceptions.insufficient_balance_handler)
app.add_exception_handler(exceptions.UnauthorizedAccessError, exceptions.unauthorized_access_handler)
app.add_exception_handler(exceptions.InvalidTransactionError, exceptions.invalid_transaction_handler)

auth_router = APIRouter(prefix="/auth", tags=["auth"])
transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password=hashed_password, strict_mode=user.strict_mode, scope=user.scope)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_scopes = user.scope.split(" ")
    if not form_data.scopes:
        granted_scopes = user_scopes
    else:
        granted_scopes = [s for s in form_data.scopes if s in user_scopes]
        
    access_token = auth.create_access_token(
        data={"sub": user.email, "scopes": granted_scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def _get_current_balance(user_id: int, db: Session) -> float:
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id, 
        models.Transaction.is_active == True
    ).all()
    income = sum(t.amount for t in transactions if t.type == models.TransactionTypeEnum.income)
    expense = sum(t.amount for t in transactions if t.type == models.TransactionTypeEnum.expense)
    return income - expense

@transactions_router.post("", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Security(auth.get_current_user, scopes=["write_transactions"]),
    db: Session = Depends(get_db)
):
    if current_user.strict_mode and transaction.type == models.TransactionTypeEnum.expense:
        balance = _get_current_balance(current_user.id, db)
        if transaction.amount > balance:
            raise exceptions.InsufficientBalanceError()

    db_transaction = models.Transaction(
        **transaction.model_dump(), 
        user_id=current_user.id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@transactions_router.get("/summary", response_model=schemas.FinancialSummary)
def get_summary(
    current_user: models.User = Security(auth.get_current_user, scopes=["read_transactions"]),
    db: Session = Depends(get_db)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id, 
        models.Transaction.is_active == True
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.type == models.TransactionTypeEnum.income)
    total_expense = sum(t.amount for t in transactions if t.type == models.TransactionTypeEnum.expense)
    
    return schemas.FinancialSummary(
        total_income=total_income,
        total_expense=total_expense,
        current_balance=total_income - total_expense
    )


@transactions_router.get("", response_model=list[schemas.TransactionResponse])
def get_transactions(
    month: int | None = None,
    year: int | None = None,
    current_user: models.User = Security(auth.get_current_user, scopes=["read_transactions"]),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.is_active == True
    )
    
    if month:
        query = query.filter(extract('month', models.Transaction.created_at) == month)
    if year:
        query = query.filter(extract('year', models.Transaction.created_at) == year)
        
    return query.all()


@transactions_router.put("/{id}", response_model=schemas.TransactionResponse)
def update_transaction(
    id: int,
    transaction_update: schemas.TransactionUpdate,
    current_user: models.User = Security(auth.get_current_user, scopes=["write_transactions"]),
    db: Session = Depends(get_db)
):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == id).first()
    if not db_transaction:
        raise exceptions.TransactionNotFoundError()
        
    if db_transaction.user_id != current_user.id:
        raise exceptions.UnauthorizedAccessError()
        
    time_diff = datetime.utcnow() - db_transaction.created_at
    if time_diff.total_seconds() > 24 * 3600:
        raise exceptions.InvalidTransactionError("Transaction date must not be changed after 24 hours from creation.")
        
    # Check strict mode again if changing to expense or increasing expense
    new_type = transaction_update.type if transaction_update.type else db_transaction.type
    new_amount = transaction_update.amount if transaction_update.amount is not None else db_transaction.amount
    
    if current_user.strict_mode and new_type == models.TransactionTypeEnum.expense:
        # Re-calculate balance without this specific transaction to see if the new amount fits
        balance_without_this = _get_current_balance(current_user.id, db)
        if db_transaction.type == models.TransactionTypeEnum.expense:
            balance_without_this += db_transaction.amount
        elif db_transaction.type == models.TransactionTypeEnum.income:
            balance_without_this -= db_transaction.amount
            
        if new_amount > balance_without_this:
            raise exceptions.InsufficientBalanceError()

    update_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
        
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@transactions_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    id: int,
    current_user: models.User = Security(auth.get_current_user, scopes=["write_transactions"]),
    db: Session = Depends(get_db)
):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == id).first()
    if not db_transaction:
        raise exceptions.TransactionNotFoundError()
        
    if db_transaction.user_id != current_user.id:
        raise exceptions.UnauthorizedAccessError()
        
    db_transaction.is_active = False
    db.commit()
    return None

app.include_router(auth_router)
app.include_router(transactions_router)

