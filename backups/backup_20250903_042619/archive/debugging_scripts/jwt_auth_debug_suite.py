"""
Comprehensive JWT Authentication Debug and Test Suite
import logging
logger = logging.getLogger(__name__)


This script performs the following:
1. Checks JWT library compatibility
2. Verifies environment variable loading
3. Tests token generation with both libraries
4. Tests the diagnostic endpoint
5. Runs the AI assessment endpoint tests
"""

import os
from pathlib import Path
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Test imports
logger.info("=" * 60)
logger.info("JWT AUTHENTICATION DEBUG SUITE")
logger.info("=" * 60)

# Step 1: Check JWT libraries
logger.info("\n1. Checking JWT libraries...")
jwt_libs = {}

try:
    import jwt as pyjwt

    jwt_libs["pyjwt"] = pyjwt
    logger.info("✓ PyJWT imported successfully")
except ImportError:
    logger.info("✗ PyJWT not installed")
    jwt_libs["pyjwt"] = None

try:
    from jose import jwt as jose_jwt

    jwt_libs["jose"] = jose_jwt
    logger.info("✓ python-jose imported successfully")
except ImportError:
    logger.info("✗ python-jose not installed")
    jwt_libs["jose"] = None

# Step 2: Load environment variables
logger.info("\n2. Loading environment variables...")

# Try multiple methods
env_methods = [
    (".env.local", ".env.local"),
    ("absolute path", Path(__file__).parent / ".env.local"),
    ("parent .env", Path(__file__).parent.parent / ".env"),
]

jwt_secrets = {}
for method_name, env_path in env_methods:
    if isinstance(env_path, str) and os.path.exists(env_path):
        load_dotenv(env_path)
        secret = os.getenv("JWT_SECRET")
        jwt_secrets[method_name] = secret
        logger.info(f"  {method_name}: JWT_SECRET = {secret[:10] if secret else 'None'}...")
    elif isinstance(env_path, Path) and env_path.exists():
        load_dotenv(env_path)
        secret = os.getenv("JWT_SECRET")
        jwt_secrets[method_name] = secret
        logger.info(f"  {method_name}: JWT_SECRET = {secret[:10] if secret else 'None'}...")
    else:
        logger.info(f"  {method_name}: File not found")

# Use the loaded secret or fallback
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
logger.info(f"\nUsing JWT_SECRET: {JWT_SECRET[:20]}...")

# Step 3: Test server diagnostic endpoint
logger.info("\n3. Testing server diagnostic endpoint...")
try:
    response = requests.get("http://localhost:8000/debug/config", timeout=5)
    if response.status_code == 200:
        server_config = response.json()
        logger.info("✓ Server config retrieved:")
        logger.info(f"  - JWT Secret (first 10): {server_config.get('jwt_secret_first_10')}")
        logger.info(f"  - JWT Secret length: {server_config.get('jwt_secret_length')}")
        logger.info(f"  - Working directory: {server_config.get('working_directory')}")
        logger.info(f"  - .env.local exists: {server_config.get('env_file_exists')}")
        logger.info(f"  - JWT_SECRET from env: {server_config.get('JWT_SECRET_env')}")

        # Compare secrets
        if server_config.get("jwt_secret_first_10") == JWT_SECRET[:10]:
            logger.info("✓ JWT secrets match!")
        else:
            logger.info("✗ JWT secrets DO NOT match!")
            logger.info(f"  Client: {JWT_SECRET[:10]}...")
            logger.info(f"  Server: {server_config.get('jwt_secret_first_10')}...")
    else:
        logger.info(f"✗ Failed to get server config: {response.status_code}")
except requests.exceptions.RequestException as e:
    logger.info(f"✗ Could not connect to server: {e}")
    logger.info("  Make sure the server is running: uvicorn api.main:app --reload")

# Step 4: Test token generation and verification
logger.info("\n4. Testing token generation...")

test_payload = {
    "sub": "testuser@example.com",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
}

tokens = {}
if jwt_libs["jose"]:
    try:
        token = jwt_libs["jose"].encode(test_payload, JWT_SECRET, algorithm="HS256")
        tokens["jose"] = token
        logger.info(f"✓ Token created with python-jose: {token[:50]}...")

        # Try to decode it
        decoded = jwt_libs["jose"].decode(token, JWT_SECRET, algorithms=["HS256"])
        logger.info("✓ Token verified with python-jose")
    except Exception as e:
        logger.info(f"✗ python-jose error: {e}")

# Step 5: Test AI assessment endpoints
logger.info("\n5. Testing AI assessment endpoints...")

if "jose" in tokens:
    token = tokens["jose"]
    headers = {"Authorization": f"Bearer {token}"}

    # Simple test endpoint
    test_payload = {
        "question_id": "test-q1",
        "question_text": "How should we implement access control?",
        "framework_id": "soc2",
    }

    url = "http://localhost:8000/api/v1/ai-assessments/soc2/help"
    logger.info(f"\nTesting: {url}")

    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            logger.info("✓ Authentication successful!")
            logger.info(f"Response: {response.json()}")
        elif response.status_code == 401:
            logger.info("✗ Authentication failed!")
            logger.info(f"Response: {response.text}")
        else:
            logger.info(f"? Unexpected status code: {response.status_code}")
            logger.info(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.info(f"✗ Request failed: {e}")
else:
    logger.info("✗ No token available for testing")

# Summary
logger.info("\n" + "=" * 60)
logger.info("SUMMARY")
logger.info("=" * 60)
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"python-jose available: {'Yes' if jwt_libs['jose'] else 'No'}")
logger.info(f"JWT_SECRET loaded: {'Yes' if os.getenv('JWT_SECRET') else 'No'}")
logger.info(f"JWT_SECRET value: {JWT_SECRET[:20]}...")
logger.info("\nTROUBLESHOOTING:")
if not jwt_libs["jose"]:
    logger.info("- Install python-jose: pip install python-jose[cryptography]")
if not os.getenv("JWT_SECRET"):
    logger.info("- JWT_SECRET not found in environment")
    logger.info("- Check .env.local file exists and contains JWT_SECRET")
    logger.info("- Try: export JWT_SECRET='your-secret-here'")
logger.info("\nTo run the server:")
logger.info("  uvicorn api.main:app --reload")
