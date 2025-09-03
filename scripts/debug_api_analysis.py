"""
from __future__ import annotations
import logging

# Constants
HTTP_BAD_REQUEST = 400
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_NOT_FOUND = 404
HTTP_OK = 200

MAX_ITEMS = 1000

logger = logging.getLogger(__name__)

API Route Analysis and Debugging Tool for ruleIQ

Analyzes the current API routes, identifies missing endpoints,
and provides debugging information for frontend API integration issues.
"""
import sys
import json
import asyncio
import requests
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class APIEndpoint:
    """Represents an API endpoint"""
    path: str
    method: str
    router: str
    exists: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

@dataclass
class APIAnalysisResult:
    """Results of API analysis"""
    total_endpoints: int
    working_endpoints: int
    missing_endpoints: int
    error_endpoints: int
    endpoints: List[APIEndpoint]
    router_mapping: Dict[str, List[str]]
    issues_found: List[str]
    recommendations: List[str]

class APIRouteAnalyzer:
    """Analyzes API routes and tests connectivity"""

    def __init__(self, base_url: str='http://localhost:8000'):
        self.base_url = base_url
        self.expected_endpoints = self._get_expected_endpoints()
        self.actual_routes = {}

    def _get_expected_endpoints(self) ->List[Dict[str, str]]:
        """Get list of expected endpoints based on test file analysis"""
        return [{'path': '/api/v1/auth/register', 'method': 'POST',
            'router': 'auth'}, {'path': '/api/v1/auth/login', 'method':
            'POST', 'router': 'auth'}, {'path': '/api/v1/auth/me', 'method':
            'GET', 'router': 'auth'}, {'path': '/api/v1/auth/refresh',
            'method': 'POST', 'router': 'auth'}, {'path':
            '/api/v1/assessments', 'method': 'GET', 'router': 'assessments'
            }, {'path': '/api/v1/assessments', 'method': 'POST', 'router':
            'assessments'}, {'path': '/api/v1/assessments/readiness',
            'method': 'GET', 'router': 'assessments'}, {'path':
            '/api/v1/business-profiles', 'method': 'GET', 'router':
            'business_profiles'}, {'path': '/api/v1/business-profiles',
            'method': 'POST', 'router': 'business_profiles'}, {'path':
            '/api/v1/frameworks', 'method': 'GET', 'router': 'frameworks'},
            {'path': '/api/v1/policies', 'method': 'GET', 'router':
            'policies'}, {'path': '/api/v1/policies/generate', 'method':
            'POST', 'router': 'policies'}, {'path':
            '/api/v1/ai/assessments', 'method': 'POST', 'router':
            'ai_assessments'}, {'path': '/api/v1/ai/health', 'method':
            'GET', 'router': 'ai_assessments'}, {'path':
            '/api/v1/ai/policies/generate', 'method': 'POST', 'router':
            'ai_policy'}, {'path': '/api/v1/ai/policies/templates',
            'method': 'GET', 'router': 'ai_policy'}, {'path':
            '/api/v1/ai/costs', 'method': 'GET', 'router':
            'ai_cost_monitoring'}, {'path': '/api/v1/chat/messages',
            'method': 'POST', 'router': 'chat'}, {'path':
            '/api/v1/compliance/status', 'method': 'GET', 'router':
            'compliance'}, {'path': '/api/v1/compliance/score', 'method':
            'GET', 'router': 'compliance'}, {'path':
            '/api/v1/compliance/check', 'method': 'POST', 'router':
            'compliance'}, {'path': '/api/v1/monitoring/health', 'method':
            'GET', 'router': 'monitoring'}, {'path':
            '/api/v1/monitoring/metrics', 'method': 'GET', 'router':
            'monitoring'}, {'path': '/api/v1/integrations', 'method': 'GET',
            'router': 'integrations'}, {'path': '/api/v1/reporting/reports',
            'method': 'GET', 'router': 'reporting'}]

    async def analyze_routes(self) ->APIAnalysisResult:
        """Analyze all API routes and test connectivity"""
        logger.info('🔍 Starting comprehensive API route analysis...')
        endpoints = []
        router_mapping = {}
        issues_found = []
        recommendations = []
        try:
            response = requests.get(f'{self.base_url}/health', timeout=5)
            if response.status_code != HTTP_OK:
                issues_found.append(
                    f'Health endpoint failed: {response.status_code}')
            else:
                logger.info('✅ Basic connectivity confirmed')
        except Exception as e:
            issues_found.append(f'Cannot connect to backend: {str(e)}')
            logger.info('❌ Backend connection failed: %s' % e)
            return APIAnalysisResult(0, 0, 0, 1, [], {}, issues_found,
                recommendations)
        try:
            response = requests.get(f'{self.base_url}/api/v1/openapi.json',
                timeout=5)
            if response.status_code == HTTP_OK:
                openapi_data = response.json()
                actual_paths = set(openapi_data.get('paths', {}).keys())
                logger.info('📋 Found %s documented API paths' % len(
                    actual_paths))
            else:
                actual_paths = set()
                issues_found.append('OpenAPI documentation not available')
        except Exception as e:
            actual_paths = set()
            issues_found.append(f'Failed to fetch OpenAPI spec: {str(e)}')
        for endpoint_info in self.expected_endpoints:
            path = endpoint_info['path']
            method = endpoint_info['method']
            router = endpoint_info['router']
            if router not in router_mapping:
                router_mapping[router] = []
            router_mapping[router].append(f'{method} {path}')
            endpoint_result = await self._test_endpoint(path, method, router)
            endpoints.append(endpoint_result)
            if not endpoint_result.exists:
                logger.info('❌ %s %s - Not found (router: %s)' % (method,
                    path, router))
            elif endpoint_result.error:
                logger.info('⚠️ %s %s - Error: %s' % (method, path,
                    endpoint_result.error))
            else:
                print(
                    f'✅ {method} {path} - Working ({endpoint_result.response_time_ms:.0f}ms)'
                    )
        working_endpoints = len([e for e in endpoints if e.exists and not e
            .error])
        missing_endpoints = len([e for e in endpoints if not e.exists])
        error_endpoints = len([e for e in endpoints if e.exists and e.error])
        issues_found.extend(self._identify_issues(endpoints, actual_paths))
        recommendations.extend(self._generate_recommendations(endpoints,
            router_mapping))
        return APIAnalysisResult(total_endpoints=len(endpoints),
            working_endpoints=working_endpoints, missing_endpoints=
            missing_endpoints, error_endpoints=error_endpoints, endpoints=
            endpoints, router_mapping=router_mapping, issues_found=
            issues_found, recommendations=recommendations)

    async def _test_endpoint(self, path: str, method: str, router: str
        ) ->APIEndpoint:
        """Test a specific endpoint"""
        url = f'{self.base_url}{path}'
        start_time = time.perf_counter()
        try:
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                test_data = self._get_test_data_for_endpoint(path)
                response = requests.post(url, json=test_data, timeout=5)
            else:
                return APIEndpoint(path, method, router, False, error=
                    'Method not tested')
            response_time_ms = (time.perf_counter() - start_time) * 1000
            if response.status_code == HTTP_NOT_FOUND:
                return APIEndpoint(path, method, router, False, response.
                    status_code, response_time_ms)
            exists = True
            error = None
            if response.status_code >= HTTP_INTERNAL_SERVER_ERROR:
                error = f'Server error: {response.status_code}'
            elif response.status_code >= HTTP_BAD_REQUEST and response.status_code != HTTP_NOT_FOUND:
                error = f'Client error: {response.status_code}'
            return APIEndpoint(path, method, router, exists, response.
                status_code, response_time_ms, error)
        except requests.exceptions.ConnectTimeout:
            return APIEndpoint(path, method, router, False, error=
                'Connection timeout')
        except requests.exceptions.ConnectionError:
            return APIEndpoint(path, method, router, False, error=
                'Connection failed')
        except Exception as e:
            return APIEndpoint(path, method, router, False, error=str(e))

    def _get_test_data_for_endpoint(self, path: str) ->Dict[str, Any]:
        """Get minimal test data for POST endpoints"""
        test_data_map = {'/api/v1/auth/register': {'email':
            'test@example.com', 'password': 'testpass123'},
            '/api/v1/auth/login': {'email': 'test@example.com', 'password':
            'testpass123'}, '/api/v1/assessments': {'assessment_type':
            'compliance_readiness', 'company_name': 'Test Company'},
            '/api/v1/business-profiles': {'company_name': 'Test Company',
            'industry': 'Technology'}, '/api/v1/policies/generate': {
            'policy_type': 'privacy_policy', 'company_name': 'Test Company'
            }, '/api/v1/ai/assessments': {'assessment_type':
            'compliance_check', 'context': 'test'},
            '/api/v1/ai/policies/generate': {'policy_type':
            'privacy_policy', 'company_info': {'name': 'Test Company'}},
            '/api/v1/chat/messages': {'message': 'Hello, test message'},
            '/api/v1/compliance/check': {'framework_id': 'gdpr'}}
        return test_data_map.get(path, {})

    def _identify_issues(self, endpoints: List[APIEndpoint], actual_paths: set
        ) ->List[str]:
        """Identify issues with API endpoints"""
        issues = []
        missing_endpoints = [e for e in endpoints if not e.exists]
        if missing_endpoints:
            issues.append(f'Found {len(missing_endpoints)} missing endpoints')
            for endpoint in missing_endpoints:
                similar_paths = [p for p in actual_paths if endpoint.path.
                    split('/')[-1] in p]
                if similar_paths:
                    issues.append(
                        f'Endpoint {endpoint.path} not found, but similar paths exist: {similar_paths}'
                        )
        error_endpoints = [e for e in endpoints if e.exists and e.error and
            'Server error' in e.error]
        if error_endpoints:
            issues.append(
                f'Found {len(error_endpoints)} endpoints with server errors')
        slow_endpoints = [e for e in endpoints if e.response_time_ms and e.
            response_time_ms > 2000]
        if slow_endpoints:
            issues.append(
                f'Found {len(slow_endpoints)} slow endpoints (>2s response time)'
                )
        ai_endpoints = [e for e in endpoints if '/api/v1/ai/' in e.path and
            not e.exists]
        if ai_endpoints:
            issues.append(
                "AI endpoints using '/api/v1/ai/' prefix are not found - likely mounted at '/api/v1/ai-*' instead"
                )
        return issues

    def _generate_recommendations(self, endpoints: List[APIEndpoint],
        router_mapping: Dict[str, List[str]]) ->List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        missing_endpoints = [e for e in endpoints if not e.exists]
        if missing_endpoints:
            recommendations.append(
                'Check api/main.py router mounting - some endpoints may be mounted with different prefixes'
                )
            ai_missing = [e for e in missing_endpoints if '/api/v1/ai/' in
                e.path]
            if ai_missing:
                recommendations.append(
                    "AI endpoints: Update frontend to use '/api/v1/ai-assessments' instead of '/api/v1/ai-assessments'"
                    )
                recommendations.append(
                    'AI endpoints: Update frontend to use appropriate AI router prefixes as defined in main.py'
                    )
        auth_errors = [e for e in endpoints if e.exists and e.error and (
            '401' in e.error or '403' in e.error)]
        if auth_errors:
            recommendations.append(
                'Some endpoints require authentication - ensure test suite includes valid JWT tokens'
                )
        validation_errors = [e for e in endpoints if e.exists and e.error and
            '422' in e.error]
        if validation_errors:
            recommendations.append(
                'Some endpoints have validation errors - check request schemas and required fields'
                )
            recommendations.append(
                'Consider adding Pydantic model validation to ensure proper request format'
                )
        slow_endpoints = [e for e in endpoints if e.response_time_ms and e.
            response_time_ms > MAX_ITEMS]
        if slow_endpoints:
            recommendations.append(
                'Consider adding caching or database query optimization for slow endpoints'
                )
        if len(router_mapping) > 15:
            recommendations.append(
                'Consider consolidating related routers to reduce complexity')
        return recommendations

