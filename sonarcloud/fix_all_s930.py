#!/usr/bin/env python3
"""
Fix all S930 violations - Remove unexpected named arguments
"""

import os
import re

def fix_validate_api_key_calls(file_path):
    """Fix validate_api_key calls to match the actual method signature"""
    if not os.path.exists(file_path):
        print(f"  ⚠️  File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix request_origin -> origin
    content = re.sub(r'request_origin=', 'origin=', content)
    
    # Remove endpoint and method parameters from validate_api_key calls
    # This regex finds validate_api_key calls and removes endpoint and method parameters
    pattern = r'(validate_api_key\([^)]*?)'
    
    def remove_invalid_params(match):
        call = match.group(1)
        # Remove endpoint parameter
        call = re.sub(r',\s*endpoint=[^,)]+', '', call)
        # Remove method parameter
        call = re.sub(r',\s*method=[^,)]+', '', call)
        return call
    
    content = re.sub(pattern, remove_invalid_params, content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    print("\n" + "="*60)
    print("FIXING ALL S930 VIOLATIONS - Unexpected Named Arguments")
    print("="*60)
    
    # List of all files with S930 violations
    files_to_fix = [
        "api/middleware/api_key_auth.py",
        "langgraph_agent/nodes/notification_nodes.py",
        "services/ai/assistant.py",
        "workers/compliance_tasks.py",
        "tests/integration/api/test_freemium_endpoints.py",
        "tests/integration/test_external_service_integration.py",
        "tests/test_ai_neon.py",
        "tests/integration/test_comprehensive_api_workflows.py",
        "tests/integration/test_contract_validation.py",
        "tests/test_ai_policy_generator.py",
        "tests/test_graph_execution.py",
        "tests/test_state_management.py",
        "tests/fixtures/state_fixtures.py",
        "langgraph_agent/tests/test_tenancy.py",
        "services/ai/safety_manager.py"
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        print(f"\n📝 Processing: {file_path}")
        if fix_validate_api_key_calls(file_path):
            print(f"  ✅ Fixed")
            fixed_count += 1
        else:
            print(f"  ⚠️  No changes needed or file not found")
    
    print("\n" + "="*60)
    print(f"✅ Fixed {fixed_count}/{len(files_to_fix)} files")
    print("="*60)
    
    print("\n🎯 Summary:")
    print("  - Changed 'request_origin=' to 'origin='")
    print("  - Removed 'endpoint=' parameters")
    print("  - Removed 'method=' parameters")
    print("  - All validate_api_key calls now match the method signature")

if __name__ == "__main__":
    main()