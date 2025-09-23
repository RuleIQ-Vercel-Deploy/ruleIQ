"""
Vercel-specific settings for serverless deployment.
Optimized for Vercel's serverless environment with:
- Reduced connection pools
- Disabled background tasks
- Simplified feature flags
"""

import os
from typing import Optional
from pydantic import Field, validator
from config.settings import Settings

class VercelSettings(Settings):
    """
    Settings optimized for Vercel's serverless environment.
    Inherits from base Settings but overrides values for serverless.
    """

    # Environment detection
    is_vercel: bool = Field(
        default_factory=lambda: (
            os.getenv('VERCEL', '').lower() == '1' or
            os.getenv('VERCEL_ENV') is not None
        )
    )

    # Database optimization for serverless
    database_pool_size: int = Field(default=2)  # Smaller pool for serverless
    database_max_overflow: int = Field(default=3)
    database_pool_timeout: int = Field(default=5)  # Shorter timeout
    database_pool_recycle: int = Field(default=300)  # 5 minutes
    database_echo: bool = Field(default=False)  # Disable SQL echo in production

    # Disable features incompatible with serverless
    enable_monitoring: bool = Field(default=False)
    enable_background_tasks: bool = Field(default=False)
    enable_websockets: bool = Field(default=False)
    enable_database_monitoring: bool = Field(default=False)
    enable_performance_tracking: bool = Field(default=False)

    # Redis configuration (optional in serverless)
    redis_enabled: bool = Field(
        default_factory=lambda: bool(os.getenv('REDIS_URL'))
    )
    redis_connection_timeout: int = Field(default=2)  # Shorter timeout
    redis_socket_timeout: int = Field(default=2)
    redis_max_connections: int = Field(default=5)  # Smaller pool

    # Simplified secrets management
    use_aws_secrets: bool = Field(default=False)  # Rely on Vercel env vars
    use_vault: bool = Field(default=False)  # Disable HashiCorp Vault

    # Logging optimization
    log_level: str = Field(default="INFO")
    log_to_file: bool = Field(default=False)  # No file logging in serverless
    structured_logging: bool = Field(default=True)  # JSON logs for Vercel

    # Feature flags for serverless
    enable_ai_features: bool = Field(
        default_factory=lambda: bool(
            os.getenv('GOOGLE_AI_API_KEY') or os.getenv('OPENAI_API_KEY')
        )
    )
    enable_neo4j: bool = Field(
        default_factory=lambda: bool(os.getenv('NEO4J_URI'))
    )
    enable_stripe: bool = Field(
        default_factory=lambda: bool(os.getenv('STRIPE_SECRET_KEY'))
    )
    enable_pusher: bool = Field(
        default_factory=lambda: bool(os.getenv('PUSHER_APP_ID'))
    )

    # API configuration
    api_timeout: int = Field(default=55)  # Just under Vercel's 60s limit
    max_request_size: int = Field(default=10 * 1024 * 1024)  # 10MB

    # Cache configuration (simplified for serverless)
    cache_ttl: int = Field(default=300)  # 5 minutes default cache
    enable_response_cache: bool = Field(default=True)

    # Rate limiting (simplified)
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=60)  # 1 minute

    # CORS configuration
    cors_allow_origins: list = Field(
        default_factory=lambda: os.getenv('CORS_ORIGINS', '*').split(',')
    )
    cors_allow_credentials: bool = Field(default=True)

    # Security settings
    jwt_expiry_hours: int = Field(default=24)
    secure_cookies: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator('database_url', pre=True)
    def build_database_url(cls, v, values):
        """Build database URL with Vercel-specific optimizations."""
        if v:
            # Add connection parameters for serverless
            if '?' not in v:
                v += '?'
            else:
                v += '&'

            params = [
                'sslmode=require',
                'connect_timeout=10',
                'options=-c statement_timeout=50000',  # 50 seconds
                'pool_size=2',
                'max_overflow=3'
            ]

            return v + '&'.join(params)

        return v

    @validator('redis_url', pre=True)
    def validate_redis_url(cls, v, values):
        """Validate and configure Redis URL for serverless."""
        if not v or not values.get('redis_enabled'):
            return None

        # Add connection parameters for serverless
        if '?' not in v:
            v += '?'
        else:
            v += '&'

        params = [
            'socket_timeout=2',
            'socket_connect_timeout=2',
            'socket_keepalive=True',
            'socket_keepalive_options=1,3,5'
        ]

        return v + '&'.join(params)

    def get_database_config(self) -> dict:
        """Get database configuration optimized for serverless."""
        return {
            'pool_size': self.database_pool_size,
            'max_overflow': self.database_max_overflow,
            'pool_timeout': self.database_pool_timeout,
            'pool_recycle': self.database_pool_recycle,
            'echo': self.database_echo,
            'pool_pre_ping': True,  # Important for serverless
            'connect_args': {
                'connect_timeout': 10,
                'options': '-c statement_timeout=50000'
            }
        }

    def get_redis_config(self) -> Optional[dict]:
        """Get Redis configuration if enabled."""
        if not self.redis_enabled or not self.redis_url:
            return None

        return {
            'url': self.redis_url,
            'socket_timeout': self.redis_socket_timeout,
            'socket_connect_timeout': self.redis_connection_timeout,
            'max_connections': self.redis_max_connections,
            'decode_responses': True,
            'health_check_interval': 30
        }

    def get_feature_flags(self) -> dict:
        """Get all feature flags for the application."""
        return {
            'monitoring': self.enable_monitoring,
            'background_tasks': self.enable_background_tasks,
            'websockets': self.enable_websockets,
            'ai_features': self.enable_ai_features,
            'neo4j': self.enable_neo4j,
            'stripe': self.enable_stripe,
            'pusher': self.enable_pusher,
            'redis_cache': self.redis_enabled,
            'response_cache': self.enable_response_cache,
            'rate_limiting': self.rate_limit_enabled
        }

# Singleton instance
_settings_instance: Optional[VercelSettings] = None

def get_vercel_settings() -> VercelSettings:
    """Get or create the Vercel settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = VercelSettings()
    return _settings_instance

# Export the settings instance
settings = get_vercel_settings()