import subprocess
import sys

result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "tests/ai/test_compliance_accuracy.py::TestComplianceAccuracy::test_gdpr_basic_questions_accuracy",
        "-xvs",
        "--tb=line",
        "--capture=no",
    ],
    text=True,
)

print(f"Exit code: {result.returncode}")
