"""
from __future__ import annotations
import requests
import logging

# Constants
FIVE_MINUTES_SECONDS = 300

logger = logging.getLogger(__name__)

Comprehensive API Connection Test Script
Tests all 99+ API endpoints to ensure frontend-backend connectivity
"""
import asyncio
import httpx
from typing import Dict, List, Tuple
import json
from datetime import datetime
BASE_URL = 'http://localhost:8000/api/v1'
TEST_TOKEN = 'your-test-token-here'

class APIConnectionTester:

    """Class for APIConnectionTester"""
    def __init__(self):
        self.headers = {'Authorization': f'Bearer {TEST_TOKEN}',
            'Content-Type': 'application/json'}
        self.results = {'total': 0, 'passed': 0, 'failed': 0, 'errors': []}

    async def test_endpoint(self, method: str, path: str, data: dict=None
        ) ->Tuple[bool, str]:
        """Test a single endpoint"""
        url = f'{BASE_URL}/{path}'
        try:
            async with httpx.AsyncClient() as client:
                if method == 'GET':
                    response = await client.get(url, headers=self.headers,
                        timeout=5.0)
                elif method == 'POST':
                    response = await client.post(url, headers=self.headers,
                        json=data or {}, timeout=5.0)
                elif method == 'PATCH':
                    response = await client.patch(url, headers=self.headers,
                        json=data or {}, timeout=5.0)
                elif method == 'PUT':
                    response = await client.put(url, headers=self.headers,
                        json=data or {}, timeout=5.0)
                elif method == 'DELETE':
                    response = await client.delete(url, headers=self.
                        headers, timeout=5.0)
                else:
                    return False, f'Unknown method: {method}'
                if (response.status_code < FIVE_MINUTES_SECONDS or response
                    .status_code in [401, 403]):
                    return True, f'Status: {response.status_code}'
                else:
                    return False, f'Status: {response.status_code}'
        except httpx.ConnectError:
            return False, 'Connection refused - is the server running?'
        except httpx.TimeoutException:
            return False, 'Request timeout'
        except (json.JSONDecodeError, requests.RequestException, KeyError
            ) as e:
            return False, str(e)

    async def run_all_tests(self):
        """Run tests for all endpoints"""
        endpoints = [('GET', 'evidence/'), ('GET', 'evidence/test-id'), (
            'POST', 'evidence/', {'name': 'test', 'file': 'test.pdf'}), (
            'PATCH', 'evidence/test-id', {'status': 'verified'}), ('POST',
            'evidence/test-id/automation', {'schedule': 'daily'}), ('GET',
            'evidence/dashboard/gdpr'), ('POST',
            'evidence/test-id/classify', {'classification': 'critical'}), (
            'GET', 'evidence/requirements/gdpr'), ('GET',
            'evidence/test-id/quality'), ('GET', 'compliance/status/gdpr'),
            ('POST', 'compliance/tasks', {'title': 'test task'}), ('PATCH',
            'compliance/tasks/task-123', {'status': 'completed'}), ('POST',
            'compliance/risks', {'title': 'test risk'}), ('PATCH',
            'compliance/risks/risk-123', {'severity': 'high'}), ('GET',
            'compliance/timeline'), ('GET', 'compliance/dashboard'), (
            'POST', 'compliance/certificate/generate', {'framework': 'gdpr'
            }), ('GET', 'policies/'), ('GET', 'policies/policy-123'), (
            'PATCH', 'policies/policy-123/status', {'status': 'approved'}),
            ('PUT', 'policies/policy-123/approve'), ('POST',
            'policies/policy-123/regenerate-section', {'section': 'intro'}),
            ('GET', 'policies/templates'), ('POST',
            'policies/policy-123/clone', {'name': 'cloned policy'}), ('GET',
            'policies/policy-123/versions'), ('GET', 'frameworks/'), ('GET',
            'frameworks/gdpr'), ('GET', 'frameworks/gdpr/controls'), ('GET',
            'frameworks/gdpr/implementation-guide'), ('GET',
            'frameworks/gdpr/compliance-status'), ('POST',
            'frameworks/compare', {'frameworks': ['gdpr', 'iso27001']}), (
            'GET', 'frameworks/gdpr/maturity-assessment'), ('GET',
            'integrations/'), ('GET', 'integrations/connected'), ('POST',
            'integrations/google-workspace/test'), ('GET',
            'integrations/google-workspace/sync-history'), ('POST',
            'integrations/google-workspace/webhooks', {'url': 'test'}), (
            'GET', 'integrations/google-workspace/logs'), ('POST',
            'integrations/oauth/callback', {'code': 'test'}), ('GET',
            'monitoring/database/status'), ('PATCH',
            'monitoring/alerts/alert-123/resolve'), ('GET',
            'monitoring/metrics'), ('GET', 'monitoring/api-performance'), (
            'GET', 'monitoring/error-logs'), ('GET', 'monitoring/health'),
            ('GET', 'monitoring/audit-logs'), ('POST',
            'payments/subscription/cancel'), ('POST',
            'payments/subscription/reactivate'), ('POST',
            'payments/payment-methods', {'method': 'card'}), ('GET',
            'payments/invoices'), ('GET', 'payments/invoices/upcoming'), (
            'POST', 'payments/coupons/apply', {'code': 'TEST'}), ('GET',
            'payments/subscription/limits'), ('GET', 'assessments/'), (
            'GET', 'assessments/assess-123'), ('POST', 'assessments/', {
            'title': 'test'}), ('PATCH', 'assessments/assess-123', {
            'status': 'in_progress'}), ('POST',
            'assessments/assess-123/complete'), ('GET',
            'assessments/assess-123/results'), ('GET', 'readiness/biz-123'),
            ('GET', 'readiness/gaps/biz-123'), ('POST', 'readiness/roadmap',
            {'profile_id': 'biz-123'}), ('POST',
            'readiness/quick-assessment', {'data': {}}), ('GET',
            'readiness/trends/biz-123'), ('GET', 'readiness/benchmarks'), (
            'GET', 'reports/history'), ('GET', 'reports/report-123'), (
            'POST', 'reports/schedule', {'schedule': 'weekly'}), ('GET',
            'reports/scheduled'), ('POST', 'reports/preview', {'type':
            'compliance'}), ('GET', 'reports/analytics'), ('GET',
            'business-profiles/'), ('GET', 'business-profiles/biz-123'), (
            'POST', 'business-profiles/', {'name': 'test'}), ('PUT',
            'business-profiles/biz-123', {'name': 'updated'}), ('GET',
            'business-profiles/biz-123/compliance'), ('GET', 'dashboard/'),
            ('GET', 'dashboard/widgets'), ('GET', 'dashboard/notifications'
            ), ('GET', 'dashboard/quick-actions'), ('GET',
            'dashboard/recommendations'), ('POST',
            'foundation/evidence/aws/configure', {'config': {}}), ('POST',
            'foundation/evidence/okta/configure', {'config': {}}), ('POST',
            'foundation/evidence/google/configure', {'config': {}}), (
            'POST', 'foundation/evidence/microsoft/configure', {'config': {
            }}), ('GET', 'foundation/evidence/health'), ('POST',
            'ai/self-review', {'data': {}}), ('POST',
            'ai/quick-confidence-check', {'responses': {}}), ('POST',
            'ai/assessments/followup', {'question': 'test'}), ('GET',
            'ai/assessments/metrics'), ('GET',
            'chat/conversations/conv-123'), ('POST',
            'chat/compliance-gap-analysis', {'framework': 'gdpr'}), ('GET',
            'chat/smart-compliance-guidance'), ('DELETE',
            'chat/cache/clear?pattern=test'), ('GET',
            'implementation/plans/plan-123'), ('GET',
            'implementation/recommendations'), ('GET',
            'implementation/resources/gdpr'), ('GET',
            'implementation/plans/plan-123/analytics'), ('GET',
            'evidence-collection/plans')]
        logger.info('\n%s' % ('=' * 60))
        logger.info('API CONNECTION TEST - COMPREHENSIVE')
        logger.info('%s' % ('=' * 60))
        logger.info('Testing %s endpoints...' % len(endpoints))
        logger.info('Base URL: %s' % BASE_URL)
        logger.info('%s\n' % ('=' * 60))
        for method, path, *data in endpoints:
            self.results['total'] += 1
            data_dict = data[0] if data else None
            success, message = await self.test_endpoint(method, path, data_dict
                )
            if success:
                self.results['passed'] += 1
                status = '✅ PASS'
            else:
                self.results['failed'] += 1
                status = '❌ FAIL'
                self.results['errors'].append({'endpoint':
                    f'{method} /{path}', 'error': message})
            display_path = path.replace('test-id', '{id}').replace('123',
                '{id}')
            logger.info('%s %s /%s %s' % (status, method, display_path,
                message))
        logger.info('\n%s' % ('=' * 60))
        logger.info('TEST SUMMARY')
        logger.info('%s' % ('=' * 60))
        logger.info('Total Endpoints: %s' % self.results['total'])
        print(
            f"Passed: {self.results['passed']} ({self.results['passed'] / self.results['total'] * 100:.1f}%)"
            )
        print(
            f"Failed: {self.results['failed']} ({self.results['failed'] / self.results['total'] * 100:.1f}%)"
            )
        if self.results['errors']:
            logger.info('\n%s' % ('=' * 60))
            logger.info('FAILED ENDPOINTS')
            logger.info('%s' % ('=' * 60))
            for error in self.results['errors'][:10]:
                logger.info('- %s: %s' % (error['endpoint'], error['error']))
            if len(self.results['errors']) > 10:
                logger.info('... and %s more' % (len(self.results['errors']
                    ) - 10))
        with open('api-connection-test-results.json', 'w') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'results':
                self.results}, f, indent=2)
        logger.info(
            '\n✅ Results saved to scripts/api-connection-test-results.json')
        return self.results['failed'] == 0

async def main():
    """Main test runner"""
    tester = APIConnectionTester()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{BASE_URL}/health', timeout=2.0)
            logger.info('✅ Server is running (Health check: %s)' % response
                .status_code)
    except requests.RequestException:
        logger.info('❌ Server is not running! Please start the server with:')
        logger.info('   python main.py')
        return False
    success = await tester.run_all_tests()
    if success:
        logger.info(
            '\n🎉 ALL TESTS PASSED! All API endpoints are properly connected.')
    else:
        logger.info('\n⚠️  Some tests failed. Please review the errors above.')
    return success

if __name__ == '__main__':
    asyncio.run(main())
