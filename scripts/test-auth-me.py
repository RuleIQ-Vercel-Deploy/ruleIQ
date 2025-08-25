#!/usr/bin/env python3
"""Test the /api/v1/auth/me endpoint to see the actual error"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_me():
    """Test the /api/v1/auth/me endpoint with different scenarios"""
    
    print("Testing /api/v1/auth/me endpoint...")
    print("=" * 60)
    
    # Test 1: No token
    print("\n1. Testing without token:")
    response = requests.get(f"{BASE_URL}/api/v1/auth/me")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"   Response: {response.json()}")
        except:
            print(f"   Response: {response.text}")
    
    # Test 2: Invalid token
    print("\n2. Testing with invalid token:")
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"   Response: {response.json()}")
        except:
            print(f"   Response: {response.text}")
    
    # Test 3: Malformed token
    print("\n3. Testing with malformed token:")
    headers = {"Authorization": "InvalidFormat"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"   Response: {response.json()}")
        except:
            print(f"   Response: {response.text}")
    
    # Test 4: Empty bearer token
    print("\n4. Testing with empty bearer token:")
    headers = {"Authorization": "Bearer "}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        try:
            print(f"   Response: {response.json()}")
        except:
            print(f"   Response: {response.text}")
    
    print("\n" + "=" * 60)
    print("Expected behavior:")
    print("- Should return 401 for missing/invalid tokens")
    print("- Should NOT return 500 Internal Server Error")
    print("- Current issue: Returns 500 instead of proper 401")

if __name__ == "__main__":
    test_auth_me()