#!/usr/bin/env python3
"""
Simple JWT Test - Uses correct library (python-jose)
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Use the same JWT library as the server
from jose import jwt

# Load environment variables
env_path = Path(__file__).parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")
else:
    print(f"✗ Environment file not found: {env_path}")

# Get JWT secret
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    print("✗ JWT_SECRET not found in environment, using default")
    JWT_SECRET = "dev-jwt-secret-key-change-for-production"

print(f"→ Using JWT_SECRET: {JWT_SECRET[:10]}...")

# Create a test token
payload = {
    "sub": "testuser@example.com",
    "exp": datetime.utcnow() + timedelta(minutes=5),
    "type": "access",  # This field might be required by the server
}

try:
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    print("✓ Token created successfully")
    print(f"  Token: {token[:50]}...")
except Exception as e:
    print(f"✗ Failed to create token: {e}")
    exit(1)

# Test the endpoint
url = "http://localhost:8000/api/v1/ai-assessments/soc2/help"
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "question_id": "test-q1",
    "question_text": "How should we implement access control?",
    "framework_id": "soc2",
}

print(f"\n→ Testing endpoint: {url}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code == 200:
        print("✓ SUCCESS! Authentication worked")
        print(f"  Response: {response.json()}")
    elif response.status_code == 401:
        print("✗ FAILED! Authentication error (401)")
        print(f"  Response: {response.text}")

        # Try to get more info
        try:
            error_detail = response.json()
            print(f"  Error detail: {error_detail}")
        except:
            pass
    else:
        print(f"? Unexpected status: {response.status_code}")
        print(f"  Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to server")
    print("  Make sure the server is running: uvicorn api.main:app --reload")
except Exception as e:
    print(f"✗ Request failed: {e}")
