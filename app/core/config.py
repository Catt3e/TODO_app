from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = os.getenv("VERIFICATION_TOKEN_EXPIRE_MINUTES", 60)

    EMAIL_HOST: str = os.getenv("EMAIL_HOST")
    EMAIL_PORT: int = os.getenv("EMAIL_PORT", 587)
    EMAIL_USER: str = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")

settings = Settings()