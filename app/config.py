from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

COCKTAIL_API_KEY = os.getenv("COCKTAIL_API_KEY")
COCKTAIL_BASE_URL = os.getenv("COCKTAIL_BASE_URL")


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 
    COCKTAIL_API_KEY: str
    COCKTAIL_BASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()