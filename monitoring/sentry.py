"""
from __future__ import annotations

Sentry Integration for Proactive Monitoring

This module initializes the Sentry SDK to capture errors and performance data.
"""

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from config.settings import settings

logger = logging.getLogger(__name__)

def init_sentry() -> None:
    """Initialize the Sentry SDK."""
    if not settings.sentry_dsn:
        logger.warning("SENTRY_DSN not found, Sentry monitoring is disabled.")
        return

    try:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            integrations=[sentry_logging],
            traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
            profiles_sample_rate=1.0,  # Capture 100% of profiles for performance monitoring
        )
        logger.info(
            f"Sentry initialized for environment: {settings.sentry_environment}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}", exc_info=True)
