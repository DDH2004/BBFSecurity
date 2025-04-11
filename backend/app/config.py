import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Private AI Assistant"
    
    # Auth0 settings
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_API_AUDIENCE: str = os.getenv("AUTH0_AUDIENCE", "")
    
    # Gemini API settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    # File storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    class Config:
        case_sensitive = True

settings = Settings()