#!/usr/bin/env python3
"""Find test files with service import errors"""
import os
import re

def find_service_imports():
    """Find test files importing from services directory"""
    
    test_dirs = ['tests']
    service_imports = []
    
    for test_dir in test_dirs:
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith('.py') and file.startswith('test_'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            
                        # Look for service imports
                        patterns = [
                            r'^from services\.\w+',
                            r'^import services\.\w+',
                            r'^from middleware\.\w+',
                            r'^import middleware\.\w+'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content, re.MULTILINE)
                            if matches:
                                # Check if they're commented out
                                for match in matches:
                                    lines = content.split('\n')
                                    for i, line in enumerate(lines):
                                        if match in line and not line.strip().startswith('#'):
                                            service_imports.append({
                                                'file': filepath,
                                                'line': i + 1,
                                                'import': match
                                            })
                                            break
                                            
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
    
    return service_imports

if __name__ == "__main__":
    imports = find_service_imports()
    
    if imports:
        print(f"Found {len(imports)} uncommented service imports:")
        
        # Group by file
        by_file = {}
        for imp in imports:
            if imp['file'] not in by_file:
                by_file[imp['file']] = []
            by_file[imp['file']].append(imp)
        
        for file, file_imports in by_file.items():
            print(f"\n{file}:")
            for imp in file_imports:
                print(f"  Line {imp['line']}: {imp['import']}")
    else:
        print("No uncommented service imports found in test files.")
        
    # Also check for specific modules we know don't exist
    missing_modules = [
        'services.assessment_service',
        'services.ai_service', 
        'services.evidence_service',
        'services.compliance_service',
        'services.auth_service',
        'services.rbac_service',
        'services.notification_service',
        'services.email_service',
        'services.ai.tools',
        'middleware.jwt_auth',
        'middleware.rbac_middleware'
    ]
    
    print("\n\nChecking for specific missing module imports:")
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        for module in missing_modules:
                            if module in line and not line.strip().startswith('#'):
                                print(f"{filepath}:{i+1} - {line.strip()}")
                                
                except Exception:
                    pass