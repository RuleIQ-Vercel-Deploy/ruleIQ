#!/usr/bin/env python3
"""
Check import errors in the RuleIQ application
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/omar/Documents/ruleIQ')

def check_main_imports():
    """Check if main.py can import all its dependencies."""
    print("Checking main.py imports...")
    errors = []
    
    # Try importing each router module that's used in main.py
    routers_to_check = [
        'api.routers.agentic_rag',
        'api.routers.ai_assessments', 
        'api.routers.ai_cost_monitoring',
        'api.routers.ai_cost_websocket',
        'api.routers.ai_optimization',
        'api.routers.ai_policy',
        'api.routers.api_keys',
        'api.routers.assessments',
        'api.routers.auth',
        'api.routers.business_profiles',
        'api.routers.chat',
        'api.routers.compliance',
        'api.routers.dashboard',
        'api.routers.evidence',
        'api.routers.evidence_collection',
        'api.routers.feedback',
        'api.routers.foundation_evidence',
        'api.routers.frameworks',
        'api.routers.freemium',
        'api.routers.google_auth',
        'api.routers.implementation',
        'api.routers.integrations',
        'api.routers.iq_agent',
        'api.routers.monitoring',
        'api.routers.payment',
        'api.routers.performance_monitoring',
        'api.routers.policies',
        'api.routers.readiness',
        'api.routers.reports',
        'api.routers.security',
        'api.routers.secrets_vault',
        'api.routers.test_utils',
        'api.routers.uk_compliance',
        'api.routers.users',
        'api.routers.webhooks',
        'api.routers.admin',
        'api.routers.rbac_auth',
        'api.routers.auth_monitoring',
        'api.routers.usage_dashboard',
        'api.routers.audit_export',
    ]
    
    for module in routers_to_check:
        try:
            exec(f"import {module}")
            print(f"✓ {module}")
        except ImportError as e:
            errors.append((module, str(e)))
            print(f"✗ {module}: {e}")
        except SyntaxError as e:
            errors.append((module, f"Syntax error: {e}"))
            print(f"✗ {module}: Syntax error: {e}")
        except Exception as e:
            errors.append((module, f"Other error: {e}"))
            print(f"✗ {module}: Other error: {e}")
    
    # Check middleware imports
    print("\nChecking middleware imports...")
    middleware_modules = [
        'middleware.jwt_auth',
        'middleware.security_middleware',
        'middleware.security_headers',
        'api.middleware.rbac_middleware',
        'api.middleware.rate_limiter',
        'api.middleware.error_handler',
        'api.request_id_middleware',
    ]
    
    for module in middleware_modules:
        try:
            exec(f"import {module}")
            print(f"✓ {module}")
        except ImportError as e:
            errors.append((module, str(e)))
            print(f"✗ {module}: {e}")
        except Exception as e:
            errors.append((module, f"Other error: {e}"))
            print(f"✗ {module}: Other error: {e}")
    
    # Check service imports
    print("\nChecking service imports...")
    service_modules = [
        'services.ai.cost_management',
        'services.ai.policy_generator',
        'services.rate_limiting',
        'services.framework_service',
        'services.agentic_integration',
    ]
    
    for module in service_modules:
        try:
            exec(f"import {module}")
            print(f"✓ {module}")
        except ImportError as e:
            errors.append((module, str(e)))
            print(f"✗ {module}: {e}")
        except Exception as e:
            errors.append((module, f"Other error: {e}"))
            print(f"✗ {module}: Other error: {e}")
    
    # Check database imports
    print("\nChecking database imports...")
    database_modules = [
        'database.db_setup',
        'database.user',
        'database.User',
        'database.compliance_framework',
        'database.rbac',
    ]
    
    for module in database_modules:
        try:
            if module == 'database.User':
                exec("from database import User")
            else:
                exec(f"import {module}")
            print(f"✓ {module}")
        except ImportError as e:
            errors.append((module, str(e)))
            print(f"✗ {module}: {e}")
        except Exception as e:
            errors.append((module, f"Other error: {e}"))
            print(f"✗ {module}: Other error: {e}")
    
    return errors

def check_main_startup():
    """Try to import and start the FastAPI app."""
    print("\nAttempting to import main.py...")
    try:
        import main
        print("✓ main.py imported successfully")
        print(f"✓ FastAPI app created: {main.app}")
        return True
    except Exception as e:
        print(f"✗ Failed to import main.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("RuleIQ Import Check")
    print("=" * 60)
    
    errors = check_main_imports()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if errors:
        print(f"\n{len(errors)} import errors found:")
        for module, error in errors:
            print(f"  - {module}: {error}")
        
        print("\nCritical modules needing attention:")
        critical = [m for m, _ in errors if 'routers' in m or 'middleware' in m]
        for module in critical[:5]:
            print(f"  - {module}")
    else:
        print("\n✅ All imports successful!")
    
    print("\n" + "=" * 60)
    print("MAIN APP TEST")
    print("=" * 60)
    
    if check_main_startup():
        print("\n✅ Main application can start!")
    else:
        print("\n❌ Main application cannot start - fix the errors above")

if __name__ == '__main__':
    main()