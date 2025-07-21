"""
Environment Configuration Management for RuleIQ

This module handles all environment variables and configuration settings
using Pydantic for validation and type safety.
"""

from dotenv import load_dotenv

# Load .env.local file at the very top to ensure variables are available
load_dotenv(".env.local")

import json
import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def parse_list_from_string(v: Union[str, list]) -> list:
    """Parse a list from string or return as-is if already a list."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        # Try JSON parsing first
        if v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        # Otherwise split by comma
        return [item.strip() for item in v.split(",") if item.strip()]
    # Return empty list for other types
    return []


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

    # ===================================================================
    # APPLICATION SETTINGS
    # ===================================================================
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    app_name: str = Field(default="RuleIQ")
    app_version: str = Field(default="1.0.0")
    app_url: str = Field(default="http://localhost:3000")
    api_version: str = Field(default="v1")

    # ===================================================================
    # SERVER CONFIGURATION
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    # ============================================================
    # ============================================================
    # DATABASE CONFIGURATION
    # ============================================================
    database_url: str = Field(default="postgresql://localhost/ruleiq")
    test_database_url: Optional[str] = Field(default=None)

    # Database pool settings
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)
    db_pool_timeout: int = Field(default=30)
    db_pool_recycle: int = Field(default=3600)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        allowed_prefixes = ("postgresql://", "postgresql+psycopg2://", "postgresql+asyncpg://")
        if not v.startswith(allowed_prefixes):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")
        return v

    # ===================================================================
    # REDIS CONFIGURATION
    # ===================================================================
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)

    # Redis for specific purposes
    cache_redis_url: str = Field(default="redis://localhost:6379/1")
    session_redis_url: str = Field(default="redis://localhost:6379/2")

    # ============================================================
    # JWT CONFIGURATION
    # ============================================================
    jwt_secret: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET", "dev-secret-key-change-in-production"),
        description="Secret key for signing JWT tokens. Must be set via environment variable.",
    )

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        """Ensure JWT secret is properly set and secure."""
        # Skip validation for empty string during initialization
        if not v:
            return v

        forbidden_values = [
            "dev-secret-key-change-in-production",
            "your-secret-key-here-change-this-in-production",
            "secret",
            "password",
            "123456",
        ]

        if v in forbidden_values:
            env = info.data.get("environment")
            if env == Environment.PRODUCTION:
                raise ValueError(
                    "JWT_SECRET environment variable must be set in production. "
                    "Use a cryptographically secure random string of at least 256 bits."
                )
            # In development, allow the default but warn
            if v == "dev-secret-key-change-in-production":
                logger.warning(
                    "Using default JWT secret for development. "
                    "Set JWT_SECRET environment variable for security."
                )

        # Ensure minimum security requirements
        if len(v) < 32 and info.data.get("environment") == Environment.PRODUCTION:
            raise ValueError("JWT_SECRET must be at least 32 characters long in production")

        return v

    # ===================================================================
    # CORS SETTINGS
    # ===================================================================
    cors_origins: Union[List[str], str] = Field(default=["http://localhost:3000"])
    cors_allowed_origins: Union[List[str], str] = Field(default=["http://localhost:3000"])
    allowed_hosts: Union[List[str], str] = Field(default=["localhost", "127.0.0.1"])

    @field_validator(
        "cors_origins", "cors_allowed_origins", "allowed_hosts", "allowed_file_types", mode="before"
    )
    @classmethod
    def parse_list_fields(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse list fields from string or return as-is"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle JSON format
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated format
            return [item.strip() for item in v.split(",") if item.strip()]
        # Return empty list for other types - this is reachable
        return []

    # ===================================================================
    # OAUTH CONFIGURATION
    # ===================================================================
    google_client_id: Optional[str] = Field(default=None)
    google_client_secret: Optional[str] = Field(default=None)
    microsoft_client_id: Optional[str] = Field(default=None)
    microsoft_client_secret: Optional[str] = Field(default=None)
    okta_client_id: Optional[str] = Field(default=None)
    okta_client_secret: Optional[str] = Field(default=None)

    # ============================================================
    # AI & EXTERNAL SERVICES
    # ============================================================
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    google_ai_api_key: Optional[str] = Field(default=None)
    # ===================================================================
    # AWS CONFIGURATION
    # ===================================================================
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    aws_s3_bucket: Optional[str] = Field(default=None)

    # ===================================================================
    # EMAIL CONFIGURATION
    # ===================================================================
    smtp_host: str = Field(default="localhost")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    smtp_use_tls: bool = Field(default=True)
    smtp_from_email: str = Field(default="noreply@ruleiq.com")
    smtp_from_name: str = Field(default="RuleIQ")

    # ===================================================================
    # FILE UPLOAD SETTINGS
    # ===================================================================
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    allowed_file_types: Union[List[str], str] = Field(
        default=[
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "txt",
            "csv",
            "jpg",
            "jpeg",
            "png",
            "gif",
        ]
    )
    upload_dir: str = Field(default="uploads")
    temp_dir: str = Field(default="temp")

    # ===================================================================
    # RATE LIMITING
    # ===================================================================
    rate_limit_per_minute: int = Field(default=100)
    rate_limit_burst: int = Field(default=10)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)

    # ===================================================================
    # MONITORING & LOGGING
    # ===================================================================
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: str = Field(default="development")
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)

    # ===================================================================
    # BUSINESS LOGIC SETTINGS
    # ===================================================================
    default_page_size: int = Field(default=20)
    max_page_size: int = Field(default=100)
    cache_ttl: int = Field(default=300)  # 5 minutes
    assessment_timeout: int = Field(default=1800)  # 30 minutes
    chat_history_limit: int = Field(default=50)

    # ===================================================================
    # FEATURE FLAGS
    # ===================================================================
    enable_ai_features: bool = Field(default=True)
    enable_oauth: bool = Field(default=True)
    enable_email_notifications: bool = Field(default=True)
    enable_file_upload: bool = Field(default=True)
    enable_real_time_notifications: bool = Field(default=True)
    enable_advanced_analytics: bool = Field(default=False)

    # ===================================================================
    # PAYMENT & BILLING
    # ===================================================================
    stripe_publishable_key: Optional[str] = Field(default=None)
    stripe_secret_key: Optional[str] = Field(default=None)
    stripe_webhook_secret: Optional[str] = Field(default=None)

    # ===================================================================
    # DEVELOPMENT TOOLS
    # ===================================================================
    hot_reload: bool = Field(default=True)
    debug_toolbar: bool = Field(default=True)
    sql_debug: bool = Field(default=False)
    profiler_enabled: bool = Field(default=False)

    # ===================================================================
    # HEALTH CHECKS
    # ===================================================================
    health_check_interval: int = Field(default=30)
    health_check_timeout: int = Field(default=5)

    # ===================================================================
    # NEXT.JS FRONTEND
    # ===================================================================
    next_public_api_url: str = Field(default="http://localhost:8000")

    def model_post_init(self, __context) -> None:
        """Add diagnostic logging after model initialization."""
        print(
            f"[SETTINGS INIT] JWT_SECRET loaded: {self.jwt_secret[:10] if self.jwt_secret else 'None'}..."
        )
        print(f"[SETTINGS INIT] Working directory: {os.getcwd()}")
        print(f"[SETTINGS INIT] Environment: {self.environment}")

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Disable JSON parsing for list fields - we'll handle it in validators
        json_schema_extra={"env_parse_none_str": None},
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment == Environment.TESTING

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode"""
        return self.environment == Environment.STAGING

    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary"""
        return {
            "url": self.database_url,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
            "pool_recycle": self.db_pool_recycle,
        }

    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary"""
        return {
            "url": self.redis_url,
            "host": self.redis_host,
            "port": self.redis_port,
            "db": self.redis_db,
        }

    @property
    def smtp_config(self) -> Dict[str, Any]:
        """Get SMTP configuration dictionary"""
        return {
            "host": self.smtp_host,
            "port": self.smtp_port,
            "username": self.smtp_username,
            "password": self.smtp_password,
            "use_tls": self.smtp_use_tls,
            "from_email": self.smtp_from_email,
            "from_name": self.smtp_from_name,
        }


# Global settings instance - initialized lazily
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings"""
    return _get_or_create_settings()


def reload_settings() -> Settings:
    """Reload settings from environment variables"""
    return _create_new_settings()


def _get_or_create_settings() -> Settings:
    """Get existing settings or create new ones"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def _create_new_settings() -> Settings:
    """Create new settings instance"""
    global _settings
    _settings = Settings()
    return _settings
    return _settings


# Create default settings instance
settings = get_settings()
