#!/usr/bin/env python3
"""
Test script for freemium API endpoints
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1/freemium"

def test_freemium_flow() -> bool:
    """Test the complete freemium assessment flow"""

    # Step 1: Capture lead
    print("1. Testing lead capture...")
    lead_data = {
        "email": "test4@example.com",
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test Company",
        "marketing_consent": True,
        "newsletter_subscribed": True,
        "utm_source": "landing_page"
    }

    try:
        response = requests.post(f"{BASE_URL}/leads", json=lead_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code != 201:
            print("❌ Lead capture failed")
            return False

        lead_result = response.json()
        print(f"✅ Lead captured: {lead_result['lead_id']}")

    except Exception as e:
        print(f"❌ Lead capture error: {e}")
        return False

    # Step 2: Start assessment session
    print("\n2. Testing session start...")
    session_data = {
        "lead_email": "test4@example.com",
        "business_type": "technology",
        "assessment_type": "general"
    }

    try:
        response = requests.post(f"{BASE_URL}/sessions", json=session_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code != 201:
            print("❌ Session start failed")
            return False

        session_result = response.json()
        session_token = session_result['session_token']
        print(f"✅ Session started: {session_token}")

    except Exception as e:
        print(f"❌ Session start error: {e}")
        return False

    # Step 3: Get session progress
    print("\n3. Testing session progress...")
    try:
        response = requests.get(f"{BASE_URL}/sessions/{session_token}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code != 200:
            print("❌ Session progress failed")
            return False

        print("✅ Session progress retrieved")

    except Exception as e:
        print(f"❌ Session progress error: {e}")
        return False

    print("\n🎉 Freemium API flow test completed successfully!")
    return True

if __name__ == "__main__":
    print("Testing Freemium API Flow...")
    print("=" * 50)

    success = test_freemium_flow()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
