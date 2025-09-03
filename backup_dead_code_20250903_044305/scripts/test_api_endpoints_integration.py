"""
from __future__ import annotations

# Constants
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_OK = 200


Test script to verify business-profiles and frameworks endpoints are working properly
Specifically testing the endpoints that are failing in the frontend
"""
from typing import Any, Dict, List, Optional
import requests
import json
import sys
from datetime import datetime
BASE_URL = 'http://localhost:8000'


def test_login() ->Any:
    """Login and get auth token"""
    print('🔐 Testing Login...')
    login_data = {'email': 'test@ruleiq.dev', 'password': 'TestPassword123!'}
    response = requests.post(f'{BASE_URL}/api/v1/auth/login', json=
        login_data, timeout=10)
    if response.status_code == HTTP_OK:
        token = response.json().get('access_token')
        print('✅ Login successful - Token obtained')
        return token
    else:
        print(f'❌ Login failed: {response.status_code} - {response.text}')
        print('\n🔐 Attempting to register new test user...')
        register_data = {'email':
            f'test-{datetime.now().timestamp()}@ruleiq.dev', 'password':
            'TestPassword123!'}
        response = requests.post(f'{BASE_URL}/api/v1/auth/register', json=
            register_data, timeout=10)
        if response.status_code == HTTP_OK:
            tokens = response.json().get('tokens', {})
            token = tokens.get('access_token')
            print('✅ Registration successful - Token obtained')
            return token
        else:
            print(
                f'❌ Registration failed: {response.status_code} - {response.text}'
                )
            return None


def test_business_profiles(token: str) ->Any:
    """Test business profiles endpoints"""
    print('\n📋 Testing Business Profiles Endpoints...')
    headers = {'Authorization': f'Bearer {token}'}
    print('\n1. GET /api/v1/business-profiles/')
    response = requests.get(f'{BASE_URL}/api/v1/business-profiles/',
        headers=headers, timeout=10)
    if response.status_code == HTTP_OK:
        print(
            f'✅ Business profiles endpoint working - Status: {response.status_code}'
            )
        data = response.json()
        print(f'   Response: {json.dumps(data, indent=2)[:500]}')
    elif response.status_code == HTTP_NOT_FOUND:
        print(
            f'⚠️  Business profile not found (expected for new user) - Status: {response.status_code}'
            )
        print('   This is normal - user needs to create a profile first')
    else:
        print(
            f'❌ Business profiles endpoint failed - Status: {response.status_code}'
            )
        print(f'   Error: {response.text[:500]}')
    print('\n2. POST /api/v1/business-profiles/ (Creating profile)')
    profile_data = {'company_name': 'Test Company', 'industry':
        'Technology', 'employee_count': 10, 'handles_personal_data': True,
        'processes_payments': False, 'stores_health_data': False,
        'provides_financial_services': False,
        'operates_critical_infrastructure': False,
        'has_international_operations': False}
    response = requests.post(f'{BASE_URL}/api/v1/business-profiles/', json=
        profile_data, headers=headers, timeout=10)
    if response.status_code in [200, 201]:
        print(
            f'✅ Business profile created successfully - Status: {response.status_code}'
            )
        profile_id = response.json().get('id')
        print(f'   Profile ID: {profile_id}')
        print('\n3. GET /api/v1/business-profiles/ (After creation)')
        response = requests.get(f'{BASE_URL}/api/v1/business-profiles/',
            headers=headers, timeout=10)
        if response.status_code == HTTP_OK:
            print(
                f'✅ Can now retrieve profile - Status: {response.status_code}')
    elif response.status_code == HTTP_BAD_REQUEST:
        print(
            f'⚠️  Profile might already exist - Status: {response.status_code}'
            )
        print(f'   Message: {response.text[:200]}')
    else:
        print(f'❌ Failed to create profile - Status: {response.status_code}')
        print(f'   Error: {response.text[:500]}')


