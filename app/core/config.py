from pydantic import BaseSettings

class Settings(BaseSettings):
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    gemini_api_key: str
    midnight_api_key: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()