#!/usr/bin/env python
"""Check available routes in the test app."""
import logging
logger = logging.getLogger(__name__)

from tests.test_app import create_test_app

app = create_test_app()

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, "path") and hasattr(route, "methods"):
        routes.append((route.path, list(route.methods)))

# Sort and print chat-related routes
logger.info("Chat-related routes:")
for path, methods in sorted(routes):
    if "/chat" in path:
        logger.info(f"  {path}: {methods}")

# Check specifically for analytics routes
logger.info("\nAnalytics routes:")
analytics_routes = [r for r in routes if "analytics" in r[0]]
for path, methods in sorted(analytics_routes):
    logger.info(f"  {path}: {methods}")
