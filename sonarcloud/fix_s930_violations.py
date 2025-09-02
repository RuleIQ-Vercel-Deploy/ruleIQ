#!/usr/bin/env python3
"""
Fix S930 violations - Remove unexpected named arguments
"""

import os
import re

# Define the fixes needed based on the analysis
FIXES = [
    {
        "file": "api/dependencies/auth.py",
        "pattern": r"request_origin=request\.headers\.get\(\"Origin\"\)",
        "replacement": "origin=request.headers.get(\"Origin\")",
        "lines": [323]
    },
    {
        "file": "api/dependencies/auth.py", 
        "pattern": r"endpoint=str\(request\.url\.path\)",
        "replacement": "",  # Remove this argument
        "lines": [324]
    },
    {
        "file": "api/dependencies/auth.py",
        "pattern": r"method=request\.method,",
        "replacement": "",  # Remove this argument
        "lines": [325]
    },
    {
        "file": "api/middleware/api_key_auth.py",
        "pattern": r"request_origin=",
        "replacement": "origin=",
        "lines": [125, 127, 128]
    },
    {
        "file": "langgraph_agent/nodes/notification_nodes.py",
        "pattern": r"request_origin=",
        "replacement": "origin=",
        "lines": [851, 852, 857, 858, 862, 863]
    },
    {
        "file": "services/ai/assistant.py",
        "pattern": r"request_origin=",
        "replacement": "origin=",
        "lines": [4518, 4519, 4520, 4521, 4522, 4523, 4524]
    },
    {
        "file": "workers/compliance_tasks.py",
        "pattern": r"request_origin=",
        "replacement": "origin=",
        "lines": [40, 84]
    }
]

def fix_file(file_path, fixes):
    """Fix a single file"""
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    modified = False
    for fix in fixes:
        for line_num in fix['lines']:
            # Adjust for 0-based indexing
            idx = line_num - 1
            if idx < len(lines):
                old_line = lines[idx]
                if fix['replacement']:
                    # Replace the pattern
                    new_line = re.sub(fix['pattern'], fix['replacement'], old_line)
                else:
                    # Remove the line entirely if it's just an argument
                    if fix['pattern'] in old_line:
                        # Check if this is a standalone argument line
                        if old_line.strip().startswith(fix['pattern'].replace(r"\(", "(").replace(r"\)", ")")):
                            new_line = ""  # Remove the entire line
                        else:
                            # Remove just the argument part
                            new_line = re.sub(fix['pattern'] + r",?\s*", "", old_line)
                    else:
                        new_line = old_line
                
                if new_line != old_line:
                    lines[idx] = new_line
                    modified = True
                    print(f"  Fixed line {line_num}")
    
    if modified:
        with open(file_path, 'w') as f:
            f.writelines(lines)
        return True
    return False

def main():
    print("\n" + "="*60)
    print("FIXING S930 VIOLATIONS - Unexpected Named Arguments")
    print("="*60)
    
    # Group fixes by file
    fixes_by_file = {}
    for fix in FIXES:
        file_path = fix['file']
        if file_path not in fixes_by_file:
            fixes_by_file[file_path] = []
        fixes_by_file[file_path].append(fix)
    
    total_fixed = 0
    for file_path, file_fixes in fixes_by_file.items():
        print(f"\n📝 Processing: {file_path}")
        if fix_file(file_path, file_fixes):
            total_fixed += 1
            print(f"  ✅ Fixed {len(file_fixes)} issues")
        else:
            print(f"  ⚠️  No changes made")
    
    print("\n" + "="*60)
    print(f"✅ Fixed files: {total_fixed}/{len(fixes_by_file)}")
    print("="*60)
    
    # Additional fixes for test files
    print("\n🔧 Fixing test files with similar issues...")
    test_files = [
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
    
    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Replace request_origin with origin
            new_content = re.sub(r'request_origin=', 'origin=', content)
            
            # Remove endpoint and method arguments from validate_api_key calls
            new_content = re.sub(r',\s*endpoint=[^,\)]+', '', new_content)
            new_content = re.sub(r',\s*method=[^,\)]+', '', new_content)
            
            if new_content != content:
                with open(test_file, 'w') as f:
                    f.write(new_content)
                print(f"✅ Fixed: {test_file}")

if __name__ == "__main__":
    main()