"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Simple validation script to test the authentication flow end-to-end
before running TestSprite.
"""
import requests
import sys
from typing import Optional, Any

def test_frontend_csrf() -> Optional[bool]:
    """Test CSRF token endpoint"""
    logger.info('🔐 Testing CSRF token endpoint...')
    try:
        response = requests.get('http://localhost:3000/api/csrf-token', timeout=10)
        if response.status_code == 200:
            logger.info('✅ CSRF token endpoint working')
            return True
        else:
            logger.info(f'❌ CSRF endpoint failed: {response.status_code}')
            return False
    except Exception as e:
        logger.info(f'❌ CSRF endpoint error: {e}')
        return False

def test_backend_auth() -> Optional[bool]:
    """Test backend authentication"""
    logger.info('🔐 Testing backend authentication...')
    try:
        login_data = {'username': 'test@example.com', 'password': 'testpassword123'}
        response = requests.post('http://localhost:8000/api/v1/auth/token', data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            logger.info('✅ Backend login successful')
            me_response = requests.get('http://localhost:8000/api/v1/auth/me', headers={'Authorization': f'Bearer {access_token}'}, timeout=10)
            if me_response.status_code == 200:
                user_data = me_response.json()
                logger.info(f"✅ User data retrieved: {user_data.get('email')}")
                return True
            else:
                logger.info(f'❌ /me endpoint failed: {me_response.status_code}')
                return False
        else:
            logger.info(f'❌ Backend login failed: {response.status_code}')
            logger.info(f'Response: {response.text}')
            return False
    except Exception as e:
        logger.info(f'❌ Backend auth error: {e}')
        return False

def test_page_loads() -> Any:
    """Test that key pages load"""
    logger.info('📱 Testing page loads...')
    pages = [('http://localhost:3000/', 'Home page'), ('http://localhost:3000/login', 'Login page'), ('http://localhost:3000/register', 'Register page')]
    all_passed = True
    for url, name in pages:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logger.info(f'✅ {name} loads successfully')
            else:
                logger.info(f'❌ {name} failed: {response.status_code}')
                all_passed = False
        except Exception as e:
            logger.info(f'❌ {name} error: {e}')
            all_passed = False
    return all_passed

def main() -> int:
    """Run all validation tests"""
    logger.info('🚀 Starting authentication flow validation...\n')
    results = []
    results.append(test_frontend_csrf())
    logger.info()
    results.append(test_backend_auth())
    logger.info()
    results.append(test_page_loads())
    logger.info()
    if all(results):
        logger.info('🎉 All validation tests PASSED! ✅')
        logger.info('✅ Ready for TestSprite execution')
        return 0
    else:
        logger.info('❌ Some validation tests FAILED!')
        logger.info('🔧 Please fix issues before running TestSprite')
        return 1
if __name__ == '__main__':
    sys.exit(main())