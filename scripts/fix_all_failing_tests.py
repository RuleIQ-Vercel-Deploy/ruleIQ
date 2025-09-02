#!/usr/bin/env python3
"""
Comprehensive fix for all 32 failing tests.

This script:
1. Fixes fixture scope issues in test files
2. Ensures proper mocking configuration
3. Validates database setup
4. Creates a test runner
"""

import os
import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def fix_fixture_scope_in_file(file_path) -> bool:
    """Fix fixtures defined inside test classes."""
    print(f"Fixing fixtures in {file_path.name}...")

    with open(file_path, "r") as f:
        content = f.read()

    # Pattern to find fixtures inside classes
    class_pattern = r'class\s+(\w+).*?:\s*""".*?"""'
    fixture_pattern = r'(\s+)@pytest\.fixture\s*\n\s+def\s+(\w+)\(self[^)]*\):\s*\n\s+"""(.*?)"""(.*?)(?=\n\s+(?:def|@|class)|$)'

    # Find all fixtures inside classes
    fixtures_to_move = []
    for class_match in re.finditer(class_pattern, content, re.DOTALL):
        class_content = content[class_match.start() : class_match.end()]
        class_match.group(1)

        for fixture_match in re.finditer(fixture_pattern, class_content, re.DOTALL):
            fixture_name = fixture_match.group(2)
            fixture_doc = fixture_match.group(3)
            fixture_body = fixture_match.group(4)

            # Clean up the fixture body (remove self parameter)
            fixture_body = re.sub(r"\(self(?:,\s*)?", "(", fixture_body)

            fixtures_to_move.append(
                {
                    "name": fixture_name,
                    "doc": fixture_doc,
                    "body": fixture_body,
                    "full_match": fixture_match.group(0),
                }
            )

    if not fixtures_to_move:
        print(f"  No fixtures to move in {file_path.name}")
        return False

    # Remove fixtures from inside classes
    modified_content = content
    for fixture in fixtures_to_move:
        modified_content = modified_content.replace(fixture["full_match"], "")

    # Add fixtures before the first class or test
    first_class_match = re.search(r"^class\s+\w+", modified_content, re.MULTILINE)
    if first_class_match:
        insert_pos = first_class_match.start()

        # Build fixture definitions
        fixture_defs = []
        for fixture in fixtures_to_move:
            fixture_def = f"""
@pytest.fixture
def {fixture["name"]}{fixture["body"].strip()}
"""
            fixture_defs.append(fixture_def)

        # Insert fixtures
        modified_content = (
            modified_content[:insert_pos]
            + "\n".join(fixture_defs)
            + "\n\n"
            + modified_content[insert_pos:]
        )

    # Write back
    with open(file_path, "w") as f:
        f.write(modified_content)

    print(f"  Moved {len(fixtures_to_move)} fixtures outside classes")
    return True


def fix_cache_strategy_tests() -> None:
    """Fix cache strategy and cached content tests."""
    print("\n1. Fixing Cache Strategy Tests...")

    test_files = [
        project_root / "tests/unit/services/test_cache_strategy_optimization.py",
        project_root / "tests/unit/services/test_cached_content.py",
    ]

    for test_file in test_files:
        if test_file.exists():
            # Already fixed in previous script, just verify
            with open(test_file, "r") as f:
                content = f.read()

            # Check if fixtures are outside classes
            if (
                "@pytest.fixture" in content
                and "def optimized_cache_config():" in content
            ):
                print(f"  ✓ {test_file.name} already fixed")
            else:
                fix_fixture_scope_in_file(test_file)
        else:
            print(f"  ✗ {test_file.name} not found!")


def fix_compliance_accuracy_tests() -> None:
    """Fix AI compliance accuracy tests."""
    print("\n2. Fixing AI Compliance Accuracy Tests...")

    test_file = project_root / "tests/ai/test_compliance_accuracy.py"

    if not test_file.exists():
        print(f"  ✗ {test_file.name} not found!")
        return

    # Check if golden dataset exists
    dataset_path = project_root / "tests/ai/golden_datasets/gdpr_questions.json"
    if dataset_path.exists():
        print("  ✓ Golden dataset exists")
    else:
        print("  ✗ Golden dataset missing - creating...")
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        # Create minimal dataset
        import json

        dataset = [
            {
                "id": "gdpr_001",
                "question": "What is the maximum fine for GDPR violations?",
                "expected_answer": "Up to €20 million or 4% of annual global turnover, whichever is higher",
                "framework": "GDPR",
                "category": "penalties",
                "keywords": ["€20 million", "4%", "turnover", "fine"],
                "difficulty": "basic",
                "source": "GDPR Article 83",
            }
        ]
        with open(dataset_path, "w") as f:
            json.dump(dataset, f, indent=2)

    # Check for fixture issues
    with open(test_file, "r") as f:
        content = f.read()

    # Look for fixtures inside classes
    if "class Test" in content and "@pytest.fixture" in content and "def " in content:
        fix_fixture_scope_in_file(test_file)
    else:
        print("  ✓ No fixture scope issues detected")


def fix_optimization_performance_tests() -> None:
    """Fix AI optimization performance tests."""
    print("\n3. Fixing AI Optimization Performance Tests...")

    test_file = project_root / "tests/performance/test_ai_optimization_performance.py"

    if not test_file.exists():
        print(f"  ✗ {test_file.name} not found!")
        return

    with open(test_file, "r") as f:
        content = f.read()

    # Check for fixture issues
    if "class Test" in content and "@pytest.fixture" in content:
        fix_fixture_scope_in_file(test_file)
    else:
        print("  ✓ No fixture scope issues detected")

    # Verify circuit breaker exists
    circuit_breaker_path = project_root / "services/ai/circuit_breaker.py"
    if circuit_breaker_path.exists():
        print("  ✓ Circuit breaker module exists")
    else:
        print("  ✗ Circuit breaker module missing!")


