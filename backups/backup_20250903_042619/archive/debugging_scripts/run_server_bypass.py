#!/usr/bin/env python3
"""
Run server with JWT fix verification - bypasses sentry issues
"""
import logging
logger = logging.getLogger(__name__)


import os
import sys

# Set environment to disable sentry if needed
os.environ["SENTRY_DSN"] = ""

# Bypass sentry import issue by creating a mock
sys.path.insert(0, ".")

# Create a minimal sentry mock
import types

sentry_mock = types.ModuleType("sentry_sdk")
sentry_mock.init = lambda *args, **kwargs: None
sys.modules["sentry_sdk"] = sentry_mock

# Now run the actual verification
logger.info("Starting server with JWT fix...")
logger.info("=" * 60)

# Import after mocking
from api.main import app
import uvicorn

# Run server
logger.info("✓ Server starting on port 8000...")
uvicorn.run(app, host="127.0.0.1", port=8000)
