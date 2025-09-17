"""Quick API test to verify connectivity without timeout"""
import logging

# Constants
HTTP_INTERNAL_SERVER_ERROR = 500

DEFAULT_LIMIT = 100

logger = logging.getLogger(__name__)
import asyncio
import aiohttp
import json
from datetime import datetime
BASE_URL = 'http://localhost:8000'


async def test_endpoints():
    """Test key endpoints to verify API alignment"""
    test_endpoints = [('GET', '/', 'Root', False), ('GET', '/health',
        'Health', False), ('GET', '/api/v1/health', 'API Health', False), (
        'POST', '/api/v1/auth/token', 'Auth Token', False), ('GET',
        '/api/v1/auth/me', 'Current User', True), ('GET',
        '/api/v1/auth/google/login', 'Google Login', False), ('GET',
        '/api/v1/users', 'List Users', True), ('GET',
        '/api/v1/business-profiles', 'Business Profiles', True), ('GET',
        '/api/v1/assessments', 'Assessments', True), ('GET',
        '/api/v1/frameworks', 'Frameworks', True), ('GET',
        '/api/v1/policies', 'Policies', True), ('POST',
        '/api/v1/ai/analyze', 'AI Analyze', True), ('GET',
        '/api/v1/ai/optimization/circuit-breaker/status', 'Circuit Breaker',
        True), ('GET', '/api/v1/compliance/status', 'Compliance Status',
        True), ('GET', '/api/v1/dashboard/stats', 'Dashboard Stats', True),
        ('GET', '/api/v1/monitoring/health', 'Monitoring Health', False), (
        'POST', '/api/v1/agentic-rag/find-examples', 'RAG Examples', True),
        ('POST', '/api/v1/chat/message', 'Chat Message', True), ('GET',
        '/api/v1/iq-agent/suggestions', 'IQ Agent', True)]
    results = {'timestamp': datetime.now().isoformat(), 'total': 0,
        'passed': 0, 'failed': 0, 'endpoints': []}
    async with aiohttp.ClientSession() as session:
        for method, path, name, auth_required in test_endpoints:
            results['total'] += 1
            try:
                async with session.request(method, f'{BASE_URL}{path}',
                    timeout=aiohttp.ClientTimeout(total=2)) as response:
                    status = response.status
                    if (status < HTTP_INTERNAL_SERVER_ERROR or
                        auth_required and status in [401, 403]):
                        results['passed'] += 1
                        logger.info('✓ %s %s [%s] - %s' % (method, path,
                            status, name))
                        results['endpoints'].append({'method': method,
                            'path': path, 'status': status, 'passed': True,
                            'name': name})
                    else:
                        results['failed'] += 1
                        logger.info('✗ %s %s [%s] - %s' % (method, path,
                            status, name))
                        results['endpoints'].append({'method': method,
                            'path': path, 'status': status, 'passed': False,
                            'name': name})
            except Exception as e:
                results['failed'] += 1
                logger.info('✗ %s %s [ERROR] - %s: %s' % (method, path,
                    name, str(e)))
                results['endpoints'].append({'method': method, 'path': path,
                    'error': str(e), 'passed': False, 'name': name})
    pass_rate = results['passed'] / results['total'] * 100 if results['total',
        ] > 0 else 0
    logger.info('\n%s' % ('=' * 60))
    logger.info('QUICK API TEST SUMMARY')
    logger.info('%s' % ('=' * 60))
    logger.info('Total Endpoints Tested: %s' % results['total'])
    logger.info('Passed: %s (%s%)' % (results['passed'], pass_rate))
    logger.info('Failed: %s (%s%)' % (results['failed'], 100 - pass_rate))
    if pass_rate == DEFAULT_LIMIT:
        logger.info('\n🎉 PERFECT! All tested endpoints are connected!')
    elif pass_rate >= 90:
        logger.info('\n✅ EXCELLENT! Most endpoints are working!')
    else:
        logger.info('\n⚠️  Some endpoints need attention')
    with open('scripts/quick-api-test-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    logger.info('\nResults saved to: scripts/quick-api-test-results.json')
    return results


if __name__ == '__main__':
    asyncio.run(test_endpoints())
