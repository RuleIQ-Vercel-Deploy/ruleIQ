#!/usr/bin/env python3
"""Debug a single failing test to see specific errors."""

import subprocess
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_single_test(test_file, test_name=None):
    """Run a single test file or specific test."""
    print(f"Running test: {test_file}")
    if test_name:
        print(f"Specific test: {test_name}")

    cmd = [sys.executable, "-m", "pytest", test_file, "-xvs", "--tb=long"]
    if test_name:
        cmd.extend(["-k", test_name])

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["USE_MOCK_AI"] = "true"

    result = subprocess.run(cmd, env=env)
    return result.returncode == 0


if __name__ == "__main__":
    # Test the cache strategy optimization first
    test_file = "tests/unit/services/test_cache_strategy_optimization.py"

    # Run just the first test to see specific error
    success = run_single_test(test_file, "test_performance_based_ttl_optimization")

    sys.exit(0 if success else 1)
