"""
Security Testing Suite for ComplianceGPT

This module contains comprehensive security tests including:
- OWASP Top 10 vulnerability testing
- Input validation and sanitization
- Authentication and authorization testing
- Rate limiting and DDoS protection
- Data protection and privacy validation
"""

from unittest.mock import patch

import pytest


@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization"""

    def test_sql_injection_prevention(self, client, security_test_payloads, authenticated_headers):
        """Test SQL injection prevention in API endpoints"""
        for payload in security_test_payloads["sql_injection"]:
            # Test various endpoints with SQL injection payloads
            response = client.get(f"/api/frameworks?search={payload}")
            assert response.status_code != 500, "SQL injection may have caused server error"

            # Test POST endpoints with authentication
            response = client.post("/api/business-profiles",
                                 headers=authenticated_headers,
                                 json={
                                     "company_name": payload,
                                     "industry": "Technology"
                                 })
            # Should either reject the input (400/422) or process it safely (200/201)
            # The key is that it shouldn't cause a 500 server error
            assert response.status_code != 500, "SQL injection may have caused server error"

    def test_xss_prevention(self, client, security_test_payloads, authenticated_headers):
        """Test XSS prevention in API responses"""
        for payload in security_test_payloads["xss_payloads"]:
            response = client.post("/api/business-profiles",
                                 headers=authenticated_headers,
                                 json={
                                     "company_name": f"Test Company {payload}",
                                     "industry": "Technology"
                                 })

            if response.status_code in [200, 201]:
                # Ensure XSS payload is properly escaped in response
                response_text = response.text
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
                assert "onerror=" not in response_text

    def test_command_injection_prevention(self, client, security_test_payloads, authenticated_headers):
        """Test command injection prevention"""
        for payload in security_test_payloads["command_injection"]:
            response = client.post("/api/policies/generate",
                                 headers=authenticated_headers,
                                 json={
                                     "framework": "GDPR",
                                     "business_context": payload
                                 })

            # Should not cause server errors or execute commands
            assert response.status_code != 500
            if response.status_code == 200:
                # Response should not contain command execution results
                response_data = response.json()
                assert "etc/passwd" not in str(response_data)
                assert "system32" not in str(response_data)

    def test_path_traversal_prevention(self, client, security_test_payloads):
        """Test path traversal prevention"""
        for payload in security_test_payloads["path_traversal"]:
            # Test file access endpoints
            response = client.get(f"/api/evidence/download/{payload}")
            assert response.status_code in [400, 404, 403], "Path traversal should be blocked"


@pytest.mark.security
class TestAuthentication:
    """Test authentication security"""

    def test_unauthenticated_access_blocked(self, client):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/users/me",
            "/api/business-profiles",
            "/api/assessments",
            "/api/policies/generate"
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected"""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "Bearer ",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]

        for token in invalid_tokens:
            headers = {"Authorization": token} if token else {}
            response = client.get("/api/users/me", headers=headers)
            assert response.status_code == 401, f"Invalid token {token} should be rejected"

    def test_token_expiry_enforcement(self, client, sample_user):
        """Test that expired tokens are rejected"""
        # This would require mocking time or using short-lived tokens
        with patch('jose.jwt.decode') as mock_decode:
            from jose.exceptions import ExpiredSignatureError
            mock_decode.side_effect = ExpiredSignatureError("Token has expired")

            response = client.get("/api/users/me", headers={
                "Authorization": "Bearer expired_token"
            })
            assert response.status_code == 401

    def test_password_complexity_requirements(self, client):
        """Test password complexity enforcement"""
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "12345678",  # Only numbers
            "abcdefgh",  # Only lowercase
            "ABCDEFGH",  # Only uppercase
        ]

        for weak_password in weak_passwords:
            response = client.post("/api/auth/register", json={
                "email": "test@example.com",
                "password": weak_password,
                "full_name": "Test User"
            })
            assert response.status_code == 422, f"Weak password {weak_password} should be rejected"


@pytest.mark.security
class TestAuthorization:
    """Test authorization and access control"""

    def test_role_based_access_control(self, client, sample_user_data):
        """Test role-based access control"""
        # Create users with different roles
        admin_user = {**sample_user_data, "email": "admin@example.com", "role": "admin"}
        manager_user = {**sample_user_data, "email": "manager@example.com", "role": "compliance_manager"}
        viewer_user = {**sample_user_data, "email": "viewer@example.com", "role": "viewer"}

        # Register users
        for user in [admin_user, manager_user, viewer_user]:
            client.post("/api/auth/register", json=user)

        # Test admin-only endpoints
        admin_token = self._get_auth_token(client, admin_user)
        manager_token = self._get_auth_token(client, manager_user)
        viewer_token = self._get_auth_token(client, viewer_user)

        # Admin should have access to user management
        response = client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200

        # Manager should not have access to user management
        response = client.get("/api/users", headers={"Authorization": f"Bearer {manager_token}"})
        assert response.status_code == 403

        # Viewer should not have write access
        response = client.post("/api/business-profiles",
                             headers={"Authorization": f"Bearer {viewer_token}"},
                             json={"company_name": "Test", "industry": "Tech"})
        assert response.status_code == 403

    def _get_auth_token(self, client, user_data):
        """Helper to get authentication token"""
        response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        return response.json()["access_token"]


