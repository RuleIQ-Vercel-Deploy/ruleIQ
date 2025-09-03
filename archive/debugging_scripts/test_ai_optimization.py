#!/usr/bin/env python3
"""
from __future__ import annotations

Quick test runner for AI Optimization implementation.

This script runs a subset of the AI optimization tests to verify
the implementation is working correctly.
"""

import subprocess
import sys
from pathlib import Path

def run_quick_tests() -> bool:
    """Run a quick subset of AI optimization tests."""
    print("🚀 Running AI Optimization Quick Tests...")
    print("=" * 50)

    # Test files to run
    test_files = [
        "tests/unit/services/test_ai_circuit_breaker.py::TestAICircuitBreaker::test_circuit_breaker_initialization",
        "tests/unit/services/test_ai_model_selection.py::TestModelMetadata::test_model_metadata_creation",
        "tests/unit/services/test_ai_streaming.py::TestAIStreaming::test_stream_response_basic",
    ]

    success_count = 0
    total_tests = len(test_files)

    for test_file in test_files:
        print(f"\n🧪 Running: {test_file.split('::')[-1]}")

        cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("✅ PASSED")
                success_count += 1
            else:
                print("❌ FAILED")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")

        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT")
        except Exception as e:
            print(f"💥 ERROR: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 All quick tests PASSED!")
        return True
    else:
        print("⚠️  Some tests failed. Run full test suite for details.")
        return False

def check_test_setup() -> bool:
    """Check if the test environment is properly set up."""
    print("🔍 Checking test setup...")

    # Check if pytest is available
    try:
        import pytest

        print("✅ pytest available")
    except ImportError:
        print("❌ pytest not found. Install with: pip install pytest")
        return False

    # Check if test files exist
    test_files = [
        "tests/unit/services/test_ai_circuit_breaker.py",
        "tests/unit/services/test_ai_model_selection.py",
        "tests/unit/services/test_ai_streaming.py",
    ]

    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)

    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False

    print("✅ Test files found")

    # Check if AI modules can be imported
    try:
        from config.ai_config import get_ai_model
        from services.ai.assistant import ComplianceAssistant
        from services.ai.circuit_breaker import AICircuitBreaker

        print("✅ AI modules can be imported")
    except ImportError as e:
        print(f"❌ Cannot import AI modules: {e}")
        return False

    return True

def main() -> None:
    """Main function."""
    print("AI Optimization Test Verification")
    print("=" * 50)

    # Check setup first
    if not check_test_setup():
        print("\n❌ Test setup incomplete. Please fix the issues above.")
        sys.exit(1)

    print("\n✅ Test setup complete!")

    # Run quick tests
    if run_quick_tests():
        print("\n🎯 Quick tests completed successfully!")
        print("\nTo run the full test suite:")
        print("  python scripts/run_ai_optimization_tests.py")
        print("  python scripts/run_ai_optimization_tests.py --performance")
        sys.exit(0)
    else:
        print("\n❌ Some quick tests failed.")
        print("\nFor detailed diagnostics:")
        print("  python scripts/run_ai_optimization_tests.py --verbose")
        sys.exit(1)

if __name__ == "__main__":
    main()
