"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

API Route Fixing Script for ruleIQ
Addresses the API routing mismatches identified in debug analysis.

Key Issues Found:
1. AI endpoints: Frontend expects '/api/v1/ai/assessments' but backend has '/api/v1/ai-assessments'
2. Some AI routers mounted at '/api/v1/ai' need specific sub-paths
3. Missing authentication for testing endpoints
"""

from pathlib import Path
from typing import Dict, List
ROUTE_MAPPINGS = {'/api/v1/ai/assessments': '/api/v1/ai-assessments',
    '/api/v1/ai/health': '/api/v1/ai-assessments/health',
    '/api/v1/ai/policies/generate': '/api/v1/ai/policies/generate',
    '/api/v1/ai/policies/templates': '/api/v1/ai/policies/templates',
    '/api/v1/ai/costs': '/api/v1/ai/costs', '/api/v1/chat/messages':
    '/api/v1/chat/messages', '/api/v1/compliance/score':
    '/api/v1/compliance/score', '/api/v1/compliance/check':
    '/api/v1/compliance/run-check', '/api/v1/monitoring/health':
    '/api/v1/monitoring/health', '/api/v1/monitoring/metrics':
    '/api/v1/monitoring/metrics', '/api/v1/integrations':
    '/api/v1/integrations', '/api/v1/reporting/reports':
    '/api/v1/reporting/reports'}


def find_api_service_files() ->List[Path]:
    """Find all API service files in the frontend."""
    frontend_path = Path('frontend/lib/api')
    if not frontend_path.exists():
        logger.info('❌ Frontend API path not found: %s' % frontend_path)
        return []
    service_files = list(frontend_path.glob('*.ts'))
    logger.info('📁 Found %s API service files:' % len(service_files))
    for f in service_files:
        logger.info('   - %s' % f)
    return service_files


def find_hook_files() ->List[Path]:
    """Find all TanStack Query hook files."""
    hooks_path = Path('frontend/lib/tanstack-query/hooks')
    if not hooks_path.exists():
        logger.info('❌ Hooks path not found: %s' % hooks_path)
        return []
    hook_files = list(hooks_path.glob('use-*.ts'))
    logger.info('📁 Found %s hook files:' % len(hook_files))
    for f in hook_files:
        logger.info('   - %s' % f)
    return hook_files


def update_api_routes_in_file(file_path: Path, route_mappings: Dict[str, str]
    ) ->bool:
    """Update API routes in a single file."""
    try:
        content = file_path.read_text()
        original_content = content
        changes_made = 0
        for old_route, new_route in route_mappings.items():
            patterns = [f"'{old_route}'", f'"{old_route}"',
                f'`{old_route}`', f"'{old_route}/", f'"{old_route}/',
                f'`{old_route}/']
            for pattern in patterns:
                if pattern in content:
                    replacement = pattern.replace(old_route, new_route)
                    content = content.replace(pattern, replacement)
                    changes_made += 1
                    logger.info('   ✅ %s → %s' % (old_route, new_route))
        if content != original_content:
            file_path.write_text(content)
            logger.info('📝 Updated %s (%s changes)' % (file_path, changes_made),
                )
            return True
        else:
            logger.info('📄 No changes needed in %s' % file_path)
            return False
    except Exception as e:
        logger.info('❌ Error updating %s: %s' % (file_path, e))
        return False


def update_debug_analysis_tool() ->bool:
    """Update the debug analysis tool with correct route mappings."""
    debug_file = Path('debug_api_analysis.py')
    if not debug_file.exists():
        logger.info('❌ debug_api_analysis.py not found')
        return False
    try:
        content = debug_file.read_text()
        old_ai_endpoints = ["'/api/v1/ai/assessments'",
            "'/api/v1/ai/health'", "'/api/v1/ai/policies/generate'",
            "'/api/v1/ai/policies/templates'", "'/api/v1/ai/costs'"]
        new_ai_endpoints = ["'/api/v1/ai-assessments'",
            "'/api/v1/ai-assessments/health'",
            "'/api/v1/ai/policies/generate'",
            "'/api/v1/ai/policies/templates'", "'/api/v1/ai/costs'"]
        for old, new in zip(old_ai_endpoints, new_ai_endpoints):
            content = content.replace(old, new)
        debug_file.write_text(content)
        logger.info('✅ Updated debug_api_analysis.py with correct routes')
        return True
    except Exception as e:
        logger.info('❌ Error updating debug analysis: %s' % e)
        return False


def create_auth_test_script() ->None:
    """Create a script to test endpoints with proper authentication."""
    script_content = """#!/usr/bin/env python3
