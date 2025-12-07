from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = ""
    
    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # Fast and powerful (updated model)
    
    # Application
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:7860,http://localhost:3000"
    
    # LLM Settings
    MAX_CONTEXT_MESSAGES: int = 10  # Number of previous messages to include
    ESCALATION_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    
    # FAQ Settings
    TOP_K_FAQS: int = 3  # Number of relevant FAQs to retrieve
    
    class Config:
        # Look for .env in project root
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'


# Global settings instance
settings = Settings()
