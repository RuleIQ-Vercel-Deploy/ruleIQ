"""
Test JWT Authentication Coverage

This test file validates that all critical API endpoints are properly protected
with JWT authentication, ensuring 100% coverage of sensitive routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import re
from typing import List, Dict, Any

# Import the middleware to test
from middleware.jwt_auth import JWTAuthMiddleware

class TestJWTAuthenticationCoverage:
    """Test suite for JWT authentication coverage validation."""
    
    @pytest.fixture
    def jwt_middleware(self):
        """Create a JWT middleware instance for testing."""
        return JWTAuthMiddleware(
            enable_strict_mode=True,
            enable_rate_limiting=True,
            enable_audit_logging=False  # Disable logging for tests
        )
    
    def test_all_critical_routes_protected(self, jwt_middleware):
        """Test that all critical routes are marked as protected."""
        critical_routes = [
            # User management
            '/api/v1/users/profile',
            '/api/v1/users/123/update',
            '/api/v1/users/settings',
            
            # Admin
            '/api/v1/admin/users',
            '/api/v1/admin/settings',
            
            # Business profiles
            '/api/v1/business-profiles/create',
            '/api/v1/business-profiles/123/update',
            
            # Assessments
            '/api/v1/assessments/start',
            '/api/v1/assessments/123/complete',
            '/api/v1/readiness/check',
            
            # Evidence
            '/api/v1/evidence/upload',
            '/api/v1/evidence/123/approve',
            '/api/v1/evidence-collection/start',
            '/api/v1/foundation/evidence/create',
            
            # Compliance
            '/api/v1/compliance/status',
            '/api/v1/frameworks/select',
            
            # Policies
            '/api/v1/policies/generate',
            '/api/v1/policies/123/approve',
            
            # Implementation
            '/api/v1/implementation/plans',
            '/api/v1/implementation/plans/123',
            
            # Reports
            '/api/v1/reports/generate',
            '/api/v1/reports/export',
            '/api/v1/audit-export/request',
            
            # Integrations
            '/api/v1/integrations/connect',
            '/api/v1/integrations/google/sync',
            
            # Payments
            '/api/v1/payments/process',
            '/api/v1/payments/subscription',
            
            # API Keys
            '/api/v1/api-keys/create',
            '/api/v1/api-keys/revoke',
            
            # Webhooks
            '/api/v1/webhooks/create',
            '/api/v1/webhooks/123/delete',
            
            # Secrets
            '/api/v1/secrets/vault/access',
            
            # AI endpoints
            '/api/v1/ai/generate',
            '/api/v1/ai/cost/track',
            '/api/v1/iq-agent/query',
            '/api/v1/agentic-rag/search',
            '/api/v1/chat/message',
            
            # Dashboard
            '/api/dashboard',
            '/api/v1/dashboard/widgets',
            
            # Monitoring
            '/api/v1/monitoring/metrics',
            '/api/v1/security/audit',
            '/api/v1/performance/stats',
            
            # UK Compliance
            '/api/v1/uk-compliance/gdpr',
            
            # Feedback
            '/api/v1/feedback/submit',
        ]
        
        for route in critical_routes:
            assert jwt_middleware.is_critical_path(route), f"Route {route} should be protected but isn't"
    
    def test_public_routes_not_protected(self, jwt_middleware):
        """Test that public routes are correctly identified as not requiring auth."""
        public_routes = [
            '/docs',
            '/docs/api',
            '/redoc',
            '/openapi.json',
            '/health',
            '/api/v1/health',
            '/api/v1/health/detailed',
            '/',
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/token',
            '/api/v1/auth/refresh',
            '/api/v1/auth/forgot-password',
            '/api/v1/auth/reset-password',
            '/api/v1/auth/google/login',
            '/api/v1/freemium/assessment',
            '/api/v1/ping',
        ]
        
        for route in public_routes:
            assert jwt_middleware.is_public_path(route), f"Route {route} should be public but isn't"
            assert not jwt_middleware.is_critical_path(route), f"Route {route} shouldn't be critical"
    
    def test_optional_auth_routes(self, jwt_middleware):
        """Test that optional auth routes are correctly identified."""
        optional_routes = [
            '/api/v1/frameworks/public/list',
            '/api/v1/policies/templates/view',
        ]
        
        for route in optional_routes:
            assert jwt_middleware.is_optional_auth_path(route), f"Route {route} should be optional auth"
    
    def test_coverage_percentage_calculation(self, jwt_middleware):
        """Test the authentication coverage percentage calculation."""
        # Simulate some requests
        jwt_middleware.auth_coverage_stats = {
            'total_requests': 100,
            'authenticated_requests': 85,
            'public_requests': 10,
            'failed_auth_requests': 5
        }
        
        report = jwt_middleware.get_auth_coverage_report()
        
        assert report['coverage_percentage'] == 85.0
        assert report['total_requests'] == 100
        assert report['authenticated_requests'] == 85
        assert report['public_requests'] == 10
        assert report['failed_auth_requests'] == 5
    
    def test_route_pattern_matching(self, jwt_middleware):
        """Test that route patterns correctly match various path formats."""
        test_cases = [
            # Should match protected patterns
            ('/api/v1/users/123/profile', True, False),
            ('/api/v1/evidence/456/download', True, False),
            ('/api/v1/ai/policy/generate', True, False),
            ('/api/v1/dashboard/overview', True, False),
            
            # Should match public patterns
            ('/docs/swagger', False, True),
            ('/api/v1/auth/login', False, True),
            ('/health', False, True),
            
            # Edge cases
            ('/api/v1/users', True, False),  # Base users endpoint (protected)
            ('/api/v1/auth/logout', True, False),  # Logout is not in public list
            ('/api/v2/users', False, False),  # v2 API not defined
        ]
        
        for path, should_be_critical, should_be_public in test_cases:
            is_critical = jwt_middleware.is_critical_path(path)
            is_public = jwt_middleware.is_public_path(path)
            
            assert is_critical == should_be_critical, \
                f"Path {path}: expected critical={should_be_critical}, got {is_critical}"
            assert is_public == should_be_public, \
                f"Path {path}: expected public={should_be_public}, got {is_public}"
    
    def test_all_endpoints_categorized(self, jwt_middleware):
        """Test that common endpoint patterns are either public or protected."""
        common_endpoints = [
            '/api/v1/users/list',
            '/api/v1/assessments/create',
            '/api/v1/evidence/upload',
            '/api/v1/compliance/check',
            '/api/v1/policies/generate',
            '/api/v1/reports/export',
            '/api/v1/auth/login',
            '/health',
            '/docs',
        ]
        
        for endpoint in common_endpoints:
            is_public = jwt_middleware.is_public_path(endpoint)
            is_protected = jwt_middleware.is_critical_path(endpoint)
            is_optional = jwt_middleware.is_optional_auth_path(endpoint)
            
            # Each endpoint should be in at least one category
            assert is_public or is_protected or is_optional, \
                f"Endpoint {endpoint} is not categorized (neither public, protected, nor optional)"
    
    @pytest.mark.asyncio
    async def test_middleware_blocks_unauthenticated_critical_routes(self, jwt_middleware):
        """Test that the middleware blocks unauthenticated access to critical routes."""
        from fastapi import Request
        from fastapi.responses import JSONResponse
        
        # Mock request without auth header
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = '/api/v1/users/profile'
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = '127.0.0.1'
        mock_request.method = 'GET'
        
        # Mock call_next
        async def mock_call_next(request):
            return JSONResponse(content={'data': 'test'})
        
        # Call middleware
        response = await jwt_middleware(mock_request, mock_call_next)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert 'Authentication required' in str(response.body)
    
    @pytest.mark.asyncio
    async def test_middleware_allows_public_routes(self, jwt_middleware):
        """Test that the middleware allows access to public routes without auth."""
        from fastapi import Request
        from fastapi.responses import JSONResponse
        
        # Mock request to public endpoint
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = '/health'
        mock_request.headers = {}
        mock_request.client = None
        
        # Mock call_next
        async def mock_call_next(request):
            return JSONResponse(content={'status': 'healthy'}, status_code=200)
        
        # Call middleware
        response = await jwt_middleware(mock_request, mock_call_next)
        
        # Should allow through
        assert response.status_code == 200
    
    def test_authentication_coverage_complete(self, jwt_middleware):
        """Comprehensive test to ensure 100% coverage of critical endpoints."""
        # List of all critical endpoint categories
        critical_categories = {
            'user_management': ['/api/v1/users/', '/api/v1/admin/'],
            'business_data': ['/api/v1/business-profiles/', '/api/v1/assessments/'],
            'compliance_data': ['/api/v1/evidence/', '/api/v1/compliance/', '/api/v1/policies/'],
            'financial': ['/api/v1/payments/'],
            'security': ['/api/v1/api-keys/', '/api/v1/webhooks/', '/api/v1/secrets/'],
            'ai_services': ['/api/v1/ai/', '/api/v1/iq-agent/', '/api/v1/chat/'],
            'reporting': ['/api/v1/reports/', '/api/v1/audit-export/'],
            'monitoring': ['/api/v1/monitoring/', '/api/v1/security/', '/api/v1/performance/'],
            'integrations': ['/api/v1/integrations/'],
            'dashboard': ['/api/v1/dashboard/', '/api/dashboard'],
        }
        
        total_categories = len(critical_categories)
        protected_categories = 0
        
        for category, endpoints in critical_categories.items():
            category_protected = all(
                jwt_middleware.is_critical_path(endpoint + 'test')
                for endpoint in endpoints
            )
            if category_protected:
                protected_categories += 1
            else:
                unprotected = [e for e in endpoints if not jwt_middleware.is_critical_path(e + 'test')]
                pytest.fail(f"Category '{category}' has unprotected endpoints: {unprotected}")
        
        coverage_percentage = (protected_categories / total_categories) * 100
        assert coverage_percentage == 100.0, f"Only {coverage_percentage}% of critical categories are protected"
        
        print(f"✅ Authentication Coverage: {coverage_percentage}% - All critical endpoints are protected!")


if __name__ == "__main__":
    # Run tests with coverage report
    pytest.main([__file__, '-v', '--tb=short'])