def print_analysis_report(result: APIAnalysisResult) ->None:
    """Print a comprehensive analysis report"""
    logger.info('\n' + '=' * 80)
    logger.info('🚀 ruleIQ API ROUTE ANALYSIS REPORT')
    logger.info('=' * 80)
    logger.info('\n📊 SUMMARY:')
    logger.info('   Total endpoints tested: %s' % result.total_endpoints)
    logger.info('   ✅ Working endpoints: %s' % result.working_endpoints)
    logger.info('   ❌ Missing endpoints: %s' % result.missing_endpoints)
    logger.info('   ⚠️  Error endpoints: %s' % result.error_endpoints)
    if result.total_endpoints > 0:
        success_rate = result.working_endpoints / result.total_endpoints * 100
        logger.info('   📈 Success rate: %s%' % success_rate)
    logger.info('\n🗂️  ROUTER BREAKDOWN:')
    for router, endpoints in result.router_mapping.items():
        working_count = len([e for e in result.endpoints if e.router ==
            router and e.exists and not e.error])
        total_count = len([e for e in result.endpoints if e.router == router])
        logger.info('   %s: %s/%s working' % (router, working_count,
            total_count))
    if result.issues_found:
        logger.info('\n🚨 ISSUES FOUND:')
        for i, issue in enumerate(result.issues_found, 1):
            logger.info('   %s. %s' % (i, issue))
    if result.recommendations:
        logger.info('\n💡 RECOMMENDATIONS:')
        for i, rec in enumerate(result.recommendations, 1):
            logger.info('   %s. %s' % (i, rec))
    logger.info('\n📋 DETAILED ENDPOINT STATUS:')
    working = [e for e in result.endpoints if e.exists and not e.error]
    missing = [e for e in result.endpoints if not e.exists]
    errors = [e for e in result.endpoints if e.exists and e.error]
    if working:
        logger.info('\n✅ WORKING ENDPOINTS (%s):' % len(working))
        for endpoint in working:
            response_time = (f' ({endpoint.response_time_ms:.0f}ms)' if
                endpoint.response_time_ms else '')
            logger.info('   %s %s%s' % (endpoint.method, endpoint.path,
                response_time))
    if missing:
        logger.info('\n❌ MISSING ENDPOINTS (%s):' % len(missing))
        for endpoint in missing:
            logger.info('   %s %s (router: %s)' % (endpoint.method,
                endpoint.path, endpoint.router))
    if errors:
        logger.info('\n⚠️  ERROR ENDPOINTS (%s):' % len(errors))
        for endpoint in errors:
            logger.info('   %s %s - %s' % (endpoint.method, endpoint.path,
                endpoint.error))
    logger.info('\n' + '=' * 80)

