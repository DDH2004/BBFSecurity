from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import jwt  # PyJWT for JSON Web Tokens
import logging
from pymongo import MongoClient

# -------------------------------
# Configuration & Setup
# -------------------------------

SECRET_KEY = "your-secret-key"  # Use a strong secret key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration period

# Configure basic logging to file
logging.basicConfig(filename="auth_usage.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize FastAPI application
app = FastAPI()

# MongoDB connection (assumes MongoDB is running locally)
client = MongoClient("mongodb://localhost:27017/")
db = client.mydatabase
collection = db.mycollection

# OAuth2 scheme setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# -------------------------------
# Data Models
# -------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Dummy user database for demonstration purposes
fake_users_db = {
    "agent1": {
        "username": "agent1",
        "password": "secret",  # In production, store hashed passwords
    },
}

# -------------------------------
# Helper Functions
# -------------------------------

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------------------
# OAuth2 Endpoints
# -------------------------------

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint for obtaining an access token using OAuth2.
    Uses a simple form-based username/password for demonstration.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------------------
# Token Validation & Logging Middleware
# -------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validates the token and logs usage.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Log token usage
    logging.info(f"Token used by {token_data.username}")
    return token_data

# -------------------------------
# Data Query Endpoint (Read-Only)
# -------------------------------

@app.get("/data")
async def read_data(current_user: TokenData = Depends(get_current_user)):
    """
    Read-only endpoint that retrieves data from MongoDB.
    Only accessible to authenticated users.
    """
    # Retrieve data from MongoDB (example query, adjust as needed)
    results = list(collection.find({}, {"_id": 0}))  # Exclude _id field from output
    return {"user": current_user.username, "data": results}

# -------------------------------
# Running the Application Locally
# -------------------------------
# Use `uvicorn` to run this app locally:
#   uvicorn app:app --reload
