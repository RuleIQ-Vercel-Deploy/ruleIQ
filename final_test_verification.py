#!/usr/bin/env python3
"""Final verification script for test collection fixes."""

import subprocess
import sys
import time

def run_collection_test():
    """Run pytest collection-only to verify all tests are collectable."""
    print("FINAL TEST COLLECTION VERIFICATION")
    print("=" * 80)
    print("\n🔍 Running pytest collection-only on entire test suite...\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "--collect-only", "--quiet"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        # Parse output
        output_lines = result.stdout.split('\n')
        stderr_lines = result.stderr.split('\n')
        
        # Look for collection summary
        collected_count = 0
        errors_count = 0
        
        for line in output_lines:
            if 'collected' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'collected' and i > 0:
                        try:
                            collected_count = int(parts[i-1])
                        except:
                            pass
            if 'error' in line.lower():
                errors_count += 1
        
        # Check for errors in stderr
        for line in stderr_lines:
            if 'ERROR' in line or 'FAILED' in line:
                errors_count += 1
        
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        if result.returncode == 0 and errors_count == 0:
            print(f"✅ SUCCESS: All tests are collectable!")
            print(f"   - Total tests collected: {collected_count}")
            print(f"   - Collection time: {elapsed:.2f} seconds")
            print(f"   - No collection errors detected")
            
            if collected_count >= 1800:
                print(f"\n🎉 PERFECT! Collected {collected_count} tests (target was 1800+)")
            elif collected_count >= 1500:
                print(f"\n✅ EXCELLENT! Collected {collected_count} tests")
            else:
                print(f"\n⚠️ Collected {collected_count} tests (fewer than expected)")
                
        else:
            print(f"❌ COLLECTION ERRORS DETECTED")
            print(f"   - Tests collected: {collected_count}")
            print(f"   - Errors found: {errors_count}")
            print(f"   - Return code: {result.returncode}")
            
            # Show specific errors
            print("\nError details:")
            for line in stderr_lines:
                if 'ERROR' in line or 'ImportError' in line or 'ModuleNotFoundError' in line:
                    print(f"   {line}")
        
        return result.returncode == 0 and errors_count == 0
        
    except subprocess.TimeoutExpired:
        print("⚠️ Collection timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_specific_files():
    """Check the specific 10 files that had issues."""
    print("\n" + "=" * 80)
    print("CHECKING SPECIFIC PROBLEM FILES")
    print("=" * 80)
    
    problem_files = [
        "tests/integration/test_assessment_workflow.py",
        "tests/test_critical_auth.py", 
        "tests/test_golden_dataset_validators.py",
        "tests/test_integration.py",
        "tests/test_jwt_authentication.py",
        "tests/test_notification_basic.py",
        "tests/test_phase1_fastapi.py",
        "tests/test_phase2_fastapi.py",
        "tests/test_phase3_fastapi.py",
        "tests/test_security_integration_e2e.py"
    ]
    
    all_pass = True
    for filepath in problem_files:
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", filepath, "--collect-only", "--quiet"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Count tests
                count = 0
                for line in result.stdout.split('\n'):
                    if 'collected' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'collected' and i > 0:
                                try:
                                    count = int(parts[i-1])
                                except:
                                    pass
                print(f"✅ {filepath:50} [{count:3} tests]")
            else:
                print(f"❌ {filepath:50} [FAILED]")
                all_pass = False
                
        except Exception as e:
            print(f"❌ {filepath:50} [ERROR: {e}]")
            all_pass = False
    
    return all_pass

def main():
    """Main verification."""
    print("\n" + "🎯" * 40)
    print("PERFECTIONIST'S FINAL VERIFICATION")
    print("🎯" * 40)
    print("\nGoal: ZERO collection errors, 1800+ accessible tests")
    
    # Check specific files first
    specific_ok = check_specific_files()
    
    # Then check full collection
    full_ok = run_collection_test()
    
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    
    if specific_ok and full_ok:
        print("🏆 PERFECT SUCCESS! 🏆")
        print("✅ All 10 problem files fixed")
        print("✅ Zero collection errors")
        print("✅ Full test suite accessible")
        print("\nThe perfectionist mission is COMPLETE!")
        return 0
    else:
        print("⚠️ Some issues remain:")
        if not specific_ok:
            print("  - Some specific files still have errors")
        if not full_ok:
            print("  - Full collection has errors")
        print("\nRun 'python check_test_errors.py' for detailed diagnostics")
        return 1

if __name__ == "__main__":
    sys.exit(main())