def test_frameworks(token: str) ->Any:
    """Test frameworks endpoints"""
    print('\n🎯 Testing Frameworks Endpoints...')
    headers = {'Authorization': f'Bearer {token}'}
    print('\n1. GET /api/v1/frameworks/')
    response = requests.get(f'{BASE_URL}/api/v1/frameworks/', headers=
        headers, timeout=10)
    if response.status_code == HTTP_OK:
        print(f'✅ Frameworks endpoint working - Status: {response.status_code}'
            )
        data = response.json()
        print(f'   Found {len(data)} frameworks')
        if data:
            print(f"   First framework: {data[0].get('name', 'Unknown')}")
    else:
        print(f'❌ Frameworks endpoint failed - Status: {response.status_code}')
        print(f'   Error: {response.text[:500]}')
    print('\n2. GET /api/v1/frameworks/all-public')
    response = requests.get(f'{BASE_URL}/api/v1/frameworks/all-public',
        headers=headers, timeout=10)
    if response.status_code == HTTP_OK:
        print(
            f'✅ Public frameworks endpoint working - Status: {response.status_code}'
            )
        data = response.json()
        print(f'   Found {len(data)} public frameworks')
    elif response.status_code == HTTP_NOT_FOUND:
        print(
            f'⚠️  Public endpoint might not exist - Status: {response.status_code}'
            )
    else:
        print(
            f'❌ Public frameworks endpoint failed - Status: {response.status_code}'
            )
        print(f'   Error: {response.text[:200]}')


def test_compliance_wizard_requirements(token: str) ->Any:
    """Test specific endpoints needed by compliance wizard"""
    print('\n🧙 Testing Compliance Wizard Requirements...')
    headers = {'Authorization': f'Bearer {token}'}
    print('\n1. Testing complete flow for compliance wizard:')
    response = requests.get(f'{BASE_URL}/api/v1/business-profiles/',
        headers=headers, timeout=10)
    has_profile = response.status_code == HTTP_OK
    if has_profile:
        print(
            '✅ User has business profile - can proceed with framework recommendations'
            )
        print('\n2. GET /api/v1/frameworks/recommendations')
        response = requests.get(f'{BASE_URL}/api/v1/frameworks/recommendations'
            , headers=headers, timeout=10)
        if response.status_code == HTTP_OK:
            print(
                f'✅ Framework recommendations working - Status: {response.status_code}'
                )
            data = response.json()
            print(f'   Recommendations: {json.dumps(data, indent=2)[:300]}')
        elif response.status_code == HTTP_NOT_FOUND:
            print(
                f'⚠️  Recommendations endpoint might not be implemented - Status: {response.status_code}'
                )
        else:
            print(f'❌ Recommendations failed - Status: {response.status_code}')
            print(f'   Error: {response.text[:200]}')
    else:
        print(
            '⚠️  No business profile - compliance wizard would show profile creation form first'
            )


def main() ->Any:
    print('🚀 Testing Fixed API Routes for Business Profiles and Frameworks')
    print('=' * 70)
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code != HTTP_OK:
            print(
                '❌ Server health check failed. Make sure the backend is running:'
                )
            print('   python main.py')
            sys.exit(1)
        print('✅ Server is running')
    except (requests.RequestException, ValueError):
        print(f'❌ Cannot connect to server at {BASE_URL}')
        print('   Make sure the backend is running: python main.py')
        sys.exit(1)
    token = test_login()
    if not token:
        print('\n❌ Cannot proceed without authentication')
        sys.exit(1)
    test_business_profiles(token)
    test_frameworks(token)
    test_compliance_wizard_requirements(token)
    print('\n' + '=' * 70)
    print('📊 Test Summary:')
    print("   - Check the results above to see what's working")
    print('   - ✅ = Working correctly')
    print('   - ⚠️  = Working but needs attention')
    print('   - ❌ = Not working, needs fixing')
    print('\n💡 Next Steps:')
    print("   1. If business-profiles returns 404, that's normal for new users"
        )
    print(
        '   2. If frameworks returns empty list, check if frameworks are loaded in DB'
        )
    print('   3. Check frontend is using correct API paths (/api/v1/...)')
    print(
        '   4. Ensure frontend is sending Authorization header with Bearer token'
        )


if __name__ == '__main__':
    main()
