import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def normalize_database_url(database_url):
    if database_url.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url[len("postgres://"):]
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url[len("postgresql://"):]
    return database_url


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY")
    DEBUG = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
    ROADMAP_API_KEY = os.getenv("ROADMAP_API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DATABASE_URL = normalize_database_url(
        os.getenv("DATABASE_URL") or "sqlite:///./data/careerforge.db"
    )
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in {"true", "1"}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT_DEFAULT", "120"))
    RATE_LIMIT_AI = int(os.getenv("RATE_LIMIT_AI", "10"))
    RATE_LIMIT_AUTH = int(os.getenv("RATE_LIMIT_AUTH", "5"))
    
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    DATA_FOLDER = BASE_DIR / "data"
    PROMPTS_FOLDER = BASE_DIR / "prompts"
    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB upload limit
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    @staticmethod
    def init_app(app):
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError("Set FLASK_SECRET_KEY or SECRET_KEY in the environment.")
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DATA_FOLDER, exist_ok=True)
        os.makedirs(Config.PROMPTS_FOLDER, exist_ok=True)
