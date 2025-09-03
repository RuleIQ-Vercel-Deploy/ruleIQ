"""Test the /api/v1/auth/me endpoint to see the actual error"""
import logging

# Constants
HTTP_OK = 200

logger = logging.getLogger(__name__)
from __future__ import annotations
from typing import Any, Dict, List, Optional
import requests
import json
BASE_URL = 'http://localhost:8000'

def test_auth_me() ->Any:
    """Test the /api/v1/auth/me endpoint with different scenarios"""
    logger.info('Testing /api/v1/auth/me endpoint...')
    logger.info('=' * 60)
    logger.info('\n1. Testing without token:')
    response = requests.get(f'{BASE_URL}/api/v1/auth/me')
    logger.info('   Status: %s' % response.status_code)
    if response.status_code != HTTP_OK:
        try:
            logger.info('   Response: %s' % response.json())
        except json.JSONDecodeError:
            logger.info('   Response: %s' % response.text)
    logger.info('\n2. Testing with invalid token:')
    headers = {'Authorization': 'Bearer invalid_token'}
    response = requests.get(f'{BASE_URL}/api/v1/auth/me', headers=headers)
    logger.info('   Status: %s' % response.status_code)
    if response.status_code != HTTP_OK:
        try:
            logger.info('   Response: %s' % response.json())
        except json.JSONDecodeError:
            logger.info('   Response: %s' % response.text)
    logger.info('\n3. Testing with malformed token:')
    headers = {'Authorization': 'InvalidFormat'}
    response = requests.get(f'{BASE_URL}/api/v1/auth/me', headers=headers)
    logger.info('   Status: %s' % response.status_code)
    if response.status_code != HTTP_OK:
        try:
            logger.info('   Response: %s' % response.json())
        except json.JSONDecodeError:
            logger.info('   Response: %s' % response.text)
    logger.info('\n4. Testing with empty bearer token:')
    headers = {'Authorization': 'Bearer '}
    response = requests.get(f'{BASE_URL}/api/v1/auth/me', headers=headers)
    logger.info('   Status: %s' % response.status_code)
    if response.status_code != HTTP_OK:
        try:
            logger.info('   Response: %s' % response.json())
        except json.JSONDecodeError:
            logger.info('   Response: %s' % response.text)
    logger.info('\n' + '=' * 60)
    logger.info('Expected behavior:')
    logger.info('- Should return 401 for missing/invalid tokens')
    logger.info('- Should NOT return 500 Internal Server Error')
    logger.info('- Current issue: Returns 500 instead of proper 401')

if __name__ == '__main__':
    test_auth_me()