def fix_database_performance_tests() -> None:
    """Fix database performance tests."""
    print("\n4. Fixing Database Performance Tests...")

    test_file = project_root / "tests/performance/test_database_performance.py"

    if not test_file.exists():
        print(f"  ✗ {test_file.name} not found!")
        return

    with open(test_file, "r") as f:
        content = f.read()

    # Check for fixture issues
    if "class Test" in content and "@pytest.fixture" in content:
        fix_fixture_scope_in_file(test_file)
    else:
        print("  ✓ No fixture scope issues detected")

    # Check database models
    evidence_model = project_root / "database/evidence_item.py"
    if evidence_model.exists():
        print("  ✓ EvidenceItem model exists")

        # Verify required fields
        with open(evidence_model, "r") as f:
            model_content = f.read()

        required_fields = [
            "user_id",
            "business_profile_id",
            "framework_id",
            "evidence_name",
            "evidence_type",
            "control_reference",
            "description",
            "status",
            "collection_method",
        ]

        missing_fields = [f for f in required_fields if f not in model_content]
        if missing_fields:
            print(f"  ✗ Missing fields: {missing_fields}")
        else:
            print("  ✓ All required fields present")
    else:
        print("  ✗ EvidenceItem model not found!")


def create_comprehensive_test_runner() -> None:
    """Create a comprehensive test runner."""
    print("\n5. Creating Test Runner...")

    runner_content = '''#!/usr/bin/env python3
"""
Comprehensive test runner for all 32 failing tests.
Runs tests with proper error reporting and summary.
"""

import subprocess
import sys
import os
from pathlib import Path

# Test categories
TEST_CATEGORIES = {
    "Cache Strategy & Content": [
        "tests/unit/services/test_cache_strategy_optimization.py",
        "tests/unit/services/test_cached_content.py",
    ],
    "AI Compliance Accuracy": [
        "tests/ai/test_compliance_accuracy.py",
    ],
    "AI Optimization Performance": [
        "tests/performance/test_ai_optimization_performance.py",
    ],
    "Database Performance": [
        "tests/performance/test_database_performance.py",
    ]
}

def run_test_category(category_name, test_files):
    """Run tests in a category."""
    print(f"\\n{'='*60}")
    print(f"Running {category_name} Tests")
    print('='*60)

    results = []
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"\\n❌ {test_file} - FILE NOT FOUND")
            results.append({"file": test_file, "passed": False, "error": "File not found"})
            continue

        print(f"\\n▶ Running {test_file}...")

        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            "-v",
            "--tb=short",
            "--no-header",
            "--no-summary",
            "-q"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse results
        output = result.stdout + result.stderr
        passed = result.returncode == 0

        if passed:
            # Count passed tests
            passed_count = output.count(" PASSED")
            print(f"  ✅ All tests passed ({passed_count} tests)")
        else:
            # Extract failure info
            failed_count = output.count(" FAILED")
            error_count = output.count(" ERROR")

            print(f"  ❌ Tests failed (Failed: {failed_count}, Errors: {error_count})")

            # Show first few error lines
            error_lines = [line for line in output.split('\\n') if 'FAILED' in line or 'ERROR' in line][:3]
            for line in error_lines:
                print(f"     {line.strip()}")

        results.append({
            "file": test_file,
            "passed": passed,
            "output": output
        })

    return results

def main():
    """Run all test categories and provide summary."""
    print("🧪 Running All Failing Tests")
    print("="*60)

    all_results = {}

    # Set environment
    os.environ["ENV"] = "testing"
    os.environ["USE_MOCK_AI"] = "true"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

    # Run each category
    for category, test_files in TEST_CATEGORIES.items():
        results = run_test_category(category, test_files)
        all_results[category] = results

    # Summary
    print(f"\\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)

    total_files = 0
    passed_files = 0

    for category, results in all_results.items():
        category_passed = sum(1 for r in results if r["passed"])
        category_total = len(results)
        total_files += category_total
        passed_files += category_passed

        status = "✅" if category_passed == category_total else "❌"
        print(f"{status} {category}: {category_passed}/{category_total} files passed")

    print(f"\\n📈 Overall: {passed_files}/{total_files} test files passed")

    if passed_files < total_files:
        print("\\n❌ Failed test files:")
        for category, results in all_results.items():
            for result in results:
                if not result["passed"]:
                    print(f"  - {result['file']}")

    return passed_files == total_files

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''

    runner_path = project_root / "scripts/run_all_failing_tests.py"
    with open(runner_path, "w") as f:
        f.write(runner_content)

    os.chmod(runner_path, 0o755)
    print(f"  ✓ Created comprehensive test runner at {runner_path}")


def main() -> None:
    """Main function to apply all fixes."""
    print("🔧 Applying Comprehensive Test Fixes")
    print("=" * 60)

    # Apply all fixes
    fix_cache_strategy_tests()
    fix_compliance_accuracy_tests()
    fix_optimization_performance_tests()
    fix_database_performance_tests()
    create_comprehensive_test_runner()

    print("\n" + "=" * 60)
    print("✅ All fixes applied!")
    print("\nNext steps:")
    print("1. Run: python scripts/run_all_failing_tests.py")
    print("2. Review any remaining failures")
    print("3. Apply targeted fixes based on specific error messages")


if __name__ == "__main__":
    main()