""\"
Authenticated API Test Script
Tests ruleIQ API endpoints with proper authentication.
""\"

import asyncio
import aiohttp
import json
from typing import Dict, Optional

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def register_test_user(self) -> bool:
        ""\"Register a test user for authentication.""\"
        try:
            register_data = {
                "email": "test@example.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "company_name": "Test Company",
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data
            ) as response:
                if response.status == 201:
                    logger.info("✅ Test user registered successfully")
                    return True
                elif response.status == 400:
                    # User already exists, try to login
                    logger.info("ℹ️ Test user already exists, will try login")
                    return True
                else:
                    text = await response.text()
                    logger.info(f"❌ Registration failed: {response.status} - {text}")
                    return False
        except Exception as e:
            logger.info(f"❌ Registration error: {e}")
            return False
    
    async def login(self) -> bool:
        ""\"Login with test user credentials.""\"
        try:
            login_data = {
                "email": "test@example.com", 
                "password": "TestPassword123!",
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("✅ Login successful")
                    return True
                else:
                    text = await response.text()
                    logger.info(f"❌ Login failed: {response.status} - {text}")
                    return False
        except Exception as e:
            logger.info(f"❌ Login error: {e}")
            return False
    
    async def test_authenticated_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None) -> bool:
        ""\"Test an endpoint with authentication.""\"
        if not self.auth_token:
            logger.info(f"❌ No auth token for {endpoint}")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.request(
                method, 
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=data
            ) as response:
                if response.status < 400:
                    logger.info(f"✅ {method} {endpoint} - Status: {response.status}")
                    return True
                else:
                    text = await response.text()
                    logger.info(f"❌ {method} {endpoint} - Status: {response.status} - {text}")
                    return False
        except Exception as e:
            logger.info(f"❌ {method} {endpoint} - Error: {e}")
            return False

async def main():
    ""\"Run authenticated API tests.""\"
    logger.info("🔐 Testing ruleIQ API with Authentication")
    logger.info("=" * 50)
    
    async with APITester() as tester:
        # Step 1: Register/Login
        if not await tester.register_test_user():
            return
        
        if not await tester.login():
            return
        
        # Step 2: Test authenticated endpoints
        endpoints_to_test = [
            ("GET", "/api/v1/assessments"),
            ("GET", "/api/v1/business-profiles"),
            ("GET", "/api/v1/frameworks"),
            ("GET", "/api/v1/policies"),
            ("GET", "/api/v1/compliance/status"),
            ("GET", "/api/v1/ai-assessments"),  # Corrected route
            ("GET", "/api/v1/monitoring/health"),
            ("GET", "/api/v1/integrations"),
        ]
        
        success_count = 0
        for method, endpoint in endpoints_to_test:
            if await tester.test_authenticated_endpoint(method, endpoint):
                success_count += 1
        
        logger.info(f"\\n📊 Results: {success_count}/{len(endpoints_to_test)} endpoints working")

if __name__ == "__main__":
    asyncio.run(main())
"""
    script_path = Path('test_auth_api.py')
    script_path.write_text(script_content)
    script_path.chmod(493)
    logger.info('✅ Created authenticated API test script: test_auth_api.py')


def main() ->None:
    """Main execution function."""
    logger.info('🔧 ruleIQ API Route Fixing Script')
    logger.info('=' * 50)
    logger.info('\\n📝 Updating API service files...')
    service_files = find_api_service_files()
    service_updates = 0
    for file_path in service_files:
        if update_api_routes_in_file(file_path, ROUTE_MAPPINGS):
            service_updates += 1
    logger.info('   Updated %s/%s service files' % (service_updates, len(
        service_files)))
    logger.info('\\n🪝 Updating TanStack Query hook files...')
    hook_files = find_hook_files()
    hook_updates = 0
    for file_path in hook_files:
        if update_api_routes_in_file(file_path, ROUTE_MAPPINGS):
            hook_updates += 1
    logger.info('   Updated %s/%s hook files' % (hook_updates, len(hook_files)),
        )
    logger.info('\\n🔍 Updating debug analysis tool...')
    update_debug_analysis_tool()
    logger.info('\\n🔐 Creating authenticated test script...')
    create_auth_test_script()
    logger.info('\\n🎉 Route fixing complete!')
    logger.info('\\nNext steps:')
    logger.info('1. Run: python test_auth_api.py (to test with authentication)',
        )
    logger.info('2. Run: python debug_api_analysis.py (to verify fixed routes)',
        )
    logger.info('3. Test frontend compliance wizard integration')


if __name__ == '__main__':
    main()
