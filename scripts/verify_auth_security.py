#!/usr/bin/env python3
"""
Security Verification Script for Authentication Middleware

This script performs comprehensive security testing to ensure:
1. No authentication bypass vulnerabilities exist
2. All protected routes require valid JWT tokens
3. Public routes remain accessible
4. Rate limiting is functional
5. Token validation is properly implemented

Run this script after any authentication changes to verify security.
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import httpx
import jwt
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000"
SECRET_KEY = None  # Will be loaded from environment
ALGORITHM = "HS256"

# Test results tracking
test_results = []
vulnerabilities_found = []


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result with color coding."""
    status = f"{Fore.GREEN}✓ PASS" if passed else f"{Fore.RED}✗ FAIL"
    print(f"{status}{Style.RESET_ALL} - {test_name}")
    if details:
        print(f"  {Fore.YELLOW}→ {details}{Style.RESET_ALL}")
    
    test_results.append({
        'test': test_name,
        'passed': passed,
        'details': details
    })
    
    if not passed:
        vulnerabilities_found.append({
            'test': test_name,
            'details': details
        })


def create_token(payload: Dict[str, Any], secret: str = None) -> str:
    """Create a JWT token for testing."""
    if secret is None:
        secret = SECRET_KEY or "test-secret-key"
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


async def test_public_endpoints(client: httpx.AsyncClient) -> List[Tuple[str, bool]]:
    """Test that public endpoints are accessible without authentication."""
    print_header("Testing Public Endpoints")
    
    public_endpoints = [
        "/",
        "/health",
        "/api/v1/health",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/docs",
        "/openapi.json"
    ]
    
    results = []
    for endpoint in public_endpoints:
        try:
            response = await client.get(endpoint)
            # Public endpoints should not return 401
            passed = response.status_code != 401
            print_test(
                f"Public endpoint {endpoint}",
                passed,
                f"Status: {response.status_code}"
            )
            results.append((endpoint, passed))
        except Exception as e:
            print_test(
                f"Public endpoint {endpoint}",
                False,
                f"Error: {str(e)}"
            )
            results.append((endpoint, False))
    
    return results


async def test_protected_endpoints_without_auth(client: httpx.AsyncClient) -> List[Tuple[str, bool]]:
    """Test that protected endpoints require authentication."""
    print_header("Testing Protected Endpoints (No Auth)")
    
    protected_endpoints = [
        "/api/v1/users/profile",
        "/api/v1/admin/settings",
        "/api/v1/assessments",
        "/api/v1/policies",
        "/api/v1/payments/process",
        "/api/v1/dashboard",
        "/api/v1/monitoring/metrics",
        "/api/v1/security/audit",
        "/api/dashboard"
    ]
    
    results = []
    for endpoint in protected_endpoints:
        try:
            response = await client.get(endpoint)
            # Protected endpoints MUST return 401 without auth
            passed = response.status_code == 401
            print_test(
                f"Protected endpoint {endpoint} blocks unauthenticated access",
                passed,
                f"Status: {response.status_code} (Expected: 401)"
            )
            
            if not passed:
                vulnerabilities_found.append({
                    'severity': 'CRITICAL',
                    'endpoint': endpoint,
                    'issue': f'Endpoint accessible without authentication (Status: {response.status_code})'
                })
            
            results.append((endpoint, passed))
        except Exception as e:
            print_test(
                f"Protected endpoint {endpoint}",
                False,
                f"Error: {str(e)}"
            )
            results.append((endpoint, False))
    
    return results


