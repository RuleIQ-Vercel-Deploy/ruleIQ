#!/usr/bin/env python3
"""
Create a test user for TestSprite testing
"""
import requests
from typing import Optional

def create_test_user() -> Optional[bool]:
    """Create test user via API"""
    url = "http://localhost:8000/api/v1/auth/register"

    payload = {
        "email": "testuser@testsprite.com",
        "password": "TestSprite123@",
        "full_name": "TestSprite User"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            data = response.json()
            print("✅ Test user created successfully!")
            print(f"📧 Email: {payload['email']}")
            print(f"🔑 Password: {payload['password']}")
            print(f"🎫 Access Token: {data['tokens']['access_token'][:50]}...")
            return True
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

if __name__ == "__main__":
    create_test_user()
