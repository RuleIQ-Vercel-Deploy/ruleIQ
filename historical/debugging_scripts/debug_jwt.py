#!/usr/bin/env python3
"""
Standalone JWT test script to verify token generation and verification.
This helps isolate JWT issues from the rest of the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Test both JWT libraries
print("Testing JWT libraries...")

# Test 1: PyJWT
try:
    import jwt as pyjwt
    print("✓ PyJWT imported successfully")
except ImportError:
    print("✗ PyJWT not installed")
    pyjwt = None

# Test 2: python-jose
try:
    from jose import jwt as jose_jwt
    print("✓ python-jose imported successfully")
except ImportError:
    print("✗ python-jose not installed")
    jose_jwt = None

print("\n" + "="*50)

# Test environment loading from different paths
print("\nTesting environment variable loading...")

# Method 1: Direct .env.local
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
    jwt_secret_1 = os.getenv("JWT_SECRET")
    print(f"Method 1 (.env.local): JWT_SECRET = {jwt_secret_1[:10] if jwt_secret_1 else 'None'}...")

# Method 2: Absolute path
env_path = Path(__file__).parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    jwt_secret_2 = os.getenv("JWT_SECRET")
    print(f"Method 2 (absolute path): JWT_SECRET = {jwt_secret_2[:10] if jwt_secret_2 else 'None'}...")

# Method 3: Check if already in environment
jwt_secret_3 = os.getenv("JWT_SECRET")
print(f"Method 3 (direct env): JWT_SECRET = {jwt_secret_3[:10] if jwt_secret_3 else 'None'}...")

print("\n" + "="*50)

# Use the loaded secret or fallback
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
print(f"\nUsing JWT_SECRET: {JWT_SECRET[:20]}...")

# Test token creation and verification
print("\n" + "="*50)
print("\nTesting token creation and verification...")

test_payload = {"test": "data", "sub": "testuser@example.com"}

# Test with PyJWT
if pyjwt:
    print("\nTesting with PyJWT:")
    try:
        token = pyjwt.encode(test_payload, JWT_SECRET, algorithm="HS256")
        print(f"✓ Token created: {token[:50]}...")
        
        decoded = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"✓ Token verified: {decoded}")
    except Exception as e:
        print(f"✗ PyJWT error: {e}")

# Test with python-jose
if jose_jwt:
    print("\nTesting with python-jose:")
    try:
        token = jose_jwt.encode(test_payload, JWT_SECRET, algorithm="HS256")
        print(f"✓ Token created: {token[:50]}...")
        
        decoded = jose_jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"✓ Token verified: {decoded}")
    except Exception as e:
        print(f"✗ python-jose error: {e}")

# Cross-library test
if pyjwt and jose_jwt:
    print("\n" + "="*50)
    print("\nTesting cross-library compatibility...")
    try:
        # Create with PyJWT, verify with jose
        token_pyjwt = pyjwt.encode(test_payload, JWT_SECRET, algorithm="HS256")
        decoded_jose = jose_jwt.decode(token_pyjwt, JWT_SECRET, algorithms=["HS256"])
        print("✓ PyJWT -> python-jose: Success")
        
        # Create with jose, verify with PyJWT
        token_jose = jose_jwt.encode(test_payload, JWT_SECRET, algorithm="HS256")
        decoded_pyjwt = pyjwt.decode(token_jose, JWT_SECRET, algorithms=["HS256"])
        print("✓ python-jose -> PyJWT: Success")
    except Exception as e:
        print(f"✗ Cross-library compatibility error: {e}")

print("\n" + "="*50)
print("\nSummary:")
print(f"- Working directory: {os.getcwd()}")
print(f"- .env.local exists: {os.path.exists('.env.local')}")
print(f"- JWT_SECRET is set: {'Yes' if os.getenv('JWT_SECRET') else 'No'}")
print(f"- Both JWT libraries work: {'Yes' if pyjwt and jose_jwt else 'No'}")
