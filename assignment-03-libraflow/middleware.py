import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Example output: GET /books completed in 12.45 ms
        logger.info(f"{request.method} {request.url.path} completed in {process_time:.2f} ms")
        return response

