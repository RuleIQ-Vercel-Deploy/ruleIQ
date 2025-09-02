#!/usr/bin/env python3
"""Test the API response directly."""

import requests
import json


def test_api_directly():
    # Test the lead capture endpoint directly
    url = "http://localhost:8000/api/v1/freemium/leads"
    data = {
        "email": "direct_test@example.com",
        "utm_source": "test",
        "utm_campaign": "test",
        "marketing_consent": True,
    }

    print(f"Testing API endpoint: {url}")
    print(f"Payload: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response Body: {json.dumps(result, indent=2)}")

            # Check if token is present
            if "token" in result:
                print(f"\n✅ Token received: {result['token']}")
            else:
                print("\n⚠️  No token in response!")
                print(f"Available keys: {list(result.keys())}")
        else:
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_api_directly()
