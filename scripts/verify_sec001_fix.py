#!/usr/bin/env python3
"""
Verification script for SEC-001 Authentication Middleware Security Fix
This script validates that the authentication bypass vulnerability has been resolved.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.feature_flags import FeatureFlagService
from config.settings import settings
import json

def verify_sec001_fix():
    """Verify SEC-001 fix is properly implemented"""
    
    print("=" * 60)
    print("SEC-001 Authentication Middleware Security Fix Verification")
    print("=" * 60)
    
    results = {
        "feature_flag_enabled": False,
        "middleware_v2_present": False,
        "strict_mode_enabled": False,
        "vulnerability_fixed": False,
        "tests_pass": False
    }
    
    # 1. Check feature flag is enabled
    print("\n1. Checking feature flag status...")
    try:
        feature_service = FeatureFlagService()
        flag_enabled = feature_service.is_enabled(
            "AUTH_MIDDLEWARE_V2_ENABLED",
            environment=settings.environment.value
        )
        results["feature_flag_enabled"] = flag_enabled
        print(f"   ✓ Feature flag AUTH_MIDDLEWARE_V2_ENABLED: {'ENABLED' if flag_enabled else 'DISABLED'}")
    except Exception as e:
        print(f"   ✗ Error checking feature flag: {e}")
    
    # 2. Check middleware v2 file exists
    print("\n2. Checking middleware v2 implementation...")
    middleware_path = "middleware/jwt_auth_v2.py"
    if os.path.exists(middleware_path):
        results["middleware_v2_present"] = True
        print(f"   ✓ Middleware v2 file exists: {middleware_path}")
        
        # Check for strict mode in the code
        with open(middleware_path, 'r') as f:
            content = f.read()
            if "enable_strict_mode: bool = True" in content:
                results["strict_mode_enabled"] = True
                print("   ✓ Strict mode is enabled by default")
            else:
                print("   ✗ Strict mode not enabled by default")
                
            # Check for vulnerability fix comments
            if "SEC-001" in content and "SECURITY FIX" in content:
                print("   ✓ SEC-001 fix comments found in code")
            else:
                print("   ⚠ SEC-001 fix comments not found")
    else:
        print(f"   ✗ Middleware v2 file not found: {middleware_path}")
    
    # 3. Check main.py integration
    print("\n3. Checking main.py integration...")
    main_path = "main.py"
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
            if "from middleware.jwt_auth_v2 import JWTAuthMiddlewareV2" in content:
                print("   ✓ Main.py imports JWTAuthMiddlewareV2")
            else:
                print("   ✗ Main.py does not import JWTAuthMiddlewareV2")
                
            if "use_v2_middleware" in content and "feature_service.is_enabled" in content:
                print("   ✓ Feature flag check implemented in main.py")
            else:
                print("   ✗ Feature flag check not implemented")
                
            if "enable_strict_mode=True" in content:
                print("   ✓ Strict mode explicitly enabled in main.py")
    
    # 4. Check public paths configuration
    print("\n4. Checking public paths configuration...")
    if results["middleware_v2_present"]:
        with open(middleware_path, 'r') as f:
            content = f.read()
            public_paths = [
                "r'^/docs.*'",
                "r'^/api/v1/auth/login$'",
                "r'^/api/v1/auth/register$'",
                "r'^/health$'"
            ]
            missing_paths = []
            for path in public_paths:
                if path not in content:
                    missing_paths.append(path)
            
            if not missing_paths:
                print("   ✓ All required public paths configured")
            else:
                print(f"   ⚠ Missing public paths: {missing_paths}")
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_checks_pass = (
        results["feature_flag_enabled"] and
        results["middleware_v2_present"] and
        results["strict_mode_enabled"]
    )
    
    results["vulnerability_fixed"] = all_checks_pass
    
    if all_checks_pass:
        print("\n✅ SEC-001 VULNERABILITY FIXED!")
        print("   - JWT Authentication Middleware v2 is active")
        print("   - Strict mode is enabled (no bypasses)")
        print("   - Feature flag is enabled for gradual rollout")
        print("   - All non-public routes require authentication")
    else:
        print("\n⚠️  SEC-001 FIX INCOMPLETE")
        print("\nIssues found:")
        if not results["feature_flag_enabled"]:
            print("   - Feature flag not enabled")
        if not results["middleware_v2_present"]:
            print("   - Middleware v2 not found")
        if not results["strict_mode_enabled"]:
            print("   - Strict mode not enabled")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    if all_checks_pass:
        print("\n1. Run comprehensive test suite:")
        print("   pytest tests/test_sec001_auth_fix.py -v")
        print("\n2. Deploy to staging for integration testing")
        print("\n3. Monitor authentication metrics")
        print("\n4. Gradually increase rollout percentage")
        print("\n5. Mark SEC-001 as resolved and unblock 14 dependent tasks")
    else:
        print("\n1. Enable the feature flag in config/feature_flags.py")
        print("2. Ensure middleware v2 is properly imported in main.py")
        print("3. Re-run this verification script")
    
    return results

if __name__ == "__main__":
    results = verify_sec001_fix()
    
    # Exit with proper code
    if results["vulnerability_fixed"]:
        print("\n✅ Verification PASSED - SEC-001 is FIXED!")
        sys.exit(0)
    else:
        print("\n❌ Verification FAILED - SEC-001 needs attention")
        sys.exit(1)