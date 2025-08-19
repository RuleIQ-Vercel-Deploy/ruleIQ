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
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import Field, field_validator
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
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===================================================================
    # GENERAL APP SETTINGS
    # ===================================================================
    app_name: str = Field(default="RuleIQ API", description="Application name")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Environment")
    debug: bool = Field(default=True, description="Debug mode")
    version: str = Field(default="1.0.0", description="API version")
    host: str = Field(default="0.0.0.0", description="Host to bind")
    port: int = Field(default=8000, description="Port to bind")

    # Computed properties
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING

    # ===================================================================
    # DATABASE SETTINGS
    # ===================================================================
    database_url: str = Field(..., description="Primary database URL")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    database_pool_timeout: int = Field(
        default=30, description="Database connection timeout (seconds)"
    )
    database_pool_recycle: int = Field(default=3600, description="Database connection recycle time")

    # ===================================================================
    # REDIS CACHE SETTINGS
    # ===================================================================
    redis_url: str = Field(..., description="Redis URL for caching")
    redis_max_connections: int = Field(default=20, description="Max Redis connections")
    redis_socket_keepalive: bool = Field(default=True, description="Redis socket keepalive")
    redis_socket_keepalive_options: Dict[str, int] = Field(
        default_factory=lambda: {}, description="Redis keepalive options"
    )

    # ===================================================================
    # JWT AUTHENTICATION
    # ===================================================================
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="JWT access token expiration (minutes)"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30, description="JWT refresh token expiration (days)"
    )

    # ===================================================================
    # GOOGLE OAUTH SETTINGS
    # ===================================================================
    google_client_id: Optional[str] = Field(default=None, description="Google OAuth client ID")
    google_client_secret: Optional[str] = Field(
        default=None, description="Google OAuth client secret"
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        description="Google OAuth redirect URI",
    )

    # ===================================================================
    # AI SERVICES (GOOGLE GEMINI)
    # ===================================================================
    google_api_key: str = Field(..., description="Google AI API key")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model")
    gemini_temperature: float = Field(default=0.1, description="Gemini temperature")
    gemini_max_tokens: int = Field(default=4096, description="Gemini max tokens")
    gemini_timeout: int = Field(default=60, description="Gemini request timeout")

    # AI service rate limiting
    ai_rate_limit_tier_1: int = Field(default=20, description="AI Tier 1 requests per minute")
    ai_rate_limit_tier_2: int = Field(default=10, description="AI Tier 2 requests per minute")
    ai_rate_limit_tier_3: int = Field(default=3, description="AI Tier 3 requests per minute")

    # AI cost tracking
    ai_cost_tracking_enabled: bool = Field(default=True, description="Enable AI cost tracking")
    ai_monthly_budget_limit: float = Field(
        default=500.0, description="Monthly AI budget limit (USD)"
    )
    ai_cost_alert_threshold: float = Field(
        default=0.8, description="Alert threshold (80% of budget)"
    )

    # ===================================================================
    # FILE UPLOAD SETTINGS
    # ===================================================================
    max_file_size_mb: int = Field(default=10, description="Max file upload size (MB)")
    upload_directory: str = Field(default="./uploads", description="File upload directory")
    allowed_file_types: Union[List[str], str] = Field(
        default=["pdf", "docx", "doc", "txt", "csv", "xlsx", "json"],
        description="Allowed file extensions",
    )

    # ===================================================================
    # SECURITY SETTINGS
    # ===================================================================
    password_min_length: int = Field(default=8, description="Minimum password length")
    bcrypt_rounds: int = Field(default=12, description="Bcrypt hashing rounds")
    session_timeout_minutes: int = Field(default=60, description="Session timeout (minutes)")

    # HTTPS and security headers
    force_https: bool = Field(default=False, description="Force HTTPS in production")
    secure_cookies: bool = Field(default=False, description="Use secure cookies")
    csrf_protection_enabled: bool = Field(default=True, description="Enable CSRF protection")

    # ===================================================================
    # CORS SETTINGS
    # ===================================================================
    cors_origins: Union[List[str], str] = Field(default=["http://localhost:3000"])
    cors_allowed_origins: Union[List[str], str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:8080",  # Debug suite origin
            "http://localhost:8080",  # Alternative debug suite origin
        ]
    )
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
        return []

    # ===================================================================
    # RATE LIMITING SETTINGS
    # ===================================================================
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=100, description="General rate limit per minute")
    auth_rate_limit_per_minute: int = Field(default=5, description="Auth rate limit per minute")

    # ===================================================================
    # LOGGING SETTINGS
    # ===================================================================
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_file_enabled: bool = Field(default=True, description="Enable file logging")
    log_file_path: str = Field(default="./logs/app.log", description="Log file path")
    log_file_max_bytes: int = Field(default=10_000_000, description="Max log file size (bytes)")
    log_file_backup_count: int = Field(default=5, description="Log file backup count")

    # ===================================================================
    # MONITORING SETTINGS
    # ===================================================================
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    performance_monitoring_enabled: bool = Field(
        default=True, description="Enable performance monitoring"
    )
    error_monitoring_enabled: bool = Field(default=True, description="Enable error monitoring")

    # ===================================================================
    # TASK QUEUE SETTINGS (Celery)
    # ===================================================================
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    celery_task_timeout: int = Field(default=300, description="Celery task timeout (seconds)")

    # ===================================================================
    # THIRD-PARTY INTEGRATIONS
    # ===================================================================
    # AWS Settings
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret key")
    aws_region: str = Field(default="eu-west-2", description="AWS region")
    s3_bucket_name: Optional[str] = Field(default=None, description="S3 bucket name")

    # Stripe Settings
    stripe_publishable_key: Optional[str] = Field(
        default=None, description="Stripe publishable key"
    )
    stripe_secret_key: Optional[str] = Field(default=None, description="Stripe secret key")
    stripe_webhook_secret: Optional[str] = Field(default=None, description="Stripe webhook secret")

    # ===================================================================
    # FEATURE FLAGS
    # ===================================================================
    agentic_assessments_enabled: bool = Field(
        default=False, description="Enable agentic assessments"
    )
    ai_policy_generation_enabled: bool = Field(
        default=True, description="Enable AI policy generation"
    )
    advanced_analytics_enabled: bool = Field(default=True, description="Enable advanced analytics")
    integration_sync_enabled: bool = Field(default=True, description="Enable integration sync")

    # ===================================================================
    # VALIDATION METHODS
    # ===================================================================

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite:///")):
            raise ValueError("Database URL must start with postgresql:// or sqlite:///")
        return v

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format"""
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with redis://")
        return v

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret key strength"""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    @field_validator("google_api_key")
    @classmethod
    def validate_google_api_key(cls, v: str) -> str:
        """Validate Google API key format"""
        if not v.startswith("AIza"):
            logger.warning(
                "Google API key may not be in the correct format (should start with 'AIza')"
            )
        return v

    @field_validator("max_file_size_mb")
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """Validate file size limits"""
        if v > 100:  # 100MB max
            raise ValueError("Max file size cannot exceed 100MB")
        return v

    @field_validator("bcrypt_rounds")
    @classmethod
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """Validate bcrypt rounds"""
        if v < 10 or v > 16:
            raise ValueError("Bcrypt rounds must be between 10 and 16")
        return v


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
