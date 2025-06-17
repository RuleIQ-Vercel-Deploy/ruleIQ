"""
Logging Configuration for ComplianceGPT

This module sets up comprehensive logging with different handlers,
formatters, and configurations for different environments.
"""

import logging
import logging.config
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import settings


def setup_logging() -> None:
    """Setup logging configuration based on environment settings"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Try to load YAML configuration first
    yaml_config_path = Path("config/log_config.yaml")
    
    if yaml_config_path.exists():
        try:
            with open(yaml_config_path, 'r') as f:
                logging_config = yaml.safe_load(f)
            
            # Apply configuration
            logging.config.dictConfig(logging_config)
            
            # Log startup message
            logger = logging.getLogger(__name__)
            logger.info(f"Logging initialized from YAML - Environment: {settings.env.value}")
            logger.info(f"Log level: {settings.log_level.value}")
            return
            
        except Exception as e:
            print(f"Failed to load YAML logging config: {e}")
            print("Falling back to programmatic configuration")
    
    # Fallback to programmatic configuration
    # Generate log filename with timestamp
    log_filename = f"compliancegpt_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = logs_dir / log_filename

    # Define logging configuration
    logging_config = get_logging_config(str(log_filepath))

    # Apply configuration
    logging.config.dictConfig(logging_config)

    # Set root logger level
    logging.getLogger().setLevel(settings.log_level.value)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized (fallback) - Environment: {settings.env.value}")
    logger.info(f"Log level: {settings.log_level.value}")


def get_logging_config(log_filepath: str) -> Dict[str, Any]:
    """Get logging configuration dictionary"""

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(funcName)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': log_filepath,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': str(Path(log_filepath).parent / f"error_{Path(log_filepath).name}"),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': settings.log_level.value,
                'propagate': False
            },
            'uvicorn': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            },
            'uvicorn.error': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False
            },
            'uvicorn.access': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': False
            },
            'sqlalchemy': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False
            },
            'sqlalchemy.engine': {
                'handlers': ['file'],
                'level': 'INFO' if settings.database_echo else 'WARNING',
                'propagate': False
            }
        }
    }

    # Adjust configuration for production
    if settings.is_production:
        # Use JSON formatting for production logs
        config['handlers']['file']['formatter'] = 'json'
        config['handlers']['error_file']['formatter'] = 'json'

        # Reduce console logging in production
        config['handlers']['console']['level'] = 'WARNING'

    # Adjust configuration for development
    if settings.is_development:
        # More verbose logging for development
        config['handlers']['console']['formatter'] = 'detailed'
        config['handlers']['console']['level'] = 'DEBUG'

    return config


class ComplianceLogger:
    """Custom logger class with convenience methods for compliance-specific logging"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_user_action(self, user_id: str, action: str, details: Optional[Dict[str, Any]] = None):
        """Log user actions for audit purposes"""
        message = f"User {user_id} performed action: {action}"
        if details:
            message += f" | Details: {details}"
        self.logger.info(message, extra={
            'user_id': user_id,
            'action': action,
            'details': details,
            'event_type': 'user_action'
        })

    def log_compliance_event(self, event_type: str, framework: str, details: Optional[Dict[str, Any]] = None):
        """Log compliance-related events"""
        message = f"Compliance event: {event_type} for framework {framework}"
        if details:
            message += f" | Details: {details}"
        self.logger.info(message, extra={
            'event_type': 'compliance_event',
            'compliance_framework': framework,
            'compliance_event_type': event_type,
            'details': details
        })

    def log_ai_interaction(self, model: str, prompt_type: str, tokens_used: Optional[int] = None):
        """Log AI model interactions"""
        message = f"AI interaction: {model} for {prompt_type}"
        if tokens_used:
            message += f" | Tokens used: {tokens_used}"
        self.logger.info(message, extra={
            'event_type': 'ai_interaction',
            'ai_model': model,
            'prompt_type': prompt_type,
            'tokens_used': tokens_used
        })

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log errors with additional context"""
        message = f"Error occurred: {error!s}"
        if context:
            message += f" | Context: {context}"
        self.logger.error(message, extra={
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }, exc_info=True)


def get_logger(name: str) -> ComplianceLogger:
    """Get a ComplianceLogger instance"""
    return ComplianceLogger(name)
