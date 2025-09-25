#!/usr/bin/env python3
"""
Test group runner for organized test execution.
Divides tests into logical groups for better organization and parallelization.
"""

import sys
import subprocess
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Test group definitions
TEST_GROUPS = {
    "group1_unit": {
        "name": "Unit Tests",
        "paths": ["tests/unit/"],
        "markers": "unit",
        "workers": "auto",
        "estimated_time": "2-3 minutes"
    },
    "group2_ai_core": {
        "name": "AI Core Tests",
        "paths": ["tests/services/test_ai_service.py", "tests/services/test_llm_service.py"],
        "markers": "ai or llm",
        "workers": 2,
        "estimated_time": "3-4 minutes"
    },
    "group3_api_basic": {
        "name": "Basic API Tests",
        "paths": ["tests/api/"],
        "markers": "api and not slow",
        "workers": 4,
        "estimated_time": "4-5 minutes"
    },
    "group4_ai_endpoints": {
        "name": "AI Endpoints Tests",
        "paths": ["tests/api/test_ai_endpoints.py", "tests/api/test_compliance_ai.py"],
        "markers": "ai and api",
        "workers": 2,
        "estimated_time": "5-6 minutes"
    },
    "group5_advanced": {
        "name": "Advanced Features Tests",
        "paths": ["tests/integration/"],
        "markers": "integration or compliance",
        "workers": 2,
        "estimated_time": "3-4 minutes"
    },
    "group6_e2e": {
        "name": "End-to-End Tests",
        "paths": ["tests/e2e/"],
        "markers": "e2e",
        "workers": 1,
        "estimated_time": "6-8 minutes"
    }
}

def run_test_group(group_key):
    """Run a specific test group."""
    group = TEST_GROUPS[group_key]
    print(f"\n{'='*60}")
    print(f"Running {group['name']} ({group['estimated_time']})")
    print(f"{'='*60}")

    cmd = [".venv/bin/python", "-m", "pytest"]

    # Add paths if they exist
    existing_paths = []
    for path in group["paths"]:
        if Path(path).exists():
            existing_paths.append(path)

    if existing_paths:
        cmd.extend(existing_paths)
    elif group["markers"]:
        # If no paths exist, fall back to markers only
        pass
    else:
        print(f"Warning: No test paths found for {group['name']}")
        return 0

    # Add markers
    if group["markers"]:
        cmd.extend(["-m", group["markers"]])

    # Add parallelization
    workers = group["workers"]
    if workers == "auto":
        cmd.extend(["-n", "auto", "--dist=worksteal"])
    elif workers > 1:
        cmd.extend(["-n", str(workers), "--dist=worksteal"])

    # Add common options
    cmd.extend(["--tb=short", "--maxfail=5", "-q"])

    start_time = time.time()
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    elapsed_time = time.time() - start_time

    print(f"\n{group['name']} completed in {elapsed_time:.1f} seconds")
    return result.returncode

def run_all_groups_sequential():
    """Run all test groups sequentially."""
    print("Running all test groups sequentially...")
    total_start = time.time()
    results = {}

    for group_key in TEST_GROUPS:
        result = run_test_group(group_key)
        results[group_key] = result

    total_time = time.time() - total_start

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    for group_key, result in results.items():
        status = "✓ PASSED" if result == 0 else "✗ FAILED"
        print(f"{TEST_GROUPS[group_key]['name']:30} {status}")

    print(f"\nTotal execution time: {total_time:.1f} seconds")

    # Return failure if any group failed
    return 1 if any(r != 0 for r in results.values()) else 0

def run_all_groups_parallel():
    """Run all test groups in parallel."""
    print("Running all test groups in parallel...")
    total_start = time.time()

    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_test_group, group_key): group_key
            for group_key in TEST_GROUPS
        }

        results = {}
        for future in as_completed(futures):
            group_key = futures[future]
            try:
                result = future.result()
                results[group_key] = result
            except Exception as e:
                print(f"Error running {group_key}: {e}")
                results[group_key] = 1

    total_time = time.time() - total_start

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    for group_key in TEST_GROUPS:
        if group_key in results:
            status = "✓ PASSED" if results[group_key] == 0 else "✗ FAILED"
            print(f"{TEST_GROUPS[group_key]['name']:30} {status}")

    print(f"\nTotal execution time: {total_time:.1f} seconds")

    # Return failure if any group failed
    return 1 if any(r != 0 for r in results.values()) else 0

def list_groups():
    """List all available test groups."""
    print("\nAvailable Test Groups:")
    print("="*60)
    for group_key, group in TEST_GROUPS.items():
        print(f"\n{group_key}:")
        print(f"  Name: {group['name']}")
        print(f"  Estimated Time: {group['estimated_time']}")
        print(f"  Markers: {group['markers']}")
        print(f"  Workers: {group['workers']}")
    print("="*60)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_groups.py <command>")
        print("Commands:")
        print("  all          - Run all groups sequentially")
        print("  parallel     - Run all groups in parallel")
        print("  list         - List all test groups")
        print("  <group_key>  - Run a specific group (e.g., group1_unit)")
        return 1

    command = sys.argv[1]

    if command == "all":
        return run_all_groups_sequential()
    elif command == "parallel":
        return run_all_groups_parallel()
    elif command == "list":
        list_groups()
        return 0
    elif command in TEST_GROUPS:
        return run_test_group(command)
    else:
        print(f"Unknown command: {command}")
        print("Use 'python test_groups.py list' to see available groups")
        return 1

if __name__ == "__main__":
    sys.exit(main())
