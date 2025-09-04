"""
from __future__ import annotations

# Constants
HTTP_BAD_REQUEST = 400
HTTP_CREATED = 201
HTTP_OK = 200


Authenticated API Test Script
Tests ruleIQ API endpoints with proper authentication.
"""
import asyncio
import aiohttp
from typing import Dict, Optional


class APITester:

    """Class for APITester"""
    def __init__(self, base_url: str='http://localhost:8000'):
        self.base_url = base_url
        self.session = None
        self.auth_token = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def register_test_user(self) ->bool:
        """Register a test user for authentication."""
        try:
            register_data = {'email': 'test@example.com', 'password':
                'TestPassword123!', 'first_name': 'Test', 'last_name':
                'User', 'company_name': 'Test Company'}
            async with self.session.post(
                f'{self.base_url}/api/v1/auth/register', json=register_data
                ) as response:
                if response.status == HTTP_CREATED:
                    print('✅ Test user registered successfully')
                    return True
                elif response.status == HTTP_BAD_REQUEST:
                    print('ℹ️ Test user already exists, will try login')
                    return True
                else:
                    text = await response.text()
                    print(f'❌ Registration failed: {response.status} - {text}')
                    return False
        except Exception as e:
            print(f'❌ Registration error: {e}')
            return False

    async def login(self) ->bool:
        """Login with test user credentials."""
        try:
            login_data = {'email': 'test@example.com', 'password':
                'TestPassword123!'}
            async with self.session.post(f'{self.base_url}/api/v1/auth/login',
                json=login_data) as response:
                if response.status == HTTP_OK:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    print('✅ Login successful')
                    return True
                else:
                    text = await response.text()
                    print(f'❌ Login failed: {response.status} - {text}')
                    return False
        except Exception as e:
            print(f'❌ Login error: {e}')
            return False

    async def test_authenticated_endpoint(self, method: str, endpoint: str,
        data: Optional[Dict]=None) ->bool:
        """Test an endpoint with authentication."""
        if not self.auth_token:
            print(f'❌ No auth token for {endpoint}')
            return False
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        try:
            async with self.session.request(method,
                f'{self.base_url}{endpoint}', headers=headers, json=data
                ) as response:
                if response.status < HTTP_BAD_REQUEST:
                    print(f'✅ {method} {endpoint} - Status: {response.status}')
                    return True
                else:
                    text = await response.text()
                    print(
                        f'❌ {method} {endpoint} - Status: {response.status} - {text}'
                        )
                    return False
        except Exception as e:
            print(f'❌ {method} {endpoint} - Error: {e}')
            return False


async def main():
    """Run authenticated API tests."""
    print('🔐 Testing ruleIQ API with Authentication')
    print('=' * 50)
    async with APITester() as tester:
        if not await tester.register_test_user():
            return
        if not await tester.login():
            return
        endpoints_to_test = [('GET', '/api/v1/assessments'), ('GET',
            '/api/v1/business-profiles'), ('GET', '/api/v1/frameworks'), (
            'GET', '/api/v1/policies'), ('GET', '/api/v1/compliance/status'
            ), ('GET', '/api/v1/ai-assessments'), ('GET',
            '/api/v1/monitoring/health'), ('GET', '/api/v1/integrations')]
        success_count = 0
        for method, endpoint in endpoints_to_test:
            if await tester.test_authenticated_endpoint(method, endpoint):
                success_count += 1
        print(
            f'\n📊 Results: {success_count}/{len(endpoints_to_test)} endpoints working'
            )


if __name__ == '__main__':
    asyncio.run(main())
