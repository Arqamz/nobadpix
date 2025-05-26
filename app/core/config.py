import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "nobadpix")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    ADMIN_TOKEN_STRING: str = os.getenv("ADMIN_TOKEN_STRING", "supersecretadmintoken")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    AZURE_CONTENT_SAFETY_ENDPOINT: str = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
    AZURE_CONTENT_SAFETY_KEY: str = os.getenv("AZURE_CONTENT_SAFETY_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 