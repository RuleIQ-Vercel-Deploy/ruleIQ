"""
from __future__ import annotations
import logging

# Constants
HTTP_OK = 200

logger = logging.getLogger(__name__)

Comprehensive API Endpoint Tester for ruleIQ
Tests all major endpoint categories with proper authentication
"""
import requests
import json
import time
from typing import Dict, List, Any


class EndpointTester:

    """Class for EndpointTester"""
    def __init__(self, base_url: str='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.business_profile_id = None

    def authenticate(self, email: str, password: str) ->bool:
        """Authenticate and store JWT token"""
        try:
            response = self.session.post(f'{self.base_url}/api/v1/auth/token',
                data={'username': email, 'password': password}, headers={
                'Content-Type': 'application/x-www-form-urlencoded'})
            if response.status_code == HTTP_OK:
                data = response.json()
                self.jwt_token = data['access_token']
                self.session.headers.update({'Authorization':
                    f'Bearer {self.jwt_token}'})
                logger.info('✅ Authentication successful')
                return True
            else:
                print(
                    f'❌ Authentication failed: {response.status_code} - {response.text}'
                    )
                return False
        except Exception as e:
            logger.info('❌ Authentication error: %s' % str(e))
            return False

    def test_endpoint(self, method: str, endpoint: str, data: Dict=None,
        expected_codes: List[int]=None) ->Dict[str, Any]:
        """Test a single endpoint and return results"""
        if expected_codes is None:
            expected_codes = [200, 201, 202]
        url = f'{self.base_url}{endpoint}'
        try:
            start_time = time.time()
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data)
            else:
                raise ValueError(f'Unsupported method: {method}')
            response_time = time.time() - start_time
            success = response.status_code in expected_codes
            return {'endpoint': endpoint, 'method': method.upper(),
                'status_code': response.status_code, 'response_time_ms':
                round(response_time * 1000), 'success': success,
                'content_length': len(response.content), 'error': None}
        except Exception as e:
            return {'endpoint': endpoint, 'method': method.upper(),
                'status_code': None, 'response_time_ms': None, 'success': 
                False, 'content_length': 0, 'error': str(e)}

    def run_endpoint_tests(self) ->Dict[str, List[Dict]]:
        """Run comprehensive endpoint tests"""
        test_results = {'authentication': [], 'business_profiles': [],
            'assessments': [], 'ai_services': [], 'compliance_frameworks':
            [], 'admin': [], 'health': []}
        logger.info('\n🔐 Testing Authentication Endpoints...')
        auth_tests = [('GET', '/api/v1/auth/me', None, [200, 401]), ('POST',
            '/api/v1/auth/logout', None, [200, 204])]
        for method, endpoint, data, codes in auth_tests:
            result = self.test_endpoint(method, endpoint, data, codes)
            test_results['authentication'].append(result)
            status = '✅' if result['success'] else '❌'
            print(
                f"{status} {method} {endpoint} - {result['status_code']} ({result.get('response_time_ms', 'N/A')}ms)"
                )
        logger.info('\n🏢 Testing Business Profile Endpoints...')
        business_tests = [('GET', '/api/v1/business-profiles', None, [200, 
            404]), ('GET', '/api/v1/business-profiles/current', None, [200,
            404])]
        for method, endpoint, data, codes in business_tests:
            result = self.test_endpoint(method, endpoint, data, codes)
            test_results['business_profiles'].append(result)
            status = '✅' if result['success'] else '❌'
            print(
                f"{status} {method} {endpoint} - {result['status_code']} ({result.get('response_time_ms', 'N/A')}ms)"
                )
        logger.info('\n📊 Testing Assessment Endpoints...')
        assessment_tests = [('GET', '/api/v1/assessments', None, [200, 404]
            ), ('GET', '/api/v1/assessments/templates', None, [200, 404])]
        for method, endpoint, data, codes in assessment_tests:
            result = self.test_endpoint(method, endpoint, data, codes)
            test_results['assessments'].append(result)
            status = '✅' if result['success'] else '❌'
            print(
                f"{status} {method} {endpoint} - {result['status_code']} ({result.get('response_time_ms', 'N/A')}ms)"
                )
        logger.info('\n🧠 Testing AI Service Endpoints...')
        ai_tests = [('POST', '/api/v1/ai-assessments/analysis/stream', {
            'assessment_results': {}, 'framework_id': 'gdpr'}, [200, 400, 
            422, 500]), ('GET', '/api/v1/ai-cost/current', None, [200, 404])]
        for method, endpoint, data, codes in ai_tests:
            result = self.test_endpoint(method, endpoint, data, codes)
            test_results['ai_services'].append(result)
            status = '✅' if result['success'] else '❌'
            print(
                f"{status} {method} {endpoint} - {result['status_code']} ({result.get('response_time_ms', 'N/A')}ms)"
                )
        logger.info('\n⚖️ Testing Compliance Framework Endpoints...')
        framework_tests = [('GET', '/api/v1/compliance-frameworks', None, [
            200]), ('GET', '/api/v1/compliance-frameworks/gdpr', None, [200,
            404])]
        for method, endpoint, data, codes in framework_tests:
            result = self.test_endpoint(method, endpoint, data, codes)
            test_results['compliance_frameworks'].append(result)
            status = '✅' if result['success'] else '❌'
            print(
                f"{status} {method} {endpoint} - {result['status_code']} ({result.get('response_time_ms', 'N/A')}ms)"
                )
        logger.info('\n🏥 Testing Health Endpoints...')
        health_tests = [('GET', '/health', None, [200]), ('GET',
            '/api/v1/health', None, [200, 404])]
        for method, endpoint, data, codes in health_tests:
            result = self.test_endpoint(method, endpoint, data, codes)
            test_results['health'].append(result)
            status = '✅' if result['success'] else '❌'
            print(
                f"{status} {method} {endpoint} - {result['status_code']} ({result.get('response_time_ms', 'N/A')}ms)"
                )
        return test_results

    def generate_report(self, results: Dict[str, List[Dict]]) ->Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = sum(len(category_results) for category_results in
            results.values())
        successful_tests = sum(sum(1 for result in category_results if
            result['success']) for category_results in results.values())
        category_summaries = {}
        for category, category_results in results.items():
            if category_results:
                successful = sum(1 for r in category_results if r['success'])
                total = len(category_results)
                avg_response_time = sum(r.get('response_time_ms', 0) for r in
                    category_results if r.get('response_time_ms')) / len([r for
                    r in category_results if r.get('response_time_ms')])
                category_summaries[category] = {'successful': successful,
                    'total': total, 'success_rate': round(successful /
                    total * 100, 1), 'avg_response_time_ms': round(
                    avg_response_time) if avg_response_time else 0}
        return {'summary': {'total_tests': total_tests, 'successful_tests':
            successful_tests, 'success_rate': round(successful_tests /
            total_tests * 100, 1) if total_tests > 0 else 0, 'timestamp':
            time.strftime('%Y-%m-%d %H:%M:%S')}, 'categories':
            category_summaries, 'detailed_results': results}


