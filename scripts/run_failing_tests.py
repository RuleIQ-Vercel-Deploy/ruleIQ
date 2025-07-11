#!/usr/bin/env python3
"""
Test runner for the 32 failing tests.
Run this after applying fixes to verify they work.
"""

import subprocess
import sys

# Test files to run
test_files = [
    # Cache Strategy & Content Tests
    "tests/unit/services/test_cache_strategy_optimization.py",
    "tests/unit/services/test_cached_content.py",
    
    # AI Compliance Accuracy Tests  
    "tests/ai/test_compliance_accuracy.py",
    
    # AI Optimization Performance Tests
    "tests/performance/test_ai_optimization_performance.py",
    
    # Database Performance Tests
    "tests/performance/test_database_performance.py"
]

def run_tests():
    """Run all failing tests and report results."""
    results = {}
    
    for test_file in test_files:
        print(f"\nRunning {test_file}...")
        cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        results[test_file] = {
            "returncode": result.returncode,
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr
        }
        
        if result.returncode == 0:
            print(f"  ✓ PASSED")
        else:
            print(f"  ✗ FAILED")
            # Print first few lines of error
            error_lines = result.stderr.split('\n')[:5]
            for line in error_lines:
                if line.strip():
                    print(f"    {line}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r["passed"])
    failed = len(results) - passed
    
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed tests:")
        for test, result in results.items():
            if not result["passed"]:
                print(f"  - {test}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
