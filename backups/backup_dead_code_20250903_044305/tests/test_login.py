"""

# Constants
HTTP_OK = 200

Test login with created user
"""
import requests
import json


def test_login():
    """Test login with created user"""
    url = 'http://localhost:8000/api/v1/auth/login'
    payload = {'email': 'testuser@testsprite.com', 'password': 'TestSprite123@'
        }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == HTTP_OK:
            data = response.json()
            print('✅ Login successful!')
            print(f"🎫 Access Token: {data['access_token'][:50]}...")
            print(f"🔄 Refresh Token: {data['refresh_token'][:50]}...")
            return data
        else:
            print(f'❌ Login failed: {response.status_code}')
            print(f'Error: {response.text}')
            return None
    except Exception as e:
        print(f'❌ Error during login: {e}')
        return None


if __name__ == '__main__':
    test_login()
