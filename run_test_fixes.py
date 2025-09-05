#!/usr/bin/env python3
"""
Execute all test fixes to rapidly achieve 80% pass rate.
This consolidates all fix operations for maximum impact.
"""

import subprocess
import os
import sys
from pathlib import Path
import time

# Change to project directory
os.chdir("/home/omar/Documents/ruleIQ")

print("=" * 80)
print("🚀 RAPID TEST FIX EXECUTION - TARGET: 80% PASS RATE")
print("=" * 80)
print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Target: 2,040 of 2,550 tests passing")
print(f"Current: ~35 tests passing")
print(f"Gap: ~2,005 tests to fix")
print()

# Step 1: Run systematic fixer
print("📋 STEP 1: Running systematic test fixer...")
print("-" * 40)
try:
    result = subprocess.run(
        ["python3", "fix_tests_systematic.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
except Exception as e:
    print(f"Error running systematic fixer: {e}")

# Step 2: Run QA mission
print("\n📋 STEP 2: Running QA mission controller...")
print("-" * 40)
try:
    result = subprocess.run(
        ["python3", "qa_mission_80_percent.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
except Exception as e:
    print(f"Error running QA mission: {e}")

# Step 3: Import test fixes module to apply environment fixes
print("\n📋 STEP 3: Applying environment fixes...")
print("-" * 40)
try:
    # Import the common test fixes which auto-applies environment fixes
    sys.path.insert(0, str(Path.cwd()))
    from tests.fixtures import common_test_fixes
    print("✅ Environment variables configured")
    print("✅ Test helpers loaded")
except Exception as e:
    print(f"Error importing test fixes: {e}")

# Step 4: Verify collection
print("\n📋 STEP 4: Verifying test collection...")
print("-" * 40)
try:
    result = subprocess.run(
        ["python3", "-m", "pytest", "--co", "-q"],
        capture_output=True,
        text=True,
        timeout=30
    )
    output = result.stdout + result.stderr
    
    # Extract collection count
    import re
    match = re.search(r"collected (\d+)", output)
    if match:
        collected = int(match.group(1))
        print(f"✅ Successfully collected {collected} tests")
    else:
        print("⚠️ Could not determine collection count")
        print(output[:500])  # Show first 500 chars for debugging
except Exception as e:
    print(f"Error verifying collection: {e}")

# Step 5: Run quick test sample
print("\n📋 STEP 5: Running test sample to estimate pass rate...")
print("-" * 40)
try:
    result = subprocess.run(
        ["python3", "-m", "pytest", 
         "--maxfail=50",
         "--tb=no",
         "-q"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Parse results
    output = result.stdout
    passed = output.count(" .")
    failed = output.count(" F")
    errors = output.count(" E")
    skipped = output.count(" s")
    
    total_run = passed + failed + errors
    if total_run > 0:
        pass_rate = (passed / total_run) * 100
        print(f"Sample Results:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  💥 Errors: {errors}")
        print(f"  ⏭️  Skipped: {skipped}")
        print(f"  📊 Pass Rate: {pass_rate:.1f}%")
        
        # Estimate for full suite
        if match:  # Use collected count from earlier
            estimated_passing = int(collected * (pass_rate / 100))
            print(f"\n📈 Estimated for full suite:")
            print(f"  Total Tests: {collected}")
            print(f"  Est. Passing: {estimated_passing}")
            print(f"  Target (80%): {int(collected * 0.8)}")
            print(f"  Gap: {int(collected * 0.8) - estimated_passing}")
    else:
        print("⚠️ No test results to analyze")
        
except Exception as e:
    print(f"Error running test sample: {e}")

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

# Generate final recommendations
print("\n🔧 RECOMMENDED NEXT ACTIONS:")
print("1. Fix remaining import errors:")
print("   pytest -x 2>&1 | grep ImportError")
print("\n2. Fix fixture issues:")
print("   pytest -x 2>&1 | grep 'fixture.*not found'")
print("\n3. Fix validation errors:")
print("   pytest tests/integration/ -k api -x")
print("\n4. Run full test suite:")
print("   pytest -v")
print("\n5. Generate coverage report:")
print("   pytest --cov=. --cov-report=html")

print("\n" + "=" * 80)
print("✨ Test fix execution complete!")
print("=" * 80)