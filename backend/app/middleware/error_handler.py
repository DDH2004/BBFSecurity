from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose.exceptions import JWTError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

async def jwt_exception_handler(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid authentication credentials"},
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

def add_error_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(JWTError, jwt_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)