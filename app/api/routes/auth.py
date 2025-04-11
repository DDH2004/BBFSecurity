from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing_user = await auth_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await auth_service.create_user(user)
    return new_user

@router.post("/login", response_model=UserResponse)
async def login(user: UserCreate):
    user_data = await auth_service.authenticate_user(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user_data.email})
    return {"access_token": access_token, "token_type": "bearer", **user_data.dict()}