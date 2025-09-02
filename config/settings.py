"""
Environment Configuration Management for RuleIQ

This module handles all environment variables and configuration settings
using Pydantic for validation and type safety.
"""
from __future__ import annotations

# Constants
DEFAULT_LIMIT = 100

"""
🔐 SECURE SECRETS VAULT INTEGRATION:
Uses AWS Secrets Manager for production secrets with environment fallback.
All sensitive configuration is retrieved through the SecretsVault class.
"""
import logging
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
load_dotenv('.env.local')
import json
import logging
import os
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
try:
    from .secrets_vault import get_secrets_vault, SecretKeys
    SECRETS_VAULT_AVAILABLE = True
except ImportError:
    logger.warning(
        '⚠️ SecretsVault not available, falling back to environment variables')
    SECRETS_VAULT_AVAILABLE = False
logger = logging.getLogger(__name__)


def get_secret_or_env(secret_key: str, env_key: Optional[str]=None) ->Optional[
    str]:
    """
    🔐 Get secret from SecretsVault or environment variable fallback

    Args:
        secret_key: Key used in SecretsVault (e.g., 'database_url')
        env_key: Environment variable key (defaults to secret_key.upper())

    Returns:
        Secret value or None if not found
    """
    if SECRETS_VAULT_AVAILABLE:
        vault = get_secrets_vault()
        value = vault.get_secret(secret_key)
        if value:
            logger.debug("🔐 Retrieved '%s' from SecretsVault" % secret_key)
            return value
    env_key = env_key or secret_key.upper()
    value = os.getenv(env_key)
    if value:
        logger.debug("🔐 Retrieved '%s' from environment (%s)" % (secret_key,
            env_key))
        return value
    logger.warning("⚠️ Secret '%s' not found in vault or environment" %
        secret_key)
    return None


