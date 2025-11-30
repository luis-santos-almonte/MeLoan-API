import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "MiPréstamo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/meloan_db"
    )
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

settings = Settings()