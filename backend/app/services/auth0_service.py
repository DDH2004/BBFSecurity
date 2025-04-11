import json
import httpx
from urllib.request import urlopen
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

token_auth_scheme = HTTPBearer()

def get_token_auth_header(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    return credentials.credentials

def verify_jwt(token: str = Depends(get_token_auth_header)):
    """
    Verify a JWT token against Auth0
    """
    jsonurl = urlopen(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )
    
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=settings.AUTH0_ALGORITHMS,
                audience=settings.AUTH0_API_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.JWTClaimsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid claims: please check audience and issuer",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to parse authentication token",
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find appropriate key",
    )

async def get_auth0_token(username: str, password: str):
    """
    Get a token from Auth0 using Resource Owner Password flow
    Note: This flow must be enabled in your Auth0 tenant/application
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://{settings.AUTH0_DOMAIN}/oauth/token",
            data={
                "grant_type": "password",
                "username": username,
                "password": password,
                "client_id": settings.AUTH0_CLIENT_ID,
                "client_secret": settings.AUTH0_CLIENT_SECRET,
                "audience": settings.AUTH0_API_AUDIENCE,
                "scope": "openid profile email"
            }
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None