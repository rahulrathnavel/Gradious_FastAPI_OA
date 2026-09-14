from fastapi import Request
from fastapi.responses import JSONResponse

class TransactionNotFoundError(Exception):
    pass

class InsufficientBalanceError(Exception):
    pass

class UnauthorizedAccessError(Exception):
    pass

class InvalidTransactionError(Exception):
    def __init__(self, message: str):
        self.message = message

def transaction_not_found_handler(request: Request, exc: TransactionNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Transaction not found"})

def insufficient_balance_handler(request: Request, exc: InsufficientBalanceError):
    return JSONResponse(status_code=400, content={"detail": "Insufficient balance"})

def unauthorized_access_handler(request: Request, exc: UnauthorizedAccessError):
    return JSONResponse(status_code=403, content={"detail": "Unauthorized access"})

def invalid_transaction_handler(request: Request, exc: InvalidTransactionError):
    return JSONResponse(status_code=400, content={"detail": exc.message})

