#!/usr/bin/env python
"""
Execute comprehensive test fixes and report status.
Focus on getting tests to pass and achieving 70% coverage.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 70)
    print("EXECUTING COMPREHENSIVE TEST FIXES FOR RULEIQ")
    print("Goal: Fix failing tests and achieve 70% coverage")
    print("=" * 70)
    
    # Ensure we're in the right directory
    os.chdir("/home/omar/Documents/ruleIQ")
    
    # Step 1: Run critical fixes
    print("\n1. Running critical test fixes...")
    result = subprocess.run([".venv/bin/python", "fix_critical_tests.py"], 
                          capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    
    # Step 2: Run bulk fixes
    print("\n2. Running bulk test fixes...")
    result = subprocess.run([".venv/bin/python", "bulk_fix_tests.py"], 
                          capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    
    # Step 3: Analyze remaining errors
    print("\n3. Analyzing remaining test errors...")
    result = subprocess.run([".venv/bin/python", "analyze_test_errors.py"], 
                          capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    
    # Step 4: Try to collect tests
    print("\n4. Testing if pytest can collect tests now...")
    result = subprocess.run([".venv/bin/python", "-m", "pytest", 
                           "--collect-only", "--quiet"],
                          capture_output=True, text=True)
    
    # Count collected tests
    collected = 0
    errors = 0
    for line in result.stdout.splitlines():
        if "collected" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "collected" and i > 0:
                    try:
                        collected = int(parts[i-1])
                    except:
                        pass
        if "error" in line.lower():
            errors += 1
    
    print(f"✓ Collected {collected} tests")
    if errors > 0:
        print(f"⚠ {errors} collection errors remain")
    
    # Step 5: Run actual tests with coverage
    print("\n5. Running tests with coverage...")
    print("-" * 50)
    
    result = subprocess.run([
        ".venv/bin/python", "-m", "pytest",
        "-v",
        "--tb=short",
        "--cov=.",
        "--cov-report=term",
        "--maxfail=10",
        "-x"
    ], capture_output=True, text=True)
    
    # Parse results
    lines = result.stdout.splitlines()
    passed = failed = skipped = 0
    coverage_pct = 0
    
    for line in lines:
        if " passed" in line:
            try:
                passed = int(line.split()[0])
            except:
                pass
        if " failed" in line:
            try:
                failed = int(line.split()[0])
            except:
                pass
        if " skipped" in line:
            try:
                skipped = int(line.split()[0])
            except:
                pass
        if "TOTAL" in line and "%" in line:
            # Extract coverage percentage
            parts = line.split()
            for part in parts:
                if "%" in part:
                    try:
                        coverage_pct = int(part.replace("%", ""))
                    except:
                        pass
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST EXECUTION SUMMARY")
    print("=" * 70)
    print(f"✓ Passed:  {passed}")
    print(f"✗ Failed:  {failed}")
    print(f"⊘ Skipped: {skipped}")
    print(f"━━━━━━━━━━━")
    print(f"Total:     {passed + failed + skipped}")
    print()
    print(f"Coverage:  {coverage_pct}%")
    
    if coverage_pct >= 70:
        print("\n✅ SUCCESS: Coverage target of 70% achieved!")
    else:
        print(f"\n⚠ Coverage is {coverage_pct}%, need {70 - coverage_pct}% more to reach 70%")
    
    # Show top uncovered files if below target
    if coverage_pct < 70:
        print("\n6. Analyzing coverage gaps...")
        result = subprocess.run([
            ".venv/bin/python", "-m", "pytest",
            "--cov=.",
            "--cov-report=term-missing:skip-covered",
            "--quiet"
        ], capture_output=True, text=True)
        
        print("\nTop uncovered modules (focus on these for coverage):")
        coverage_lines = []
        for line in result.stdout.splitlines():
            if "/" in line and "%" in line and "TOTAL" not in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        pct = int(parts[-1].replace("%", ""))
                        if pct < 50:  # Show files with < 50% coverage
                            coverage_lines.append((pct, line))
                    except:
                        pass
        
        coverage_lines.sort()
        for pct, line in coverage_lines[:10]:
            print(f"  {line}")
    
    print("\n" + "=" * 70)
    print("Test fix execution complete!")
    print("=" * 70)
    
    return 0 if coverage_pct >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())