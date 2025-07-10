#!/usr/bin/env python
"""Diagnose test issues"""

import subprocess
import sys

# Run a single test with full output
result = subprocess.run([
    sys.executable, "-m", "pytest", 
    "tests/ai/test_compliance_accuracy.py::TestComplianceAccuracy::test_gdpr_basic_questions_accuracy",
    "-vvv", "--tb=short", "--capture=no"
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")