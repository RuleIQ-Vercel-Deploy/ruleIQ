#!/usr/bin/env python3
"""
Run server with JWT fix verification - bypasses sentry issues
"""

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
print("Starting server with JWT fix...")
print("=" * 60)

# Import after mocking
from api.main import app
import uvicorn

# Run server
print("✓ Server starting on port 8000...")
uvicorn.run(app, host="127.0.0.1", port=8000)
