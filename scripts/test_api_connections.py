"""

# Constants

Quick API connection test for backend-to-frontend connections
Tests the main endpoints that were failing in the API Debug Suite
"""
import requests
import json

from tests.test_constants import (
    HTTP_BAD_REQUEST
)
BASE_URL = 'http://localhost:8000'


def test_endpoint(method, endpoint, data=None, headers=None, description=''):
    """Test a single endpoint"""
    url = f'{BASE_URL}{endpoint}'
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers,
                timeout=10)
        status_code = response.status_code
        status_symbol = '✅' if status_code < HTTP_BAD_REQUEST else '❌'
        print(
            f'{status_symbol} {method} {endpoint} -> {status_code} {description}'
            )
        if status_code >= HTTP_BAD_REQUEST:
            try:
                error_detail = response.json().get('detail', 'No detail')
                print(f'    Error: {error_detail}')
            except (json.JSONDecodeError, requests.RequestException, ValueError
                ):
                print(f'    Error: {response.text[:100]}')
        return response.status_code < HTTP_BAD_REQUEST, response
    except (json.JSONDecodeError, requests.RequestException, ValueError) as e:
        print(f'❌ {method} {endpoint} -> ERROR: {e}')
        return False, None


def main():
    print('🚀 Testing API Connections - Backend to Frontend Integration')
    print('=' * 60)
    print('\n📡 Basic Connectivity:')
    test_endpoint('GET', '/health', description='Basic health check')
    test_endpoint('GET', '/api/v1/health', description='API health check')
    print('\n🔐 Authentication Tests:')
    register_data = {'email':
        f'test-api-connection-{int(1754520948)}@debugtest.com', 'password':
        'TestPassword123@'}
    success, response = test_endpoint('POST', '/api/v1/auth/register',
        register_data, description='User registration')
    if success and response:
        try:
            token = response.json()['tokens']['access_token']
            print('    ✅ Auth token obtained')
            auth_headers = {'Authorization': f'Bearer {token}'}
            print('\n📋 Previously Failing Endpoints (403 errors):')
            test_endpoint('GET', '/api/v1/business-profiles/', headers=
                auth_headers, description='Business profiles list')
            test_endpoint('GET', '/api/v1/assessments/', headers=
                auth_headers, description='Assessments list')
            test_endpoint('GET', '/api/v1/frameworks/', headers=
                auth_headers, description='Frameworks list')
            print('\n🤖 AI Endpoints (Previously 404 errors):')
            test_endpoint('GET', '/api/v1/ai/generate-policy', headers=
                auth_headers, description='AI policy generation')
            test_endpoint('GET', '/api/v1/ai/cost-monitoring', headers=
                auth_headers, description='AI cost monitoring')
            print('\n💬 Chat Endpoints:')
            test_endpoint('GET', '/api/v1/chat/', headers=auth_headers,
                description='Chat endpoint')
            print('\n🎯 Freemium Endpoints:')
            test_endpoint('POST', '/api/v1/freemium/capture-lead', {'email':
                'test@example.com', 'consent': True}, description=
                'Freemium lead capture')
        except (OSError, json.JSONDecodeError, ValueError) as e:
            print(f'    ❌ Could not extract token: {e}')
    print('\n' + '=' * 60)
    print('✅ API Connection Test Complete')
    print("   - Check results above to see what's working vs broken")
    print('   - ✅ = Working, ❌ = Needs attention')


if __name__ == '__main__':
    main()
