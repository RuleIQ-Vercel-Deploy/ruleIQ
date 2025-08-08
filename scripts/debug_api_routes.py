#!/usr/bin/env python3
"""
Debug API routes to identify exact issues
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint_with_details(method, endpoint, data=None, headers=None, description=""):
    """Test endpoint and provide detailed info"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        status_code = response.status_code
        status_symbol = "✅" if status_code < 400 else "❌"
        
        print(f"\n{status_symbol} {method} {endpoint}")
        print(f"    Status: {status_code}")
        print(f"    Description: {description}")
        
        if status_code >= 400:
            print(f"    Error Response:")
            try:
                error_json = response.json()
                print(f"      {json.dumps(error_json, indent=6)}")
            except:
                print(f"      Raw: {response.text[:200]}")
        else:
            print(f"    Success Response Preview:")
            try:
                success_json = response.json()
                if isinstance(success_json, dict):
                    for key, value in list(success_json.items())[:3]:
                        print(f"      {key}: {value}")
                    if len(success_json) > 3:
                        print(f"      ... ({len(success_json)} total keys)")
                else:
                    print(f"      {str(success_json)[:100]}")
            except:
                print(f"      Raw: {response.text[:100]}")
        
        return status_code < 400, response
        
    except Exception as e:
        print(f"\n❌ {method} {endpoint}")
        print(f"    ERROR: {e}")
        return False, None

def main():
    print("🔍 Debugging API Routes - Detailed Analysis")
    print("=" * 60)
    
    # Test basic health endpoints
    print("\n🏥 Health Check Analysis:")
    test_endpoint_with_details("GET", "/health", description="Basic health (should work)")
    test_endpoint_with_details("GET", "/api/v1/health", description="API v1 health (previously failing)")
    test_endpoint_with_details("GET", "/api/v1/health/detailed", description="Detailed health")
    
    # Test specific auth endpoint that we know should work
    print("\n🔐 Authentication Endpoint Analysis:")
    
    # First let's try to get a working user token
    register_data = {
        "email": f"api-debug-{int(time.time())}@test.com",
        "password": "TestPassword123!"
    }
    
    success, response = test_endpoint_with_details("POST", "/api/v1/auth/register", register_data, description="New user registration")
    
    if not success:
        # Try login instead
        login_data = {
            "email": "test-api-connection-1754520948@debugtest.com", 
            "password": "TestPassword123@"
        }
        success, response = test_endpoint_with_details("POST", "/api/v1/auth/login", login_data, description="Existing user login")
    
    if success and response:
        try:
            token_data = response.json()
            token = None
            
            # Handle both token response formats
            if 'tokens' in token_data and 'access_token' in token_data['tokens']:
                token = token_data['tokens']['access_token']
                print("    ✅ Token found in 'tokens.access_token' format")
            elif 'access_token' in token_data:
                token = token_data['access_token']
                print("    ✅ Token found in 'access_token' format")
            else:
                print("    ❌ No token found in response")
            
            if token:
                auth_headers = {"Authorization": f"Bearer {token}"}
                
                print("\n📋 Business Endpoints Analysis (403 errors expected if RBAC not fixed):")
                test_endpoint_with_details("GET", "/api/v1/business-profiles/", headers=auth_headers, description="Business profiles")
                test_endpoint_with_details("GET", "/api/v1/assessments/", headers=auth_headers, description="Assessments")
                test_endpoint_with_details("GET", "/api/v1/frameworks/", headers=auth_headers, description="Frameworks")
                
                print("\n🤖 AI Endpoints Analysis (404 errors expected if router issues remain):")
                test_endpoint_with_details("GET", "/api/v1/ai/policies", headers=auth_headers, description="AI policies")
                test_endpoint_with_details("GET", "/api/v1/ai/cost", headers=auth_headers, description="AI cost monitoring")
                
                print("\n💬 Chat & Freemium Analysis:")
                test_endpoint_with_details("GET", "/api/v1/chat/", headers=auth_headers, description="Chat endpoint")
                test_endpoint_with_details("POST", "/api/v1/freemium/capture-lead", {"email": "test@example.com", "consent": True}, description="Freemium endpoint")
                
        except Exception as e:
            print(f"    ❌ Could not process auth response: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Debug Analysis Complete")
if __name__ == "__main__":
    main()