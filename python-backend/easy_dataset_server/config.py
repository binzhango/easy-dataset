"""
Server configuration.

This module provides configuration settings for the FastAPI server.
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Easy Dataset API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///easy_dataset.db"
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    # File upload
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    
    # Task processing
    max_concurrent_tasks: int = 5
    task_timeout: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

