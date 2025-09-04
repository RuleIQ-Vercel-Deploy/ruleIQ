#!/usr/bin/env python3
"""
Quick diagnostic of test suite issues.
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from collections import defaultdict

def run_command(cmd):
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", -1

def diagnose():
    print("=" * 70)
    print("RuleIQ Test Suite Diagnostic")
    print("=" * 70)
    
    # 1. Check Python environment
    print("\n1️⃣ Python Environment:")
    stdout, _, _ = run_command(".venv/bin/python --version")
    print(f"   Python: {stdout.strip()}")
    
    stdout, _, _ = run_command(".venv/bin/pip --version")
    print(f"   Pip: {stdout.strip()}")
    
    # 2. Check critical dependencies
    print("\n2️⃣ Critical Dependencies:")
    deps_to_check = [
        "pytest", "langgraph", "psycopg2-binary", "asyncpg", 
        "sqlalchemy", "fastapi", "redis", "pytest-asyncio"
    ]
    
    for dep in deps_to_check:
        stdout, _, code = run_command(f".venv/bin/pip show {dep} | grep Version")
        if code == 0 and stdout:
            version = stdout.strip().replace("Version: ", "")
            print(f"   ✅ {dep}: {version}")
        else:
            print(f"   ❌ {dep}: NOT INSTALLED")
    
    # 3. Check Docker containers
    print("\n3️⃣ Docker Containers:")
    stdout, _, _ = run_command("docker ps --format 'table {{.Names}}\t{{.Status}}' | grep ruleiq")
    if stdout:
        for line in stdout.strip().split('\n'):
            print(f"   {line}")
    else:
        print("   ⚠️  No RuleIQ test containers running")
    
    # 4. Quick test collection
    print("\n4️⃣ Test Collection Analysis:")
    stdout, stderr, code = run_command(".venv/bin/python -m pytest --collect-only -q 2>&1")
    
    # Count tests and errors
    test_count = 0
    error_lines = []
    import_errors = defaultdict(list)
    
    for line in (stdout + stderr).split('\n'):
        if 'collected' in line:
            match = re.search(r'collected (\d+)', line)
            if match:
                test_count = int(match.group(1))
        
        if 'ImportError' in line or 'ModuleNotFoundError' in line:
            # Extract module name
            match = re.search(r"No module named ['\"]([^'\"]+)['\"]", line)
            if match:
                module = match.group(1)
                import_errors['ModuleNotFoundError'].append(module)
            else:
                import_errors['ImportError'].append(line[:100])
        
        if 'ERROR' in line and '::' in line:
            error_lines.append(line)
    
    print(f"   📊 Tests collectible: {test_count}/2610")
    print(f"   ❌ Collection errors: {len(error_lines)}")
    
    if import_errors:
        print("\n   🔴 Import Issues:")
        for error_type, issues in import_errors.items():
            print(f"      {error_type}:")
            for issue in list(set(issues))[:5]:  # Show unique, first 5
                print(f"        - {issue}")
    
    # 5. Quick fixture check
    print("\n5️⃣ Fixture Availability Check:")
    stdout, _, _ = run_command(".venv/bin/python -m pytest --fixtures -q | head -20")
    
    critical_fixtures = ["db", "client", "test_user", "async_client", "session"]
    available_fixtures = []
    
    for line in stdout.split('\n'):
        for fixture in critical_fixtures:
            if fixture in line:
                available_fixtures.append(fixture)
    
    for fixture in critical_fixtures:
        if fixture in available_fixtures:
            print(f"   ✅ {fixture} fixture available")
        else:
            print(f"   ⚠️  {fixture} fixture might be missing")
    
    # 6. Sample test run (quick subset)
    print("\n6️⃣ Quick Test Sample (first 10 tests):")
    stdout, stderr, code = run_command(
        ".venv/bin/python -m pytest tests/ -k 'test_' --maxfail=10 -q 2>&1"
    )
    
    # Parse results
    passed = failed = errors = 0
    for line in stdout.split('\n'):
        if ' passed' in line:
            match = re.search(r'(\d+) passed', line)
            if match:
                passed = int(match.group(1))
        if ' failed' in line:
            match = re.search(r'(\d+) failed', line)
            if match:
                failed = int(match.group(1))
        if ' error' in line:
            match = re.search(r'(\d+) error', line)
            if match:
                errors = int(match.group(1))
    
    print(f"   Sample results: {passed} passed, {failed} failed, {errors} errors")
    
    # 7. Most common failure patterns
    if failed > 0 or errors > 0:
        print("\n7️⃣ Common Failure Patterns:")
        
        failure_patterns = defaultdict(int)
        for line in stderr.split('\n'):
            if 'AssertionError' in line:
                failure_patterns['AssertionError'] += 1
            elif 'fixture' in line.lower() and 'not found' in line.lower():
                failure_patterns['Missing Fixture'] += 1
            elif 'connection' in line.lower() and 'refused' in line.lower():
                failure_patterns['Connection Refused'] += 1
            elif 'table' in line.lower() and 'exist' in line.lower():
                failure_patterns['Database Table Issue'] += 1
        
        for pattern, count in sorted(failure_patterns.items(), key=lambda x: -x[1])[:5]:
            print(f"   - {pattern}: {count} occurrences")
    
    # 8. Recommendations
    print("\n8️⃣ Recommendations:")
    
    issues = []
    
    if test_count < 2600:
        issues.append("🔧 Fix import errors to collect all tests")
    
    if 'ModuleNotFoundError' in import_errors:
        missing = import_errors['ModuleNotFoundError']
        if missing:
            issues.append(f"📦 Install missing modules: {', '.join(list(set(missing))[:3])}")
    
    if not available_fixtures:
        issues.append("⚠️  Configure test fixtures in conftest.py")
    
    if failed > passed:
        issues.append("🔴 Focus on fixing common test patterns first")
    
    if not issues:
        issues.append("✅ Test suite appears to be in good shape!")
    
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    
    print("\n" + "=" * 70)
    print("Diagnostic complete. For full test run, use: .venv/bin/python install_and_test.py")
    print("=" * 70)

if __name__ == "__main__":
    diagnose()