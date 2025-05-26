import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING")
    DATABASE_NAME: str = "nobadpix"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    AZURE_CONTENT_SAFETY_ENDPOINT: str = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
    AZURE_CONTENT_SAFETY_KEY: str = os.getenv("AZURE_CONTENT_SAFETY_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 