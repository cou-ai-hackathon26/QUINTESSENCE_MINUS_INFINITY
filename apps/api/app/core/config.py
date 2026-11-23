"""
Shongoti Core Settings and Database Configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Shongoti API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    
    # Financial Invariant: Default database is SQLite for local testability, PostgreSQL for production
    DATABASE_URL: str = Field(
        default="sqlite:///./apps/api/data/shongoti_dev.db",
        description="SQLAlchemy database connection string"
    )
    SECRET_KEY: str = "change-this-in-production-synthetic-test-key"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Optional integration settings
    GEMINI_API_KEY: str = ""
    AI_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_TEXT_MODEL: str = "openai/gpt-oss-120b"
    GROQ_VISION_MODEL: str = "qwen/qwen3.8-27b"
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"
    AI_TIMEOUT_SECONDS: float = 60.0
    AI_MAX_OUTPUT_TOKENS: int = 4096
    PDF_MAX_OCR_PAGES: int = 6
    SEMANTIC_ENABLED: bool = False
    SEMANTIC_MODEL_PATH: str = 'apps/api/data/models/multilingual-e5-small'
    SSLCOMMERZ_STORE_ID: str = ""
    SSLCOMMERZ_STORE_PASSWD: str = ""
    SSLCOMMERZ_IS_SANDBOX: bool = True


settings = Settings()
