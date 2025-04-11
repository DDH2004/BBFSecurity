import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Agent Simulation System"
    API_V1_STR: str = "/api/v1"
    
    # Gemini API settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "agent_simulation")
    
    # Midnight security settings
    MIDNIGHT_API_KEY: str = os.getenv("MIDNIGHT_API_KEY", "")
    
    # Auth0 settings
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_API_AUDIENCE: str = os.getenv("AUTH0_API_AUDIENCE", "")
    AUTH0_ALGORITHMS: list = ["RS256"]
    AUTH0_CLIENT_ID: str = os.getenv("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET: str = os.getenv("AUTH0_CLIENT_SECRET", "")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()