async def main() ->None:
    """Main analysis function"""
    logger.info('🔧 ruleIQ API Route Analyzer')
    logger.info('Analyzing API endpoints and identifying issues...')
    analyzer = APIRouteAnalyzer()
    result = await analyzer.analyze_routes()
    print_analysis_report(result)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'api_analysis_{timestamp}.json'
    result_dict = {'timestamp': datetime.now().isoformat(), 'summary': {
        'total_endpoints': result.total_endpoints, 'working_endpoints':
        result.working_endpoints, 'missing_endpoints': result.
        missing_endpoints, 'error_endpoints': result.error_endpoints},
        'endpoints': [{'path': e.path, 'method': e.method, 'router': e.
        router, 'exists': e.exists, 'status_code': e.status_code,
        'response_time_ms': e.response_time_ms, 'error': e.error} for e in
        result.endpoints], 'router_mapping': result.router_mapping,
        'issues_found': result.issues_found, 'recommendations': result.
        recommendations}
    try:
        with open(filename, 'w') as f:
            json.dump(result_dict, f, indent=2)
        logger.info('\n💾 Analysis results saved to %s' % filename)
    except Exception as e:
        logger.info('\n⚠️  Could not save results: %s' % e)

if __name__ == '__main__':
    asyncio.run(main())
