from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the request details
        logging.info(f"Request: {request.method} {request.url}")
        
        # Process the request
        response: Response = await call_next(request)
        
        # Log the response details
        logging.info(f"Response status: {response.status_code}")
        
        return response

# Add any additional middleware functions or classes as needed.