def parse_list_from_string(v: Union[str, list]) ->list:
    """Parse a list from string or return as-is if already a list."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        if v.startswith('[') and v.endswith(']'):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in v.split(',') if item.strip()]
    return []


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding=
        'utf-8', case_sensitive=False, extra='ignore')
    app_name: str = Field(default='RuleIQ API', description='Application name')
    environment: Environment = Field(default=Environment.DEVELOPMENT,
        description='Environment')
    debug: bool = Field(default=True, description='Debug mode')
    version: str = Field(default='1.0.0', description='API version')
    host: str = Field(default='0.0.0.0', description='Host to bind')
    port: int = Field(default=8000, description='Port to bind')

    @property
    def is_development(self) ->bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) ->bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) ->bool:
        return self.environment == Environment.TESTING
    database_url: str = Field(default_factory=lambda : get_secret_or_env(
        SecretKeys.DATABASE_URL if SECRETS_VAULT_AVAILABLE else
        'database_url', 'DATABASE_URL') or 'postgresql://localhost/ruleiq',
        description='Primary database URL (🔐 from SecretsVault)')
    database_pool_size: int = Field(default=10, description=
        'Database connection pool size')
    database_max_overflow: int = Field(default=20, description=
        'Database max overflow connections')
    database_pool_timeout: int = Field(default=30, description=
        'Database connection timeout (seconds)')
    database_pool_recycle: int = Field(default=3600, description=
        'Database connection recycle time')
    redis_url: str = Field(default_factory=lambda : get_secret_or_env(
        SecretKeys.REDIS_URL if SECRETS_VAULT_AVAILABLE else 'redis_url',
        'REDIS_URL') or 'redis://localhost:6379/0', description=
        'Redis URL for caching (🔐 from SecretsVault)')
    redis_max_connections: int = Field(default=20, description=
        'Max Redis connections')
    redis_socket_keepalive: bool = Field(default=True, description=
        'Redis socket keepalive')
    redis_socket_keepalive_options: Dict[str, int] = Field(default_factory=
        lambda : {}, description='Redis keepalive options')
    jwt_secret_key: str = Field(default_factory=lambda : get_secret_or_env(
        SecretKeys.JWT_SECRET if SECRETS_VAULT_AVAILABLE else 'jwt_secret',
        'JWT_SECRET_KEY') or 'insecure-dev-key-change-in-production',
        description='JWT secret key (🔐 from SecretsVault)')
    jwt_algorithm: str = Field(default='HS256', description='JWT algorithm')
    jwt_access_token_expire_minutes: int = Field(default=30, description=
        'JWT access token expiration (minutes)')
    jwt_refresh_token_expire_days: int = Field(default=30, description=
        'JWT refresh token expiration (days)')
    google_client_id: Optional[str] = Field(default_factory=lambda :
        get_secret_or_env(SecretKeys.GOOGLE_CLIENT_ID if
        SECRETS_VAULT_AVAILABLE else 'google_client_id', 'GOOGLE_CLIENT_ID'
        ), description='Google OAuth client ID (🔐 from SecretsVault)')
    google_client_secret: Optional[str] = Field(default_factory=lambda :
        get_secret_or_env(SecretKeys.GOOGLE_CLIENT_SECRET if
        SECRETS_VAULT_AVAILABLE else 'google_client_secret',
        'GOOGLE_CLIENT_SECRET'), description=
        'Google OAuth client secret (🔐 from SecretsVault)')
    google_redirect_uri: str = Field(default=
        'http://localhost:8000/api/v1/auth/google/callback', description=
        'Google OAuth redirect URI')
    google_api_key: str = Field(default_factory=lambda : get_secret_or_env(
        SecretKeys.GOOGLE_AI_API_KEY if SECRETS_VAULT_AVAILABLE else
        'google_ai_api_key', 'GOOGLE_AI_API_KEY') or
        'placeholder-change-in-production', description=
        'Google AI API key (🔐 from SecretsVault)')
    gemini_model: str = Field(default='gemini-1.5-flash', description=
        'Gemini model')
    gemini_temperature: float = Field(default=0.1, description=
        'Gemini temperature')
    gemini_max_tokens: int = Field(default=4096, description=
        'Gemini max tokens')
    gemini_timeout: int = Field(default=60, description=
        'Gemini request timeout')
    ai_rate_limit_tier_1: int = Field(default=20, description=
        'AI Tier 1 requests per minute')
    ai_rate_limit_tier_2: int = Field(default=10, description=
        'AI Tier 2 requests per minute')
    ai_rate_limit_tier_3: int = Field(default=3, description=
        'AI Tier 3 requests per minute')
    ai_cost_tracking_enabled: bool = Field(default=True, description=
        'Enable AI cost tracking')
    ai_monthly_budget_limit: float = Field(default=500.0, description=
        'Monthly AI budget limit (USD)')
    ai_cost_alert_threshold: float = Field(default=0.8, description=
        'Alert threshold (80% of budget)')
    max_file_size_mb: int = Field(default=10, description=
        'Max file upload size (MB)')
    upload_directory: str = Field(default='./uploads', description=
        'File upload directory')
    allowed_file_types: Union[List[str], str] = Field(default=['pdf',
        'docx', 'doc', 'txt', 'csv', 'xlsx', 'json'], description=
        'Allowed file extensions')
    password_min_length: int = Field(default=8, description=
        'Minimum password length')
    bcrypt_rounds: int = Field(default=12, description='Bcrypt hashing rounds')
    session_timeout_minutes: int = Field(default=60, description=
        'Session timeout (minutes)')
    force_https: bool = Field(default=False, description=
        'Force HTTPS in production')
    secure_cookies: bool = Field(default=False, description=
        'Use secure cookies')
    csrf_protection_enabled: bool = Field(default=True, description=
        'Enable CSRF protection')
    cors_origins: Union[List[str], str] = Field(default=[
        'http://localhost:3000'])
    cors_allowed_origins: Union[List[str], str] = Field(default=[
        'http://localhost:3000', 'http://127.0.0.1:8080',
        'http://localhost:8080'])
    allowed_hosts: Union[List[str], str] = Field(default=['localhost',
        '127.0.0.1'])

    @field_validator('cors_origins', 'cors_allowed_origins',
        'allowed_hosts', 'allowed_file_types', mode='before')
    @classmethod
    def parse_list_fields(cls, v: Union[str, List[str]]) ->List[str]:
        """Parse list fields from string or return as-is"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in v.split(',') if item.strip()]
        return []
    rate_limit_enabled: bool = Field(default=True, description=
        'Enable rate limiting')
    rate_limit_per_minute: int = Field(default=100, description=
        'General rate limit per minute')
    auth_rate_limit_per_minute: int = Field(default=5, description=
        'Auth rate limit per minute')
    log_level: LogLevel = Field(default=LogLevel.INFO, description=
        'Logging level')
    log_file_enabled: bool = Field(default=True, description=
        'Enable file logging')
    log_file_path: str = Field(default='./logs/app.log', description=
        'Log file path')
    log_file_max_bytes: int = Field(default=10000000, description=
        'Max log file size (bytes)')
    log_file_backup_count: int = Field(default=5, description=
        'Log file backup count')
    monitoring_enabled: bool = Field(default=True, description=
        'Enable monitoring')
    performance_monitoring_enabled: bool = Field(default=True, description=
        'Enable performance monitoring')
    error_monitoring_enabled: bool = Field(default=True, description=
        'Enable error monitoring')
    celery_broker_url: Optional[str] = Field(default_factory=lambda :
        get_secret_or_env('celery_broker_url', 'CELERY_BROKER_URL'),
        description='Celery broker URL (🔐 from SecretsVault)')
    celery_result_backend: Optional[str] = Field(default_factory=lambda :
        get_secret_or_env('celery_result_backend', 'CELERY_RESULT_BACKEND'),
        description='Celery result backend (🔐 from SecretsVault)')
    celery_task_timeout: int = Field(default=300, description=
        'Celery task timeout (seconds)')
    aws_access_key_id: Optional[str] = Field(default=None, description=
        'AWS access key')
    aws_secret_access_key: Optional[str] = Field(default=None, description=
        'AWS secret key')
    aws_region: str = Field(default='eu-west-2', description='AWS region')
    s3_bucket_name: Optional[str] = Field(default=None, description=
        'S3 bucket name')
    stripe_publishable_key: Optional[str] = Field(default=None, description
        ='Stripe publishable key')
    stripe_secret_key: Optional[str] = Field(default=None, description=
        'Stripe secret key')
    stripe_webhook_secret: Optional[str] = Field(default=None, description=
        'Stripe webhook secret')
    secrets_vault_enabled: bool = Field(default_factory=lambda : os.getenv(
        'SECRETS_MANAGER_ENABLED', 'false').lower() == 'true', description=
        'Enable AWS Secrets Manager vault integration')
    secrets_vault_region: str = Field(default_factory=lambda : os.getenv(
        'SECRETS_MANAGER_REGION', 'us-east-1'), description=
        'AWS Secrets Manager region')
    secrets_vault_name: str = Field(default_factory=lambda : os.getenv(
        'SECRETS_MANAGER_SECRET_NAME', 'ruleiq-production-secrets'),
        description='AWS Secrets Manager secret name')
    sentry_dsn: Optional[str] = Field(default_factory=lambda :
        get_secret_or_env(SecretKeys.SENTRY_DSN if SECRETS_VAULT_AVAILABLE else
        'sentry_dsn', 'SENTRY_DSN'), description=
        'Sentry DSN for error tracking (🔐 from SecretsVault)')
    enable_sentry: bool = Field(default=True, description=
        'Enable Sentry integration')
    enable_metrics: bool = Field(default=True, description=
        'Enable metrics collection')
    enable_health_checks: bool = Field(default=True, description=
        'Enable health check endpoints')
    slow_request_threshold: float = Field(default=1.0, description=
        'Slow request warning threshold (seconds)')
    log_level: LogLevel = Field(default=LogLevel.INFO, description=
        'Application log level')
    enable_performance_monitoring: bool = Field(default=True, description=
        'Enable performance monitoring')
    traces_sample_rate: float = Field(default=0.1, description=
        'Sentry traces sample rate (0.0-1.0)')
    profiles_sample_rate: float = Field(default=0.1, description=
        'Sentry profiles sample rate (0.0-1.0)')
    disk_warning_threshold: float = Field(default=80.0, description=
        'Disk usage warning threshold (%)')
    disk_critical_threshold: float = Field(default=90.0, description=
        'Disk usage critical threshold (%)')
    memory_warning_threshold: float = Field(default=85.0, description=
        'Memory usage warning threshold (%)')
    memory_critical_threshold: float = Field(default=95.0, description=
        'Memory usage critical threshold (%)')
    enable_debug_endpoints: bool = Field(default_factory=lambda : os.getenv
        ('ENVIRONMENT', 'development') == 'development', description=
        'Enable debug endpoints (auto-disabled in production)')
    metrics_endpoint_enabled: bool = Field(default=True, description=
        'Enable Prometheus metrics endpoint')
    agentic_assessments_enabled: bool = Field(default=False, description=
        'Enable agentic assessments')
    ai_policy_generation_enabled: bool = Field(default=True, description=
        'Enable AI policy generation')
    advanced_analytics_enabled: bool = Field(default=True, description=
        'Enable advanced analytics')
    integration_sync_enabled: bool = Field(default=True, description=
        'Enable integration sync')
    audit_log_retention_days: int = Field(default=90, description=
        'Number of days to retain audit logs')
    real_time_security_alerts: bool = Field(default=True, description=
        'Enable real-time security alerts')

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) ->str:
        """Validate database URL format"""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://',
            'sqlite:///')):
            raise ValueError(
                'Database URL must start with postgresql:// or sqlite:///')
        return v

    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: str) ->str:
        """Validate Redis URL format"""
        if not v.startswith('redis://'):
            raise ValueError('Redis URL must start with redis://')
        return v

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v: str) ->str:
        """Validate JWT secret key strength"""
        if len(v) < 32:
            raise ValueError(
                'JWT secret key must be at least 32 characters long')
        return v

    @field_validator('google_api_key')
    @classmethod
    def validate_google_api_key(cls, v: str) ->str:
        """Validate Google API key format"""
        if not v.startswith('AIza'):
            logger.warning(
                "Google API key may not be in the correct format (should start with 'AIza')"
                )
        return v

    @field_validator('max_file_size_mb')
    @classmethod
    def validate_max_file_size(cls, v: int) ->int:
        """Validate file size limits"""
        if v > DEFAULT_LIMIT:
            raise ValueError('Max file size cannot exceed 100MB')
        return v

    @field_validator('bcrypt_rounds')
    @classmethod
    def validate_bcrypt_rounds(cls, v: int) ->int:
        """Validate bcrypt rounds"""
        if v < 10 or v > 16:
            raise ValueError('Bcrypt rounds must be between 10 and 16')
        return v

    def get_secrets_vault_health(self) ->Dict[str, Union[str, bool]]:
        """
        🔐 Get SecretsVault health status for monitoring

        Returns:
            Dict containing vault health information
        """
        if not SECRETS_VAULT_AVAILABLE:
            return {'status': 'unavailable', 'enabled': False, 'message':
                'SecretsVault module not available', 'vault_type': 'None'}
        try:
            from .secrets_vault import vault_health_check
            return vault_health_check()
        except Exception as e:
            logger.error('❌ SecretsVault health check failed: %s' % e)
            return {'status': 'error', 'enabled': self.
                secrets_vault_enabled, 'message':
                f'Health check failed: {str(e)}', 'vault_type':
                'AWS Secrets Manager'}

    def log_vault_status(self) ->None:
        """🔐 Log SecretsVault status at application startup"""
        health = self.get_secrets_vault_health()
        if health['status'] == 'healthy':
            logger.info(
                '✅ SecretsVault: AWS Secrets Manager connected and healthy')
        elif health['status'] == 'disabled':
            logger.info('🔐 SecretsVault: Disabled, using environment variables'
                )
        elif health['status'] == 'unavailable':
            logger.warning(
                '⚠️ SecretsVault: Module unavailable, using environment fallback'
                )
        else:
            logger.error('❌ SecretsVault: %s' % health['message'])
        logger.info('🔐 Vault Configuration: enabled=%s, region=%s' % (self.
            secrets_vault_enabled, self.secrets_vault_region))

    @property
    def is_secrets_vault_healthy(self) ->bool:
        """🔐 Quick check if SecretsVault is healthy"""
        return self.get_secrets_vault_health()['status'] == 'healthy'


_settings: Optional[Settings] = None


def get_settings() ->Settings:
    """Get application settings"""
    return _get_or_create_settings()


def reload_settings() ->Settings:
    """Reload settings from environment variables"""
    return _create_new_settings()


def _get_or_create_settings() ->Settings:
    """Get existing settings or create new ones"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.log_vault_status()
    return _settings


def _create_new_settings() ->Settings:
    """Create new settings instance"""
    global _settings
    _settings = Settings()
    return _settings
    return _settings


settings = get_settings()
