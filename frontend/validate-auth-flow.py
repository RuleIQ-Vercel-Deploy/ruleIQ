#!/usr/bin/env python3
"""
Simple validation script to test the authentication flow end-to-end
before running TestSprite.
"""

import requests
import json
import time

def test_frontend_csrf():
    """Test CSRF token endpoint"""
    print("🔐 Testing CSRF token endpoint...")
    try:
        response = requests.get('http://localhost:3000/api/csrf-token', timeout=10)
        if response.status_code == 200:
            print("✅ CSRF token endpoint working")
            return True
        else:
            print(f"❌ CSRF endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CSRF endpoint error: {e}")
        return False

def test_backend_auth():
    """Test backend authentication"""
    print("🔐 Testing backend authentication...")
    try:
        # Test login
        login_data = {
            'username': 'test@example.com',
            'password': 'testpassword123'
        }
        response = requests.post(
            'http://localhost:8000/api/v1/auth/token',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print("✅ Backend login successful")
            
            # Test /me endpoint
            me_response = requests.get(
                'http://localhost:8000/api/v1/auth/me',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ User data retrieved: {user_data.get('email')}")
                return True
            else:
                print(f"❌ /me endpoint failed: {me_response.status_code}")
                return False
        else:
            print(f"❌ Backend login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend auth error: {e}")
        return False

def test_page_loads():
    """Test that key pages load"""
    print("📱 Testing page loads...")
    pages = [
        ('http://localhost:3000/', 'Home page'),
        ('http://localhost:3000/login', 'Login page'),
        ('http://localhost:3000/register', 'Register page')
    ]
    
    all_passed = True
    for url, name in pages:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} loads successfully")
            else:
                print(f"❌ {name} failed: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} error: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all validation tests"""
    print("🚀 Starting authentication flow validation...\n")
    
    results = []
    
    # Test frontend endpoints
    results.append(test_frontend_csrf())
    print()
    
    # Test backend authentication
    results.append(test_backend_auth())
    print()
    
    # Test page loads
    results.append(test_page_loads())
    print()
    
    # Summary
    if all(results):
        print("🎉 All validation tests PASSED! ✅")
        print("✅ Ready for TestSprite execution")
        return 0
    else:
        print("❌ Some validation tests FAILED!")
        print("🔧 Please fix issues before running TestSprite")
        return 1

if __name__ == '__main__':
    exit(main())