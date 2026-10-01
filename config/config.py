import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def normalize_database_url(database_url):
    if not database_url:
        return database_url
    if database_url.startswith("postgres://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgresql://"):]
    elif database_url.startswith("postgresql+psycopg://"):
        pass
    elif database_url.startswith("sqlite:///"):
        return database_url
    else:
        raise ValueError("DATABASE_URL must use SQLite or PostgreSQL with psycopg.")

    parsed = make_url(database_url)
    query = dict(parsed.query)
    query["sslmode"] = "require"
    return parsed.set(query=query).render_as_string(hide_password=False)


IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
IS_RENDER = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"))


def _database_url_from_environment():
    value = os.getenv("DATABASE_URL")
    if value:
        return normalize_database_url(value)
    if IS_RENDER or IS_VERCEL:
        raise RuntimeError("Set DATABASE_URL in the production environment.")
    return "sqlite:///./data/careerforge.db"


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY")
    DEBUG = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
    ROADMAP_API_KEY = os.getenv("ROADMAP_API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DATABASE_URL = _database_url_from_environment()
    SERVERLESS = IS_VERCEL
    AUTO_CREATE_SCHEMA = DATABASE_URL.startswith("sqlite:///")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "resumes")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in {"true", "1"}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT_DEFAULT", "120"))
    RATE_LIMIT_AI = int(os.getenv("RATE_LIMIT_AI", "10"))
    RATE_LIMIT_AUTH = int(os.getenv("RATE_LIMIT_AUTH", "5"))
    
    DATA_FOLDER = BASE_DIR / "data"
    PROMPTS_FOLDER = BASE_DIR / "prompts"
    
    # Vercel Functions reject request bodies above 4.5 MB before Flask sees them.
    MAX_CONTENT_LENGTH = (4 if IS_VERCEL else 10) * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    @staticmethod
    def init_app(app):
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError("Set FLASK_SECRET_KEY or SECRET_KEY in the environment.")
