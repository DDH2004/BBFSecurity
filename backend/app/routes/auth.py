from fastapi import APIRouter, Depends
from fastapi_auth0 import Auth0, Auth0User
from ..config import settings

auth0 = Auth0(domain=settings.AUTH0_DOMAIN, api_audience=settings.AUTH0_API_AUDIENCE)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/user")
async def get_user(user: Auth0User = Depends(auth0.get_user)):
    """Return the authenticated user's profile"""
    return {
        "id": user.id,
        "email": getattr(user, "email", None),
        "name": getattr(user, "name", None)
    }