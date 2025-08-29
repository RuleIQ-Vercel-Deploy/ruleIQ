"""
Configuration Module
Loads the appropriate configuration based on environment
"""

import os
from typing import Optional
from config.base import BaseConfig, Environment
from config.development import DevelopmentConfig
from config.production import ProductionConfig
from config.testing import TestingConfig


class ConfigurationError(Exception):
    """Configuration error"""
    pass


def get_config(environment: Optional[str] = None) -> BaseConfig:
    """
    Get configuration based on environment
    
    Args:
        environment: Environment name (development, staging, production, testing)
                    If not provided, reads from ENVIRONMENT env var
    
    Returns:
        Configuration object
    
    Raises:
        ConfigurationError: If environment is invalid
    """
    # Get environment from parameter or env var
    env = environment or os.getenv("ENVIRONMENT", "development")
    env = env.lower()
    
    # Map environment to configuration class
    config_map = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "staging": ProductionConfig,  # Use production config for staging
        "production": ProductionConfig,
        "prod": ProductionConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
    }
    
    # Get configuration class
    config_class = config_map.get(env)
    if not config_class:
        raise ConfigurationError(
            f"Invalid environment: {env}. "
            f"Must be one of: {', '.join(config_map.keys())}"
        )
    
    try:
        # Create configuration instance
        config = config_class()
        
        # Log configuration loading
        print(f"Loaded configuration for environment: {config.ENVIRONMENT}")
        
        return config
    
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {str(e)}")


def validate_config(config: BaseConfig) -> bool:
    """
    Validate configuration
    
    Args:
        config: Configuration object to validate
    
    Returns:
        True if valid
    
    Raises:
        ConfigurationError: If configuration is invalid
    """
    errors = []
    
    # Check required fields
    required_fields = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
    ]
    
    for field in required_fields:
        if not getattr(config, field, None):
            errors.append(f"Missing required field: {field}")
    
    # Check for development secrets in production
    if config.is_production():
        if "dev-" in config.SECRET_KEY or "test-" in config.SECRET_KEY:
            errors.append("Production SECRET_KEY contains development/test values")
        
        if "dev-" in config.JWT_SECRET_KEY or "test-" in config.JWT_SECRET_KEY:
            errors.append("Production JWT_SECRET_KEY contains development/test values")
        
        if "localhost" in config.DATABASE_URL or "127.0.0.1" in config.DATABASE_URL:
            errors.append("Production DATABASE_URL contains localhost")
    
    # Check AI configuration if AI is enabled
    if config.ENABLE_AI_PROCESSING:
        ai_keys = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("GOOGLE_API_KEY", "Google"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
        ]
        
        # At least one AI service should be configured
        has_ai_service = any(getattr(config, key, None) for key, _ in ai_keys)
        if not has_ai_service:
            errors.append("AI processing enabled but no AI service keys configured")
    
    # Check file upload directory
    if not config.UPLOAD_DIR.exists() and not config.is_testing():
        try:
            config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create upload directory: {e}")
    
    # Raise error if validation failed
    if errors:
        raise ConfigurationError("Configuration validation failed:\n" + "\n".join(errors))
    
    return True


# Create a singleton configuration instance
_config: Optional[BaseConfig] = None


def get_current_config() -> BaseConfig:
    """
    Get current configuration (singleton)
    
    Returns:
        Current configuration object
    """
    global _config
    
    if _config is None:
        _config = get_config()
        validate_config(_config)
    
    return _config


def reload_config(environment: Optional[str] = None) -> BaseConfig:
    """
    Reload configuration with optional environment override
    
    Args:
        environment: Optional environment to load
    
    Returns:
        New configuration object
    """
    global _config
    
    _config = get_config(environment)
    validate_config(_config)
    
    return _config


# Export commonly used items
__all__ = [
    "BaseConfig",
    "DevelopmentConfig",
    "ProductionConfig",
    "TestingConfig",
    "Environment",
    "get_config",
    "get_current_config",
    "reload_config",
    "validate_config",
    "ConfigurationError",
]