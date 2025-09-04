"""
from __future__ import annotations
import logging

# Constants
HTTP_OK = 200

logger = logging.getLogger(__name__)

Validate Postman collection setup for RuleIQ API
"""
from typing import Any, Dict, List, Optional
import json
import os
import sys


def validate_collection(filename: str) ->Any:
    """Validate Postman collection file"""
    if not os.path.exists(filename):
        return False, f'Collection file not found: {filename}'
    try:
        with open(filename, 'r') as f:
            collection = json.load(f)
        if 'info' not in collection or 'item' not in collection:
            return False, 'Invalid collection structure'
        total_endpoints = 0
        for folder in collection.get('item', []):
            if 'item' in folder:
                total_endpoints += len(folder['item'])
        has_auth = 'auth' in collection
        return True, {'name': collection['info'].get('name', 'Unknown'),
            'folders': len(collection.get('item', [])), 'endpoints':
            total_endpoints, 'has_auth': has_auth}
    except Exception as e:
        return False, f'Error reading collection: {str(e)}'


def validate_environment(filename: str) ->Any:
    """Validate Postman environment file"""
    if not os.path.exists(filename):
        return False, f'Environment file not found: {filename}'
    try:
        with open(filename, 'r') as f:
            env = json.load(f)
        required_vars = ['base_url', 'api_version', 'test_user_email',
            'test_user_password']
        env_vars = {v['key']: v['value'] for v in env.get('values', [])}
        missing = [v for v in required_vars if v not in env_vars]
        if missing:
            return (False,
                f"Missing environment variables: {', '.join(missing)}")
        return True, {'name': env.get('name', 'Unknown'), 'variables': len(
            env_vars), 'has_credentials': env_vars.get('test_user_email') ==
            'test@ruleiq.dev'}
    except Exception as e:
        return False, f'Error reading environment: {str(e)}'


def main() ->Any:
    logger.info('RuleIQ Postman Setup Validation')
    """Main"""
    logger.info('=' * 60)
    logger.info('\n📦 Checking Consolidated Collection...')
    success, result = validate_collection(
        'ruleiq_postman_collection_consolidated.json')
    if success:
        logger.info('  ✅ Collection: %s' % result['name'])
        logger.info('  ✅ Folders: %s' % result['folders'])
        logger.info('  ✅ Endpoints: %s' % result['endpoints'])
        print(
            f"  ✅ Authentication: {'Configured' if result['has_auth'] else 'Not configured'}"
            )
    else:
        logger.info('  ❌ %s' % result)
    logger.info('\n🔧 Checking Environment...')
    success, result = validate_environment('ruleiq_postman_environment.json')
    if success:
        logger.info('  ✅ Environment: %s' % result['name'])
        logger.info('  ✅ Variables: %s' % result['variables'])
        print(
            f"  ✅ Test Credentials: {'Correct' if result['has_credentials'] else 'Incorrect'}"
            )
    else:
        logger.info('  ❌ %s' % result)
    logger.info('\n🌐 Checking Backend...')
    try:
        import requests
        response = requests.get('http://localhost:8000/api/v1/health',
            timeout=2)
        if response.status_code == HTTP_OK:
            data = response.json()
            logger.info('  ✅ Backend Status: %s' % data.get('status',
                'Unknown'))
            logger.info('  ✅ Version: %s' % data.get('version', 'Unknown'))
        else:
            logger.info('  ⚠️ Backend returned status %s' % response.
                status_code)
    except Exception as e:
        logger.info('  ❌ Backend not accessible: %s' % str(e))
    logger.info('\n🔐 Testing Authentication...')
    try:
        import requests
        login_data = {'username': 'test@ruleiq.dev', 'password':
            'TestPassword123!'}
        response = requests.post('http://localhost:8000/api/v1/auth/token',
            data=login_data, timeout=5)
        if response.status_code == HTTP_OK:
            logger.info('  ✅ Login successful')
            token = response.json().get('access_token', '')[:30] + '...'
            logger.info('  ✅ Token received: %s' % token)
        else:
            logger.info('  ❌ Login failed with status %s' % response.
                status_code)
    except Exception as e:
        logger.info('  ❌ Authentication test failed: %s' % str(e))
    logger.info('\n' + '=' * 60)
    logger.info('✨ Postman Setup Validation Complete!')
    logger.info('\nNext Steps:')
    logger.info(
        "1. Import 'ruleiq_postman_collection_consolidated.json' into Postman")
    logger.info("2. Import 'ruleiq_postman_environment.json' as environment")
    logger.info("3. Select 'RuleIQ Development' environment")
    logger.info('4. Start testing with the Authentication folder!')


if __name__ == '__main__':
    main()
