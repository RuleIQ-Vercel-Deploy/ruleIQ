"""
Comprehensive JWT Authentication Debug and Test Suite

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
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Test imports
print("=" * 60)
print("JWT AUTHENTICATION DEBUG SUITE")
print("=" * 60)

# Step 1: Check JWT libraries
print("\n1. Checking JWT libraries...")
jwt_libs = {}

try:
    import jwt as pyjwt

    jwt_libs["pyjwt"] = pyjwt
    print("✓ PyJWT imported successfully")
except ImportError:
    print("✗ PyJWT not installed")
    jwt_libs["pyjwt"] = None

try:
    from jose import jwt as jose_jwt

    jwt_libs["jose"] = jose_jwt
    print("✓ python-jose imported successfully")
except ImportError:
    print("✗ python-jose not installed")
    jwt_libs["jose"] = None

# Step 2: Load environment variables
print("\n2. Loading environment variables...")

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
        print(f"  {method_name}: JWT_SECRET = {secret[:10] if secret else 'None'}...")
    elif isinstance(env_path, Path) and env_path.exists():
        load_dotenv(env_path)
        secret = os.getenv("JWT_SECRET")
        jwt_secrets[method_name] = secret
        print(f"  {method_name}: JWT_SECRET = {secret[:10] if secret else 'None'}...")
    else:
        print(f"  {method_name}: File not found")

# Use the loaded secret or fallback
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
print(f"\nUsing JWT_SECRET: {JWT_SECRET[:20]}...")

# Step 3: Test server diagnostic endpoint
print("\n3. Testing server diagnostic endpoint...")
try:
    response = requests.get("http://localhost:8000/debug/config", timeout=5)
    if response.status_code == 200:
        server_config = response.json()
        print("✓ Server config retrieved:")
        print(f"  - JWT Secret (first 10): {server_config.get('jwt_secret_first_10')}")
        print(f"  - JWT Secret length: {server_config.get('jwt_secret_length')}")
        print(f"  - Working directory: {server_config.get('working_directory')}")
        print(f"  - .env.local exists: {server_config.get('env_file_exists')}")
        print(f"  - JWT_SECRET from env: {server_config.get('JWT_SECRET_env')}")

        # Compare secrets
        if server_config.get("jwt_secret_first_10") == JWT_SECRET[:10]:
            print("✓ JWT secrets match!")
        else:
            print("✗ JWT secrets DO NOT match!")
            print(f"  Client: {JWT_SECRET[:10]}...")
            print(f"  Server: {server_config.get('jwt_secret_first_10')}...")
    else:
        print(f"✗ Failed to get server config: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"✗ Could not connect to server: {e}")
    print("  Make sure the server is running: uvicorn api.main:app --reload")

# Step 4: Test token generation and verification
print("\n4. Testing token generation...")

test_payload = {
    "sub": "testuser@example.com",
    "exp": datetime.utcnow() + timedelta(minutes=5),
}

tokens = {}
if jwt_libs["jose"]:
    try:
        token = jwt_libs["jose"].encode(test_payload, JWT_SECRET, algorithm="HS256")
        tokens["jose"] = token
        print(f"✓ Token created with python-jose: {token[:50]}...")

        # Try to decode it
        decoded = jwt_libs["jose"].decode(token, JWT_SECRET, algorithms=["HS256"])
        print("✓ Token verified with python-jose")
    except Exception as e:
        print(f"✗ python-jose error: {e}")

# Step 5: Test AI assessment endpoints
print("\n5. Testing AI assessment endpoints...")

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
    print(f"\nTesting: {url}")

    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ Authentication successful!")
            print(f"Response: {response.json()}")
        elif response.status_code == 401:
            print("✗ Authentication failed!")
            print(f"Response: {response.text}")
        else:
            print(f"? Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
else:
    print("✗ No token available for testing")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Working directory: {os.getcwd()}")
print(f"python-jose available: {'Yes' if jwt_libs['jose'] else 'No'}")
print(f"JWT_SECRET loaded: {'Yes' if os.getenv('JWT_SECRET') else 'No'}")
print(f"JWT_SECRET value: {JWT_SECRET[:20]}...")
print("\nTROUBLESHOOTING:")
if not jwt_libs["jose"]:
    print("- Install python-jose: pip install python-jose[cryptography]")
if not os.getenv("JWT_SECRET"):
    print("- JWT_SECRET not found in environment")
    print("- Check .env.local file exists and contains JWT_SECRET")
    print("- Try: export JWT_SECRET='your-secret-here'")
print("\nTo run the server:")
print("  uvicorn api.main:app --reload")
