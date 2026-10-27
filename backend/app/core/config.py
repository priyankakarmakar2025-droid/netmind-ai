import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "NetMind AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./netmind.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

settings = Settings()