async def test_bypass_attempts(client: httpx.AsyncClient) -> List[Tuple[str, bool]]:
    """Test various authentication bypass attempts."""
    print_header("Testing Authentication Bypass Attempts")
    
    test_endpoint = "/api/v1/users/profile"
    results = []
    
    # Test 1: Empty Bearer token
    response = await client.get(test_endpoint, headers={"Authorization": "Bearer"})
    passed = response.status_code == 401
    print_test(
        "Empty Bearer token rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("empty_bearer", passed))
    
    # Test 2: Space-only Bearer token
    response = await client.get(test_endpoint, headers={"Authorization": "Bearer "})
    passed = response.status_code == 401
    print_test(
        "Space-only Bearer token rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("space_bearer", passed))
    
    # Test 3: Wrong auth scheme
    response = await client.get(test_endpoint, headers={"Authorization": "Basic dGVzdDp0ZXN0"})
    passed = response.status_code == 401
    print_test(
        "Basic auth instead of Bearer rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("basic_auth", passed))
    
    # Test 4: Malformed token
    response = await client.get(test_endpoint, headers={"Authorization": "Bearer malformed.token.here"})
    passed = response.status_code == 401
    print_test(
        "Malformed JWT token rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("malformed_token", passed))
    
    # Test 5: URL manipulation
    bypass_urls = [
        "/api/v1/users/../auth/login",
        "/api/v1//users/profile",
        "/api/v1/users/profile?auth=bypass",
        "/api/v1/users/profile#authenticated"
    ]
    
    for bypass_url in bypass_urls:
        response = await client.get(bypass_url)
        passed = response.status_code in [401, 404]  # Should be blocked or not found
        print_test(
            f"URL manipulation blocked: {bypass_url}",
            passed,
            f"Status: {response.status_code}"
        )
        results.append((f"url_{bypass_url}", passed))
    
    # Test 6: Method override headers
    override_headers = [
        {"X-HTTP-Method-Override": "OPTIONS"},
        {"X-Original-Method": "GET"},
        {"X-Forwarded-Host": "trusted.internal"},
    ]
    
    for headers in override_headers:
        response = await client.get(test_endpoint, headers=headers)
        passed = response.status_code == 401
        print_test(
            f"Header override blocked: {list(headers.keys())[0]}",
            passed,
            f"Status: {response.status_code}"
        )
        results.append((f"header_{list(headers.keys())[0]}", passed))
    
    return results


async def test_token_validation(client: httpx.AsyncClient) -> List[Tuple[str, bool]]:
    """Test JWT token validation."""
    print_header("Testing JWT Token Validation")
    
    test_endpoint = "/api/v1/users/profile"
    results = []
    
    # Test 1: Expired token
    expired_payload = {
        'sub': 'test-user',
        'type': 'access',
        'exp': datetime.now(timezone.utc) - timedelta(hours=1),
        'iat': datetime.now(timezone.utc) - timedelta(hours=2)
    }
    expired_token = create_token(expired_payload)
    response = await client.get(test_endpoint, headers={"Authorization": f"Bearer {expired_token}"})
    passed = response.status_code == 401
    print_test(
        "Expired token rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("expired_token", passed))
    
    # Test 2: Wrong token type (refresh instead of access)
    refresh_payload = {
        'sub': 'test-user',
        'type': 'refresh',
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
        'iat': datetime.now(timezone.utc)
    }
    refresh_token = create_token(refresh_payload)
    response = await client.get(test_endpoint, headers={"Authorization": f"Bearer {refresh_token}"})
    passed = response.status_code == 401
    print_test(
        "Refresh token rejected for access endpoint",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("wrong_token_type", passed))
    
    # Test 3: Token with wrong signature
    wrong_secret_payload = {
        'sub': 'test-user',
        'type': 'access',
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc)
    }
    wrong_secret_token = create_token(wrong_secret_payload, secret="wrong-secret")
    response = await client.get(test_endpoint, headers={"Authorization": f"Bearer {wrong_secret_token}"})
    passed = response.status_code == 401
    print_test(
        "Token with wrong signature rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("wrong_signature", passed))
    
    # Test 4: Token missing required claims
    incomplete_payload = {
        'sub': 'test-user',
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        # Missing 'type' claim
    }
    incomplete_token = create_token(incomplete_payload)
    response = await client.get(test_endpoint, headers={"Authorization": f"Bearer {incomplete_token}"})
    passed = response.status_code == 401
    print_test(
        "Token missing required claims rejected",
        passed,
        f"Status: {response.status_code}"
    )
    results.append(("incomplete_token", passed))
    
    return results


async def test_rate_limiting(client: httpx.AsyncClient) -> bool:
    """Test rate limiting on authentication endpoints."""
    print_header("Testing Rate Limiting")
    
    auth_endpoint = "/api/v1/auth/login"
    
    # Make rapid requests to trigger rate limiting
    start_time = time.time()
    responses = []
    
    # Make 10 rapid requests
    for i in range(10):
        response = await client.post(
            auth_endpoint,
            json={"username": "test", "password": "wrong"}
        )
        responses.append(response.status_code)
        
        # Small delay to avoid connection issues
        if i < 9:
            await asyncio.sleep(0.1)
    
    elapsed_time = time.time() - start_time
    
    # Check if any returned 429 (Too Many Requests)
    rate_limited = any(status == 429 for status in responses)
    
    print_test(
        "Rate limiting active on auth endpoints",
        rate_limited or elapsed_time > 5,  # Either rate limited or slowed down
        f"Made 10 requests in {elapsed_time:.2f}s, Status codes: {set(responses)}"
    )
    
    return rate_limited


async def main():
    """Run all security tests."""
    print(f"{Fore.BLUE}╔══════════════════════════════════════════════════════════╗")
    print(f"{Fore.BLUE}║      RuleIQ Authentication Security Verification        ║")
    print(f"{Fore.BLUE}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    # Load secret key from environment
    import os
    global SECRET_KEY
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Check if server is running
        try:
            response = await client.get("/health")
            print(f"{Fore.GREEN}✓ Server is running at {BASE_URL}{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.RED}✗ Server not accessible at {BASE_URL}")
            print(f"  Error: {e}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Please start the server with: uvicorn main:app --reload{Style.RESET_ALL}")
            return
        
        # Run all tests
        public_results = await test_public_endpoints(client)
        protected_results = await test_protected_endpoints_without_auth(client)
        bypass_results = await test_bypass_attempts(client)
        validation_results = await test_token_validation(client)
        rate_limit_result = await test_rate_limiting(client)
    
    # Print summary
    print_header("Security Verification Summary")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r['passed'])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"{Fore.GREEN}Passed: {passed_tests}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed_tests}{Style.RESET_ALL}")
    
    if vulnerabilities_found:
        print(f"\n{Fore.RED}⚠️  CRITICAL SECURITY ISSUES FOUND:{Style.RESET_ALL}")
        for vuln in vulnerabilities_found:
            if isinstance(vuln, dict) and 'severity' in vuln:
                print(f"  {Fore.RED}[{vuln['severity']}] {vuln['endpoint']}: {vuln['issue']}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.RED}• {vuln.get('test', 'Unknown')}: {vuln.get('details', 'No details')}{Style.RESET_ALL}")
        
        print(f"\n{Fore.RED}SECURITY STATUS: VULNERABLE{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Action Required: Fix authentication middleware immediately!{Style.RESET_ALL}")
        sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}✓ No critical security vulnerabilities detected{Style.RESET_ALL}")
        print(f"{Fore.GREEN}SECURITY STATUS: SECURE{Style.RESET_ALL}")
        
        # Performance metrics
        print(f"\n{Fore.CYAN}Performance Metrics:{Style.RESET_ALL}")
        print(f"  • All protected routes return 401 without auth: ✓")
        print(f"  • All public routes remain accessible: ✓")
        print(f"  • JWT validation working correctly: ✓")
        print(f"  • No authentication bypass vulnerabilities: ✓")
        if rate_limit_result:
            print(f"  • Rate limiting active: ✓")
        
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())