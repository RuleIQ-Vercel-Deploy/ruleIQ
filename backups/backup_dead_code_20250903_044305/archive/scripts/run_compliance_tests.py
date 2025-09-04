#!/usr/bin/env python3
"""
Test runner for ComplianceState model tests.
"""
import sys
import os
import subprocess
import logging
logger = logging.getLogger(__name__)


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """Run tests and report results."""

    # First verify imports work
    logger.info("1. Testing imports...")
    try:
        from langgraph_agent.models.compliance_state import ComplianceState

        logger.info("✅ ComplianceState import successful")
    except ImportError as e:
        logger.info(f"❌ Import failed: {e}")
        return False

    # Run unit tests
    logger.info("\n2. Running unit tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/models/test_compliance_state.py",
            "-v",
            "--tb=short",
            "--no-header",
        ],
        capture_output=False,
        text=True,
    )

    if result.returncode != 0:
        logger.info(f"❌ Unit tests failed with code {result.returncode}")
        return False

    # Run integration tests
    logger.info("\n3. Running integration tests...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/test_state_integration.py",
            "-v",
            "--tb=short",
            "--no-header",
        ],
        capture_output=False,
        text=True,
    )

    if result.returncode != 0:
        logger.info(f"❌ Integration tests failed with code {result.returncode}")
        return False

    logger.info("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
