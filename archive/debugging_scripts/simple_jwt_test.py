#!/usr/bin/env python3
"""
Simple JWT Test - Uses correct library (python-jose)
"""
import logging
import json
logger = logging.getLogger(__name__)


import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import requests

# Use the same JWT library as the server
from jose import jwt
import sys

# Load environment variables
env_path = Path(__file__).parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"✓ Loaded environment from: {env_path}")
else:
    logger.info(f"✗ Environment file not found: {env_path}")

# Get JWT secret
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    logger.info("✗ JWT_SECRET not found in environment, using default")
    JWT_SECRET = "dev-jwt-secret-key-change-for-production"

logger.info(f"→ Using JWT_SECRET: {JWT_SECRET[:10]}...")

# Create a test token
payload = {
    "sub": "testuser@example.com",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    "type": "access",  # This field might be required by the server
}

try:
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    logger.info("✓ Token created successfully")
    logger.info(f"  Token: {token[:50]}...")
except (KeyError, IndexError) as e:
    logger.info(f"✗ Failed to create token: {e}")
    sys.exit(1)

# Test the endpoint
url = "http://localhost:8000/api/v1/ai-assessments/soc2/help"
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "question_id": "test-q1",
    "question_text": "How should we implement access control?",
    "framework_id": "soc2",
}

logger.info(f"\n→ Testing endpoint: {url}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code == 200:
        logger.info("✓ SUCCESS! Authentication worked")
        logger.info(f"  Response: {response.json()}")
    elif response.status_code == 401:
        logger.info("✗ FAILED! Authentication error (401)")
        logger.info(f"  Response: {response.text}")

        # Try to get more info
        try:
            error_detail = response.json()
            logger.info(f"  Error detail: {error_detail}")
        except json.JSONDecodeError:
            pass
    else:
        logger.info(f"? Unexpected status: {response.status_code}")
        logger.info(f"  Response: {response.text}")

except requests.exceptions.ConnectionError:
    logger.info("✗ Cannot connect to server")
    logger.info("  Make sure the server is running: uvicorn api.main:app --reload")
except (json.JSONDecodeError, requests.RequestException) as e:
    logger.info(f"✗ Request failed: {e}")
