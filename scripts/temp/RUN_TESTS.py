#!/usr/bin/env python3
"""
Master test runner for RuleIQ - P0 Task: Fix Test Infrastructure
This script handles all test setup and execution.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Execute full test suite."""
    
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "RULEIQ TEST SUITE RUNNER" + " "*23 + "║")
    print("║" + " "*18 + "P0: Fix Test Infrastructure" + " "*22 + "║")
    print("╚" + "═"*68 + "╝")
    
    # Ensure we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: tests/ directory not found.")
        print("   Please run from the RuleIQ project root.")
        sys.exit(1)
    
    # Check venv exists
    if not Path(".venv/bin/python").exists():
        print("❌ Error: .venv not found.")
        print("   Please create virtual environment first.")
        sys.exit(1)
    
    print("\n🚀 Starting test suite execution...")
    print("   This will:")
    print("   1. Install missing dependencies")
    print("   2. Fix test imports")
    print("   3. Start Docker containers")
    print("   4. Run full test suite")
    print("   5. Generate detailed report")
    
    print("\n" + "─"*70)
    
    # Run the main test execution script
    try:
        result = subprocess.run(
            [".venv/bin/python", "execute_full_test_suite.py"],
            check=False
        )
        
        # Check result
        if result.returncode == 0:
            print("\n" + "═"*70)
            print("✅ TEST SUITE EXECUTION SUCCESSFUL")
            print("   All critical tests are passing (>95% pass rate)")
            print("═"*70)
        else:
            print("\n" + "═"*70)
            print("⚠️  TEST SUITE NEEDS ATTENTION")
            print("   Check the report above for details")
            print("   Logs saved to: test_execution_full.log")
            print("═"*70)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())