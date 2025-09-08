#!/usr/bin/env python
"""Diagnose test issues"""
import logging
logger = logging.getLogger(__name__)


import subprocess
import sys

# Run a single test with full output
result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "tests/ai/test_compliance_accuracy.py::TestComplianceAccuracy::test_gdpr_basic_questions_accuracy",
        "-vvv",
        "--tb=short",
        "--capture=no",
    ],
    capture_output=True,
    text=True,
)

logger.info("STDOUT:")
logger.info(result.stdout)
logger.info("\nSTDERR:")
logger.info(result.stderr)
logger.info(f"\nReturn code: {result.returncode}")
