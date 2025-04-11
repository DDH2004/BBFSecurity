from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth0_service import verify_jwt
from app.models.schemas import Token, UserInfo

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # This would typically interact with Auth0 to get a token
    # For now, we'll simulate this process
    from app.services.auth0_service import get_auth0_token
    
    token = await get_auth0_token(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserInfo)
async def read_users_me(current_user: dict = Depends(verify_jwt)):
    """
    Get current user info
    """
    # Extract user information from the JWT payload
    return UserInfo(
        id=current_user.get("sub", ""),
        email=current_user.get("email", ""),
        is_active=True
    )