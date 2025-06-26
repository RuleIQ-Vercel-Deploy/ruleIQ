"""
Environment Configuration Management for ComplianceGPT

This module handles all environment variables and configuration settings
using Pydantic for validation and type safety.
"""

from enum import Enum
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Environment
    env: Environment = Field(default=Environment.DEVELOPMENT, env="ENV")
    debug: bool = Field(default=False, env="DEBUG")

    @field_validator('debug', mode='before')
    @classmethod
    def validate_debug_bool(cls, v):
        """Coerce string 'truthy' values to boolean"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 't', 'y', 'yes', 'on')
        return bool(v)

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(('postgresql://', 'postgresql+psycopg2://', 'postgresql+asyncpg://')):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")
        return v

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="ALLOWED_ORIGINS"
    )

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    # AI Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # Redis (for caching and sessions)
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # File Uploads
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds

    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.env == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.env == Environment.TESTING

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
