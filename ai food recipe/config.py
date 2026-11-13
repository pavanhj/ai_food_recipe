import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "bca_recipe_ai_secret_key_default_987654")
    
    # Gemini AI Config
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    
    # MySQL Database Config
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "recipe_db")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    
    # Flask settings
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