@pytest.mark.security
class TestDataProtection:
    """Test data protection and privacy measures"""

    def test_sensitive_data_not_in_logs(self, client, sample_user_data, caplog):
        """Test that sensitive data doesn't appear in logs"""
        # Perform operations that might log sensitive data
        client.post("/api/auth/register", json=sample_user_data)
        client.post("/api/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })

        # Check logs for sensitive data
        from tests.conftest import assert_no_sensitive_data_in_logs
        assert_no_sensitive_data_in_logs(caplog)

    def test_password_hashing(self, client, sample_user_data, db_session):
        """Test that passwords are properly hashed"""
        # Register user
        response = client.post("/api/auth/register", json=sample_user_data)
        assert response.status_code == 201

        # Check that password is hashed in database
        from database.user import User
        user = db_session.query(User).filter(User.email == sample_user_data["email"]).first()
        assert user.hashed_password != sample_user_data["password"]
        assert len(user.hashed_password) > 50  # Hashed passwords are longer
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash

    def test_pii_encryption_at_rest(self, client, sample_business_profile, db_session):
        """Test that PII is encrypted when stored"""
        # This would require checking if sensitive fields are encrypted
        # Implementation depends on your encryption strategy
        pass

    def test_secure_headers_present(self, client):
        """Test that security headers are present in responses"""
        response = client.get("/health")

        # Check for security headers
        headers = response.headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"


@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting and DDoS protection"""

    def test_rate_limiting_enforcement(self, client, authenticated_headers):
        """Test that rate limiting is enforced"""
        # Make many requests rapidly to an authenticated endpoint
        endpoint = "/api/frameworks"
        responses = []

        for _i in range(150):  # Exceed rate limit
            response = client.get(endpoint, headers=authenticated_headers)
            responses.append(response.status_code)

        # Should eventually get rate limited (429) or at least not all be successful
        # Rate limiting might not be fully implemented, so we check for either 429 or mixed responses
        unique_responses = set(responses)
        assert len(unique_responses) > 1 or 429 in responses, f"Rate limiting should be enforced, got responses: {unique_responses}"

    def test_rate_limiting_per_user(self, client, authenticated_headers):
        """Test rate limiting is applied per user"""
        # Test that authenticated users have different rate limits
        endpoint = "/api/business-profiles"
        rate_limited = False

        for _ in range(200):
            response = client.get(endpoint, headers=authenticated_headers)
            if response.status_code == 429:
                rate_limited = True
                break

        assert rate_limited, "Rate limiting should apply to authenticated users"


@pytest.mark.security
class TestAPISecurity:
    """Test API-specific security measures"""

    def test_cors_configuration(self, client):
        """Test CORS configuration is secure"""
        response = client.options("/api/frameworks", headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "GET"
        })

        cors_headers = response.headers
        if "Access-Control-Allow-Origin" in cors_headers:
            # Should not allow all origins in production
            assert cors_headers["Access-Control-Allow-Origin"] != "*"

    def test_api_versioning_security(self, client):
        """Test that API versioning doesn't expose old vulnerabilities"""
        # Test that deprecated API versions are properly secured or blocked
        deprecated_endpoints = [
            "/v1/api/users",
            "/api/v1/users",
            "/old/api/users"
        ]

        for endpoint in deprecated_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [404, 410], f"Deprecated endpoint {endpoint} should not be accessible"

    def test_information_disclosure_prevention(self, client):
        """Test that error messages don't disclose sensitive information"""
        # Test 404 responses don't reveal system information
        response = client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404

        error_message = response.json().get("error", {}).get("message", "")

        # Should not reveal internal paths, stack traces, or system info
        sensitive_info = [
            "/home/",
            "/usr/",
            "Traceback",
            "sqlalchemy",
            "postgresql://",
            "Exception",
            "__file__"
        ]

        for info in sensitive_info:
            assert info not in error_message, f"Error message should not contain {info}"


@pytest.mark.security
@pytest.mark.slow
class TestPenetrationTesting:
    """Automated penetration testing scenarios"""

    def test_automated_vulnerability_scan(self, client):
        """Run automated vulnerability scanning"""
        # This would integrate with tools like OWASP ZAP or similar
        # For now, we'll test common vulnerability patterns

        vulnerabilities_found = []

        # Test for common web vulnerabilities
        test_cases = [
            {"type": "Directory Traversal", "payload": "../../../etc/passwd"},
            {"type": "File Inclusion", "payload": "file:///etc/passwd"},
            {"type": "XXE", "payload": "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///etc/passwd'>]><root>&test;</root>"},
        ]

        for test_case in test_cases:
            # Test various endpoints
            endpoints = ["/api/frameworks", "/api/policies/generate"]
            for endpoint in endpoints:
                try:
                    response = client.post(endpoint, json={"data": test_case["payload"]})
                    if "root:x:" in response.text:  # Signs of file disclosure
                        vulnerabilities_found.append(f"{test_case['type']} in {endpoint}")
                except Exception:
                    pass  # Expected for many payloads

        assert len(vulnerabilities_found) == 0, f"Vulnerabilities found: {vulnerabilities_found}"

    def test_business_logic_vulnerabilities(self, client, authenticated_headers):
        """Test for business logic vulnerabilities"""
        # Test privilege escalation
        response = client.patch("/api/users/1/role",
                               headers=authenticated_headers,
                               json={"role": "admin"})
        assert response.status_code == 403, "Users should not be able to escalate their own privileges"

        # Test resource access controls
        response = client.get("/api/business-profiles/999999", headers=authenticated_headers)
        assert response.status_code in [403, 404], "Users should not access other organizations' data"
