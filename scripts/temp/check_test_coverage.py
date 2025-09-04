#!/usr/bin/env python3
"""
Script to check current test coverage and count tests.
QA Specialist - Day 4 Coverage Tracking
"""
import os
import re
from pathlib import Path
import subprocess
import json
from datetime import datetime


def count_test_functions(file_path):
    """Count test functions in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Count functions starting with test_ or methods in Test classes
    test_pattern = re.compile(r'^\s*(async )?def test_', re.MULTILINE)
    matches = test_pattern.findall(content)
    return len(matches)


def scan_test_directory(test_dir):
    """Recursively scan test directory for test files and count tests."""
    test_dir_path = Path(test_dir)
    total_tests = 0
    test_files = []
    
    for test_file in test_dir_path.rglob('test_*.py'):
        if '__pycache__' not in str(test_file):
            test_count = count_test_functions(test_file)
            if test_count > 0:
                test_files.append({
                    'file': str(test_file).replace('/home/omar/Documents/ruleIQ/', ''),
                    'tests': test_count
                })
                total_tests += test_count
    
    return total_tests, test_files


def run_coverage_analysis():
    """Run pytest with coverage and get results."""
    print("Running coverage analysis...")
    try:
        # Run pytest with coverage in JSON format
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                'tests/',
                '--cov=services',
                '--cov=api',
                '--cov=utils',
                '--cov=database',
                '--cov=middleware',
                '--cov=monitoring',
                '--cov-report=json',
                '--cov-report=term',
                '--tb=no',
                '-q'
            ],
            capture_output=True,
            text=True,
            cwd='/home/omar/Documents/ruleIQ'
        )
        
        # Try to read coverage.json if it was created
        coverage_file = Path('/home/omar/Documents/ruleIQ/coverage.json')
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
                return coverage_data.get('totals', {}).get('percent_covered', 0)
        else:
            # Parse coverage from terminal output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'TOTAL' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if '%' in part:
                            return float(part.replace('%', ''))
            return 0
    except Exception as e:
        print(f"Error running coverage: {e}")
        return 0


def main():
    """Main function to analyze test coverage."""
    print("=" * 80)
    print("RuleIQ Test Coverage Analysis - Day 4")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Count tests
    test_dir = '/home/omar/Documents/ruleIQ/tests'
    total_tests, test_files = scan_test_directory(test_dir)
    
    print(f"\nTotal Test Functions Found: {total_tests}")
    print("\nTest Distribution by File:")
    print("-" * 50)
    
    # Group by directory
    by_directory = {}
    for file_info in sorted(test_files, key=lambda x: x['file']):
        dir_name = os.path.dirname(file_info['file'])
        if dir_name not in by_directory:
            by_directory[dir_name] = []
        by_directory[dir_name].append(file_info)
    
    for directory, files in sorted(by_directory.items()):
        dir_total = sum(f['tests'] for f in files)
        print(f"\n{directory}/ ({dir_total} tests)")
        for file_info in files:
            filename = os.path.basename(file_info['file'])
            print(f"  {filename:40} {file_info['tests']:3} tests")
    
    # Run coverage analysis
    print("\n" + "=" * 80)
    print("Running Coverage Analysis...")
    print("=" * 80)
    
    coverage_percent = run_coverage_analysis()
    
    print(f"\nCurrent Coverage: {coverage_percent:.1f}%")
    print(f"Target Coverage: 70%")
    
    if coverage_percent >= 70:
        print("✅ TARGET ACHIEVED!")
    else:
        gap = 70 - coverage_percent
        print(f"⚠️  Gap to Target: {gap:.1f}%")
        
        # Estimate tests needed
        tests_per_percent = total_tests / max(coverage_percent, 1)
        estimated_tests_needed = int(gap * tests_per_percent)
        print(f"\nEstimated Additional Tests Needed: ~{estimated_tests_needed}")
    
    # Summary for Day 4
    print("\n" + "=" * 80)
    print("Day 4 Progress Summary")
    print("=" * 80)
    print(f"Starting Tests (Day 3): ~377")
    print(f"Current Tests: {total_tests}")
    print(f"Tests Added Today: {total_tests - 377}")
    print(f"Coverage Progress: {coverage_percent:.1f}% (Target: 70%)")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("Priority Areas for Additional Testing:")
    print("=" * 80)
    
    if coverage_percent < 70:
        print("1. Frontend components (currently 0% - need React testing setup)")
        print("2. Service layer functions missing tests")
        print("3. Error handling and edge cases")
        print("4. Database repository methods")
        print("5. Authentication and authorization flows")
    else:
        print("✅ Excellent work! Target coverage achieved.")
        print("   Consider adding:")
        print("   - Performance tests")
        print("   - Security vulnerability tests")
        print("   - Load testing scenarios")


if __name__ == "__main__":
    main()