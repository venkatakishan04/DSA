from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://hiresmart_user:hiresmart_password@localhost:5432/hiresmart_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # AI Models
    WHISPER_MODEL_PATH: str = "./ai-models/whisper"
    FACE_DETECTION_MODEL_PATH: str = "./ai-models/face-detection"
    EMOTION_MODEL_PATH: str = "./ai-models/emotion-detection"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/hiresmart.log"
    
    # Code Execution
    CODE_EXECUTION_TIMEOUT: int = 30
    MAX_MEMORY_USAGE: str = "128MB"
    ALLOWED_LANGUAGES: List[str] = ["python", "javascript", "java", "cpp"]
    
    # Interview Settings
    MAX_INTERVIEW_DURATION: int = 3600  # 1 hour in seconds
    REAL_TIME_ANALYSIS_INTERVAL: float = 2.0  # seconds
    
    # Assessment Settings
    DEFAULT_CODING_TIME_LIMIT: int = 1800  # 30 minutes
    MCQ_TIME_LIMIT: int = 1200  # 20 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(settings.WHISPER_MODEL_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.FACE_DETECTION_MODEL_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.EMOTION_MODEL_PATH).mkdir(parents=True, exist_ok=True)