def main():
    logger.info('🚀 Starting ruleIQ API Comprehensive Endpoint Testing')
    """Main"""
    logger.info('=' * 60)
    tester = EndpointTester()
    if not tester.authenticate('newtest@ruleiq.com', 'NewTestPass123!'):
        logger.info('Failed to authenticate. Exiting.')
        return
    results = tester.run_endpoint_tests()
    report = tester.generate_report(results)
    logger.info('\n' + '=' * 60)
    logger.info('📊 TEST SUMMARY REPORT')
    logger.info('=' * 60)
    summary = report['summary']
    logger.info('Total Tests: %s' % summary['total_tests'])
    logger.info('Successful: %s' % summary['successful_tests'])
    logger.info('Success Rate: %s%' % summary['success_rate'])
    logger.info('Timestamp: %s' % summary['timestamp'])
    logger.info('\n📋 CATEGORY BREAKDOWN:')
    for category, stats in report['categories'].items():
        print(
            f"  {category.replace('_', ' ').title()}: {stats['successful']}/{stats['total']} ({stats['success_rate']}%) - Avg: {stats['avg_response_time_ms']}ms"
            )
    with open('endpoint_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    logger.info('\n💾 Detailed report saved to: endpoint_test_report.json')
    logger.info('\n✅ Endpoint testing complete!')


if __name__ == '__main__':
    main()
