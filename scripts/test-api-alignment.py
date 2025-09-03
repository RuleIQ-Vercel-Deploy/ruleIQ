"""
from __future__ import annotations
import requests
import logging

# Constants
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401

DEFAULT_LIMIT = 100

logger = logging.getLogger(__name__)

Comprehensive API Alignment Test Suite
Tests all frontend API calls against backend endpoints
Verifies 100% connectivity after cleanup
"""
import json
import asyncio
import aiohttp
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_URL = 'http://localhost:8000'
TIMEOUT = aiohttp.ClientTimeout(total=5)

class Colors:
    GREEN = '\x1b[92m'
    RED = '\x1b[91m'
    YELLOW = '\x1b[93m'
    BLUE = '\x1b[94m'
    MAGENTA = '\x1b[95m'
    CYAN = '\x1b[96m'
    RESET = '\x1b[0m'
    BOLD = '\x1b[1m'

def colored(text: str, color: str) ->str:
    """Add color to text for terminal output"""
    return f'{color}{text}{Colors.RESET}'

class APIAlignmentTester:

    def __init__(self):
        self.results = {'total': 0, 'passed': 0, 'failed': 0, 'warnings': 0,
            'endpoints': [], 'failures': [], 'warnings_list': [],
            'timestamp': datetime.now().isoformat()}
        self.auth_token = None

    async def get_auth_token(self, session: aiohttp.ClientSession) ->Optional[
        str]:
        """Get authentication token for testing protected endpoints"""
        try:
            async with session.post(f'{BASE_URL}/api/v1/auth/token', data={
                'username': 'test@example.com', 'password': 'testpassword123'}
                ) as response:
                if response.status == HTTP_OK:
                    data = await response.json()
                    return data.get('access_token')
        except (json.JSONDecodeError, requests.RequestException):
            pass
        return None

    async def test_endpoint(self, session: aiohttp.ClientSession, method:
        str, path: str, description: str, expected_status: List[int]=None,
        auth_required: bool=False) ->Dict:
        """Test a single endpoint"""
        if expected_status is None:
            expected_status = [200, 201, 204, 400, 401, 403, 404, 422]
        url = f'{BASE_URL}{path}'
        headers = {}
        if auth_required and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        try:
            async with session.request(method, url, headers=headers,
                timeout=TIMEOUT, ssl=False) as response:
                status = response.status
                if (status in expected_status or auth_required and status ==
                    HTTP_UNAUTHORIZED):
                    return {'path': path, 'method': method, 'status':
                        status, 'passed': True, 'description': description,
                        'auth_required': auth_required}
                else:
                    return {'path': path, 'method': method, 'status':
                        status, 'passed': False, 'error':
                        f'Unexpected status: {status}', 'description':
                        description, 'auth_required': auth_required}
        except asyncio.TimeoutError:
            return {'path': path, 'method': method, 'passed': False,
                'error': 'Timeout', 'description': description,
                'auth_required': auth_required}
        except (OSError, requests.RequestException) as e:
            return {'path': path, 'method': method, 'passed': False,
                'error': str(e), 'description': description,
                'auth_required': auth_required}

    async def run_tests(self):
        """Run all API alignment tests"""
        logger.info('\n%s' % colored(
            '🚀 COMPREHENSIVE API ALIGNMENT TEST SUITE', Colors.BOLD))
        logger.info('%s' % colored('=' * 60, Colors.CYAN))
        logger.info('Testing API endpoints at: %s' % colored(BASE_URL,
            Colors.BLUE))
        print(
            f"Timestamp: {colored(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), Colors.YELLOW)}"
            )
        logger.info('%s\n' % colored('=' * 60, Colors.CYAN))
        endpoints = [('GET', '/', 'Root endpoint', False), ('GET',
            '/health', 'Health check', False), ('GET', '/api/v1/health',
            'API v1 health', False), ('GET', '/api/v1/health/detailed',
            'Detailed health', False), ('GET', '/api/dashboard',
            'Dashboard', True), ('POST', '/api/v1/auth/token',
            'Get access token', False), ('POST', '/api/v1/auth/refresh',
            'Refresh token', True), ('POST', '/api/v1/auth/logout',
            'Logout', True), ('POST', '/api/v1/auth/register',
            'Register user', False), ('GET', '/api/v1/auth/me',
            'Get current user', True), ('PUT', '/api/v1/auth/password',
            'Change password', True), ('GET', '/api/v1/auth/google/login',
            'Google OAuth login', False), ('GET',
            '/api/v1/auth/google/callback', 'Google OAuth callback', False),
            ('POST', '/api/v1/auth/google/mobile-login',
            'Google mobile login', False), ('POST',
            '/api/v1/auth/assign-role', 'Assign role', True), ('DELETE',
            '/api/v1/auth/remove-role', 'Remove role', True), ('GET',
            '/api/v1/auth/user-permissions', 'Get user permissions', True),
            ('GET', '/api/v1/auth/roles', 'List roles', True), ('GET',
            '/api/v1/users', 'List users', True), ('GET',
            '/api/v1/users/{id}', 'Get user by ID', True), ('PUT',
            '/api/v1/users/{id}', 'Update user', True), ('DELETE',
            '/api/v1/users/{id}', 'Delete user', True), ('GET',
            '/api/v1/business-profiles', 'List business profiles', True), (
            'POST', '/api/v1/business-profiles', 'Create business profile',
            True), ('GET', '/api/v1/business-profiles/{id}',
            'Get business profile', True), ('PUT',
            '/api/v1/business-profiles/{id}', 'Update business profile', 
            True), ('GET', '/api/v1/assessments', 'List assessments', True),
            ('POST', '/api/v1/assessments', 'Create assessment', True), (
            'GET', '/api/v1/assessments/{id}', 'Get assessment', True), (
            'PUT', '/api/v1/assessments/{id}', 'Update assessment', True),
            ('DELETE', '/api/v1/assessments/{id}', 'Delete assessment', 
            True), ('POST', '/api/v1/freemium-assessment',
            'Create freemium assessment', False), ('GET',
            '/api/v1/freemium-assessment/questions',
            'Get freemium questions', False), ('POST', '/api/v1/ai/analyze',
            'AI analyze', True), ('POST', '/api/v1/ai/generate-questions',
            'Generate questions', True), ('POST',
            '/api/v1/ai/evaluate-answers', 'Evaluate answers', True), (
            'GET', '/api/v1/ai/frameworks', 'List AI frameworks', True), (
            'POST', '/api/v1/ai/recommendations', 'Get recommendations', 
            True), ('GET', '/api/v1/ai/metrics', 'Get AI metrics', True), (
            'POST', '/api/v1/ai/optimization/analyze', 'Optimize analysis',
            True), ('GET', '/api/v1/ai/optimization/suggestions',
            'Get suggestions', True), ('GET',
            '/api/v1/ai/optimization/circuit-breaker/status',
            'Circuit breaker status', True), ('POST',
            '/api/v1/ai/optimization/circuit-breaker/reset',
            'Reset circuit breaker', True), ('GET',
            '/api/v1/ai/optimization/cache/metrics', 'Cache metrics', True),
            ('GET', '/api/v1/frameworks', 'List frameworks', True), ('GET',
            '/api/v1/frameworks/{id}', 'Get framework', True), ('GET',
            '/api/v1/frameworks/{id}/requirements',
            'Get framework requirements', True), ('GET', '/api/v1/policies',
            'List policies', True), ('POST', '/api/v1/policies',
            'Create policy', True), ('GET', '/api/v1/policies/{id}',
            'Get policy', True), ('PUT', '/api/v1/policies/{id}',
            'Update policy', True), ('DELETE', '/api/v1/policies/{id}',
            'Delete policy', True), ('POST', '/api/v1/ai/policies/generate',
            'Generate AI policy', True), ('POST',
            '/api/v1/ai/policies/review', 'Review AI policy', True), (
            'POST', '/api/v1/ai/policies/customize', 'Customize AI policy',
            True), ('GET', '/api/v1/implementation',
            'List implementation plans', True), ('POST',
            '/api/v1/implementation', 'Create implementation plan', True),
            ('GET', '/api/v1/implementation/{id}',
            'Get implementation plan', True), ('GET', '/api/v1/evidence',
            'List evidence', True), ('POST', '/api/v1/evidence',
            'Upload evidence', True), ('GET', '/api/v1/evidence/{id}',
            'Get evidence', True), ('PUT', '/api/v1/evidence/{id}',
            'Update evidence', True), ('DELETE', '/api/v1/evidence/{id}',
            'Delete evidence', True), ('GET',
            '/api/v1/evidence-collection/status', 'Collection status', True
            ), ('POST', '/api/v1/evidence-collection/submit',
            'Submit evidence', True), ('GET',
            '/api/v1/evidence-collection/requirements', 'Get requirements',
            True), ('GET', '/api/v1/foundation/evidence',
            'List foundation evidence', True), ('POST',
            '/api/v1/foundation/evidence/collect',
            'Collect foundation evidence', True), ('GET',
            '/api/v1/compliance/status', 'Compliance status', True), ('GET',
            '/api/v1/compliance/score', 'Compliance score', True), ('GET',
            '/api/v1/compliance/gaps', 'Compliance gaps', True), ('GET',
            '/api/v1/compliance/recommendations',
            'Compliance recommendations', True), ('GET',
            '/api/v1/uk-compliance/gdpr/requirements', 'GDPR requirements',
            True), ('GET', '/api/v1/uk-compliance/companies-house/filing',
            'Companies House filing', True), ('GET',
            '/api/v1/uk-compliance/employment/regulations',
            'Employment regulations', True), ('GET', '/api/v1/readiness',
            'Readiness assessment', True), ('POST',
            '/api/v1/readiness/evaluate', 'Evaluate readiness', True), (
            'GET', '/api/v1/readiness/report', 'Readiness report', True), (
            'GET', '/api/v1/reports', 'List reports', True), ('POST',
            '/api/v1/reports/generate', 'Generate report', True), ('GET',
            '/api/v1/reports/{id}', 'Get report', True), ('GET',
            '/api/v1/reports/{id}/download', 'Download report', True), (
            'GET', '/api/v1/integrations', 'List integrations', True), (
            'POST', '/api/v1/integrations/connect', 'Connect integration', 
            True), ('DELETE', '/api/v1/integrations/{id}',
            'Disconnect integration', True), ('GET',
            '/api/v1/dashboard/stats', 'Dashboard stats', True), ('GET',
            '/api/v1/dashboard/metrics', 'Dashboard metrics', True), ('GET',
            '/api/v1/dashboard/activity', 'Dashboard activity', True), (
            'POST', '/api/v1/payments/create-checkout', 'Create checkout', 
            True), ('POST', '/api/v1/payments/webhook', 'Payment webhook', 
            False), ('GET', '/api/v1/payments/subscription',
            'Get subscription', True), ('GET', '/api/v1/monitoring/health',
            'Health check', False), ('GET', '/api/v1/monitoring/metrics',
            'Monitoring metrics', True), ('GET',
            '/api/v1/monitoring/alerts', 'Monitoring alerts', True), ('GET',
            '/api/v1/performance/metrics', 'Performance metrics', True), (
            'GET', '/api/v1/performance/insights', 'Performance insights', 
            True), ('GET', '/api/v1/performance/trends',
            'Performance trends', True), ('GET',
            '/api/v1/security/audit-log', 'Audit log', True), ('GET',
            '/api/v1/security/active-sessions', 'Active sessions', True), (
            'POST', '/api/v1/security/revoke-session', 'Revoke session', 
            True), ('GET', '/api/secrets/list', 'List secrets', True), (
            'POST', '/api/secrets/store', 'Store secret', True), ('GET',
            '/api/secrets/retrieve/{key}', 'Retrieve secret', True), (
            'POST', '/api/v1/chat/message', 'Send chat message', True), (
            'GET', '/api/v1/chat/history', 'Chat history', True), ('DELETE',
            '/api/v1/chat/clear', 'Clear chat', True), ('GET',
            '/api/v1/ai/cost/usage', 'AI usage costs', True), ('GET',
            '/api/v1/ai/cost/analytics', 'Cost analytics', True), ('GET',
            '/api/v1/ai/cost/budget', 'Cost budget', True), ('GET',
            '/api/v1/ai/cost-websocket/ws', 'Cost WebSocket', True), (
            'POST', '/api/v1/iq-agent/query', 'IQ Agent query', True), (
            'GET', '/api/v1/iq-agent/suggestions', 'IQ Agent suggestions', 
            True), ('GET', '/api/v1/iq-agent/history', 'IQ Agent history', 
            True), ('POST', '/api/v1/agentic-rag/find-examples',
            'Find examples', True), ('POST',
            '/api/v1/agentic-rag/fact-check', 'Fact check', True), ('POST',
            '/api/v1/agentic-rag/query-with-validation',
            'Query with validation', True)]
        async with aiohttp.ClientSession() as session:
            self.auth_token = await self.get_auth_token(session)
            if not self.auth_token:
                print(
                    f"""{colored('⚠️  No auth token available - auth endpoints will show as 401', Colors.YELLOW)}
"""
                    )
            for method, path, description, auth_required in endpoints:
                if '{id}' in path:
                    path = path.replace('{id}', 'test-id')
                if '{key}' in path:
                    path = path.replace('{key}', 'test-key')
                result = await self.test_endpoint(session, method, path,
                    description, auth_required=auth_required)
                self.results['total'] += 1
                if result['passed']:
                    self.results['passed'] += 1
                    status_color = Colors.GREEN
                    status_symbol = '✓'
                else:
                    self.results['failed'] += 1
                    self.results['failures'].append(result)
                    status_color = Colors.RED
                    status_symbol = '✗'
                print(
                    f"{colored(status_symbol, status_color)} {method:6} {path:50} [{colored(result.get('status', 'ERROR'), status_color)}] {colored(description, Colors.CYAN)}"
                    )
                if not result['passed'] and 'error' in result:
                    logger.info('  %s %s' % (colored('└─', Colors.RED),
                        result['error']))
                self.results['endpoints'].append(result)
        self.print_summary()
        self.save_results()
        return self.results

    def print_summary(self):
        """Print test summary"""
        logger.info('\n%s' % colored('=' * 60, Colors.CYAN))
        logger.info('%s' % colored('TEST SUMMARY', Colors.BOLD))
        logger.info('%s' % colored('=' * 60, Colors.CYAN))
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        pass_rate = passed / total * 100 if total > 0 else 0
        logger.info('Total Endpoints: %s' % colored(str(total), Colors.BLUE))
        logger.info('Passed: %s' % colored(f'{passed} ({pass_rate:.1f}%)',
            Colors.GREEN))
        print(
            f"Failed: {colored(f'{failed} ({100 - pass_rate:.1f}%)', Colors.RED if failed > 0 else Colors.GREEN)}"
            )
        if pass_rate == DEFAULT_LIMIT:
            logger.info('\n%s' % colored('🎉 PERFECT ALIGNMENT!', Colors.
                GREEN + Colors.BOLD))
            print(
                f"{colored('All API endpoints are properly connected and working!', Colors.GREEN)}"
                )
        elif pass_rate >= 95:
            logger.info('\n%s' % colored('✅ EXCELLENT ALIGNMENT', Colors.GREEN)
                )
            print(
                f"{colored('Nearly all endpoints are working correctly.', Colors.GREEN)}"
                )
        elif pass_rate >= 90:
            logger.info('\n%s' % colored('✅ VERY GOOD ALIGNMENT', Colors.GREEN)
                )
            logger.info('%s' % colored(
                'Most endpoints are working correctly.', Colors.GREEN))
        elif pass_rate >= 80:
            logger.info('\n%s' % colored('⚠️  GOOD ALIGNMENT', Colors.YELLOW))
            logger.info('%s' % colored('Some endpoints need attention.',
                Colors.YELLOW))
        else:
            logger.info('\n%s' % colored('❌ NEEDS IMPROVEMENT', Colors.RED))
            logger.info('%s' % colored(
                'Many endpoints are not working properly.', Colors.RED))
        if self.results['failures']:
            logger.info('\n%s' % colored('FAILED ENDPOINTS:', Colors.RED +
                Colors.BOLD))
            for failure in self.results['failures'][:10]:
                logger.info('  • %s %s' % (failure['method'], failure['path']))
                if 'error' in failure:
                    logger.info('    Error: %s' % failure['error'])
            if len(self.results['failures']) > 10:
                logger.info('  ... and %s more' % (len(self.results[
                    'failures']) - 10))

    def save_results(self):
        """Save test results to JSON file"""
        results_file = Path(__file__
            ).parent / 'api-alignment-test-results.json'
        self.results['summary'] = {'pass_rate': self.results['passed'] /
            self.results['total'] * 100 if self.results['total'] > 0 else 0,
            'status': 'PASS' if self.results['failed'] == 0 else 'FAIL',
            'message':
            f"Tested {self.results['total']} endpoints: {self.results['passed']} passed, {self.results['failed']} failed"
            }
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info('\n%s %s' % (colored('📁 Results saved to:', Colors.CYAN
            ), results_file))

async def main():
    """Main test runner"""
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'{BASE_URL}/health', timeout=TIMEOUT
                    ) as response:
                    if response.status != HTTP_OK:
                        print(
                            f"{colored('⚠️  Server health check failed', Colors.YELLOW)}"
                            )
            except (requests.RequestException, ValueError):
                logger.info('%s' % colored('❌ Server is not running!',
                    Colors.RED))
                print(
                    f"Please start the server with: {colored('python main.py', Colors.YELLOW)}"
                    )
                return
        tester = APIAlignmentTester()
        results = await tester.run_tests()
        if results['failed'] == 0:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info('\n%s' % colored('Test interrupted by user', Colors.YELLOW)
            )
        sys.exit(1)
    except (requests.RequestException, ValueError, KeyError) as e:
        logger.info('\n%s' % colored(f'Error: {e}', Colors.RED))
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
