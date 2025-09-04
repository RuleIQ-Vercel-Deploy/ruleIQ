"""Test the API response directly."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import requests
import json

# Constants
HTTP_OK = 200

def test_api_directly() ->Any:
    url = 'http://localhost:8000/api/v1/freemium/leads'
    """Test Api Directly"""
    data = {'email': 'direct_test@example.com', 'utm_source': 'test',
        'utm_campaign': 'test', 'marketing_consent': True}
    print(f'Testing API endpoint: {url}')
    print(f'Payload: {json.dumps(data, indent=2)}')
    try:
        response = requests.post(url, json=data)
        print(f'\nStatus Code: {response.status_code}')
        print(f'Response Headers: {dict(response.headers)}')
        if response.status_code == HTTP_OK:
            result = response.json()
            print(f'Response Body: {json.dumps(result, indent=2)}')
            if 'token' in result:
                print(f"\n✅ Token received: {result['token']}")
            else:
                print('\n⚠️  No token in response!')
                print(f'Available keys: {list(result.keys())}')
        else:
            print(f'Error Response: {response.text}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_api_directly()
