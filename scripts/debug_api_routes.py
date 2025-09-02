"""
from __future__ import annotations
import logging

# Constants
HTTP_BAD_REQUEST = 400

MAX_RETRIES = 3

logger = logging.getLogger(__name__)

Debug API routes to identify exact issues
"""
from typing import Any, Dict, List, Optional, Tuple
import requests
import json
import time
BASE_URL = 'http://localhost:8000'


def test_endpoint_with_details(method, endpoint, data=None, headers=None,
    description='') ->Tuple[Any, ...]:
    """Test endpoint and provide detailed info"""
    url = f'{BASE_URL}{endpoint}'
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers,
                timeout=10)
        status_code = response.status_code
        status_symbol = '✅' if status_code < HTTP_BAD_REQUEST else '❌'
        logger.info('\n%s %s %s' % (status_symbol, method, endpoint))
        logger.info('    Status: %s' % status_code)
        logger.info('    Description: %s' % description)
        if status_code >= HTTP_BAD_REQUEST:
            logger.info('    Error Response:')
            try:
                error_json = response.json()
                logger.info('      %s' % json.dumps(error_json, indent=6))
            except json.JSONDecodeError:
                logger.info('      Raw: %s' % response.text[:200])
        else:
            logger.info('    Success Response Preview:')
            try:
                success_json = response.json()
                if isinstance(success_json, dict):
                    for key, value in list(success_json.items())[:3]:
                        logger.info('      %s: %s' % (key, value))
                    if len(success_json) > MAX_RETRIES:
                        logger.info('      ... (%s total keys)' % len(
                            success_json))
                else:
                    logger.info('      %s' % str(success_json)[:100])
            except (json.JSONDecodeError, KeyError, IndexError):
                logger.info('      Raw: %s' % response.text[:100])
        return status_code < HTTP_BAD_REQUEST, response
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.info('\n❌ %s %s' % (method, endpoint))
        logger.info('    ERROR: %s' % e)
        return False, None


def main() ->Any:
    logger.info('🔍 Debugging API Routes - Detailed Analysis')
    logger.info('=' * 60)
    logger.info('\n🏥 Health Check Analysis:')
    test_endpoint_with_details('GET', '/health', description=
        'Basic health (should work)')
    test_endpoint_with_details('GET', '/api/v1/health', description=
        'API v1 health (previously failing)')
    test_endpoint_with_details('GET', '/api/v1/health/detailed',
        description='Detailed health')
    logger.info('\n🔐 Authentication Endpoint Analysis:')
    register_data = {'email': f'api-debug-{int(time.time())}@test.com',
        'password': 'TestPassword123!'}
    success, response = test_endpoint_with_details('POST',
        '/api/v1/auth/register', register_data, description=
        'New user registration')
    if not success:
        login_data = {'email':
            'test-api-connection-1754520948@debugtest.com', 'password':
            'TestPassword123@'}
        success, response = test_endpoint_with_details('POST',
            '/api/v1/auth/login', login_data, description='Existing user login'
            )
    if success and response:
        try:
            token_data = response.json()
            token = None
            if 'tokens' in token_data and 'access_token' in token_data['tokens'
                ]:
                token = token_data['tokens']['access_token']
                logger.info("    ✅ Token found in 'tokens.access_token' format"
                    )
            elif 'access_token' in token_data:
                token = token_data['access_token']
                logger.info("    ✅ Token found in 'access_token' format")
            else:
                logger.info('    ❌ No token found in response')
            if token:
                auth_headers = {'Authorization': f'Bearer {token}'}
                print(
                    '\n📋 Business Endpoints Analysis (403 errors expected if RBAC not fixed):'
                    )
                test_endpoint_with_details('GET',
                    '/api/v1/business-profiles/', headers=auth_headers,
                    description='Business profiles')
                test_endpoint_with_details('GET', '/api/v1/assessments/',
                    headers=auth_headers, description='Assessments')
                test_endpoint_with_details('GET', '/api/v1/frameworks/',
                    headers=auth_headers, description='Frameworks')
                print(
                    '\n🤖 AI Endpoints Analysis (404 errors expected if router issues remain):'
                    )
                test_endpoint_with_details('GET', '/api/v1/ai/policies',
                    headers=auth_headers, description='AI policies')
                test_endpoint_with_details('GET', '/api/v1/ai/cost',
                    headers=auth_headers, description='AI cost monitoring')
                logger.info('\n💬 Chat & Freemium Analysis:')
                test_endpoint_with_details('GET', '/api/v1/chat/', headers=
                    auth_headers, description='Chat endpoint')
                test_endpoint_with_details('POST',
                    '/api/v1/freemium/capture-lead', {'email':
                    'test@example.com', 'consent': True}, description=
                    'Freemium endpoint')
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logger.info('    ❌ Could not process auth response: %s' % e)
    logger.info('\n' + '=' * 60)
    logger.info('🔍 Debug Analysis Complete')


if __name__ == '__main__':
    main()
