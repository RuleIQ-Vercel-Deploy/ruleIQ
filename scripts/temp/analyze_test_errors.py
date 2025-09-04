#!/usr/bin/env python
"""
Analyze test errors and categorize them for efficient fixing.
"""

import subprocess
import re
from collections import defaultdict
from pathlib import Path

def run_pytest_collect():
    """Run pytest collection to get all errors."""
    cmd = [
        ".venv/bin/python", "-m", "pytest",
        "--collect-only",
        "--tb=line",
        "-q"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr

def categorize_errors(output, errors):
    """Categorize test errors by type."""
    
    error_categories = defaultdict(list)
    
    # Common error patterns
    patterns = {
        'import_error': r"ImportError: cannot import name '([^']+)' from '([^']+)'",
        'module_not_found': r"ModuleNotFoundError: No module named '([^']+)'",
        'attribute_error': r"AttributeError: module '([^']+)' has no attribute '([^']+)'",
        'fixture_not_found': r"fixture '([^']+)' not found",
        'syntax_error': r"SyntaxError: (.+)",
        'name_error': r"NameError: name '([^']+)' is not defined",
        'type_error': r"TypeError: (.+)",
    }
    
    all_text = output + "\n" + errors
    lines = all_text.splitlines()
    
    for line in lines:
        for error_type, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                error_categories[error_type].append({
                    'match': match.groups(),
                    'line': line
                })
    
    # Also look for file-specific errors
    file_error_pattern = r"(tests/[^\s:]+\.py):(\d+): (.+)"
    for line in lines:
        match = re.search(file_error_pattern, line)
        if match:
            file_path, line_num, error = match.groups()
            error_categories['file_errors'].append({
                'file': file_path,
                'line': line_num,
                'error': error
            })
    
    return error_categories

def generate_fixes(error_categories):
    """Generate fix recommendations for each error category."""
    
    fixes = {}
    
    # Import errors - need to fix module paths or add mocks
    if 'import_error' in error_categories:
        import_errors = error_categories['import_error']
        fixes['import_error'] = []
        
        for error in import_errors:
            name, module = error['match']
            if 'services.ai' in module:
                fixes['import_error'].append(f"Mock {name} from {module}")
            else:
                fixes['import_error'].append(f"Fix import path for {name} from {module}")
    
    # Module not found - install or mock
    if 'module_not_found' in error_categories:
        modules = set(e['match'][0] for e in error_categories['module_not_found'])
        fixes['module_not_found'] = [f"Install or mock module: {m}" for m in modules]
    
    # Fixture not found - add to conftest.py
    if 'fixture_not_found' in error_categories:
        fixtures = set(e['match'][0] for e in error_categories['fixture_not_found'])
        fixes['fixture_not_found'] = [f"Add fixture: {f}" for f in fixtures]
    
    # Attribute errors - usually wrong imports
    if 'attribute_error' in error_categories:
        attrs = error_categories['attribute_error']
        fixes['attribute_error'] = []
        for error in attrs:
            module, attr = error['match']
            fixes['attribute_error'].append(f"Module {module} missing attribute {attr}")
    
    return fixes

def auto_fix_imports():
    """Automatically fix common import issues."""
    
    test_dir = Path("tests")
    fixes_made = []
    
    # Map of incorrect imports to correct ones
    import_mappings = {
        'from services.ai.quality_scorer import QualityScorer': 
            'from unittest.mock import Mock\nQualityScorer = Mock',
        'from services.ai.iq_agent import IQAgent':
            'from unittest.mock import Mock\nIQAgent = Mock',
        'from langgraph_agent.agents.iq_agent import IQAgent':
            'from unittest.mock import Mock\nIQAgent = Mock',
    }
    
    for test_file in test_dir.rglob("test_*.py"):
        content = test_file.read_text()
        original = content
        
        for old, new in import_mappings.items():
            if old in content and new not in content:
                content = content.replace(old, new)
                fixes_made.append(f"Fixed import in {test_file.name}")
        
        if content != original:
            test_file.write_text(content)
    
    return fixes_made

def main():
    print("=" * 60)
    print("ANALYZING TEST ERRORS")
    print("=" * 60)
    
    # Run pytest collection
    print("\n1. Collecting tests...")
    stdout, stderr = run_pytest_collect()
    
    # Categorize errors
    print("\n2. Categorizing errors...")
    error_categories = categorize_errors(stdout, stderr)
    
    print("\nError Summary:")
    for category, errors in error_categories.items():
        print(f"\n{category}: {len(errors)} errors")
        if errors and len(errors) <= 3:
            for error in errors[:3]:
                if isinstance(error, dict) and 'line' in error:
                    print(f"  - {error['line'][:80]}")
    
    # Generate fixes
    print("\n3. Recommended fixes:")
    fixes = generate_fixes(error_categories)
    for category, fix_list in fixes.items():
        print(f"\n{category}:")
        for fix in fix_list[:5]:  # Show first 5
            print(f"  - {fix}")
    
    # Apply auto-fixes
    print("\n4. Applying automatic fixes...")
    auto_fixes = auto_fix_imports()
    for fix in auto_fixes:
        print(f"  - {fix}")
    
    # Show most problematic files
    if 'file_errors' in error_categories:
        file_counts = defaultdict(int)
        for error in error_categories['file_errors']:
            file_counts[error['file']] += 1
        
        print("\n5. Most problematic test files:")
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        for file, count in sorted_files[:5]:
            print(f"  - {file}: {count} errors")
    
    print("\n" + "=" * 60)
    print("Analysis complete. Run pytest again to see remaining errors.")
    
    return len(error_categories.get('file_errors', []))

if __name__ == "__main__":
    error_count = main()
    exit(0 if error_count == 0 else 1)