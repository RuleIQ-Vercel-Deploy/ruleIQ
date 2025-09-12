"""

# Constants

Test Phase 1 Stack Auth endpoints
Quick integration test to verify authentication is working
"""
import requests
import json
import sys

from tests.test_constants import (
    HTTP_OK,
    HTTP_UNAUTHORIZED
)
BASE_URL = 'http://localhost:8000'


def test_endpoint(endpoint, description, should_fail=True):
    """Test an endpoint and return result"""
    print(f'\n🧪 Testing {description}')
    print('-' * 50)
    try:
        response = requests.get(f'{BASE_URL}{endpoint}', timeout=5)
        print(f'Without auth: {response.status_code}')
        if should_fail and response.status_code == HTTP_UNAUTHORIZED:
            print('✅ Correctly returns 401 without auth')
            return True
        elif should_fail and response.status_code != HTTP_UNAUTHORIZED:
            print(f'❌ Expected 401, got {response.status_code}')
            try:
                print(f'Response: {response.text[:200]}')
            except (ValueError, KeyError, IndexError):
                pass
            return False
        elif not should_fail and response.status_code == HTTP_OK:
            print('✅ Endpoint accessible')
            return True
        else:
            print(f'❌ Unexpected status: {response.status_code}')
            return False
    except requests.exceptions.ConnectionError:
        print('❌ Connection failed - is server running?')
        return False
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f'❌ Error: {e}')
        return False


def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f'{BASE_URL}/docs', timeout=5)
        return response.status_code == HTTP_OK
    except requests.RequestException:
        return False


def main():
    print('🚀 Phase 1 Stack Auth Endpoint Test')
    print('=' * 60)
    if not check_server():
        print('❌ Server not running on http://localhost:8000')
        print('Start with: source .venv/bin/activate && python main.py')
        return 1
    print('✅ Server is running')
    endpoints_to_test = [('/api/users/me', 'Get current user'), (
        '/api/users/profile', 'Get user profile'), ('/api/users/dashboard',
        'Get user dashboard'), ('/api/business-profiles/',
        'Get business profile')]
    results = []
    for endpoint, description in endpoints_to_test:
        result = test_endpoint(endpoint, description)
        results.append((endpoint, result))
    print('\n' + '=' * 60)
    print('📊 Test Summary')
    print('=' * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for endpoint, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{endpoint:30} {status}')
    print(f'\nResults: {passed}/{total} passed')
    if passed == total:
        print('\n✅ All Phase 1 endpoints properly protected!')
        return 0
    else:
        print(f'\n❌ {total - passed} endpoints failed authentication test')
        return 1


if __name__ == '__main__':
    sys.exit(main())
