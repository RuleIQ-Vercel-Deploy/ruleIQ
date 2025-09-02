#!/usr/bin/env python3
"""Run tests directory by directory to isolate issues."""

from __future__ import annotations

import subprocess
import os
from pathlib import Path
from typing import Dict, List


def find_test_directories():
    """Find all directories containing test files."""
    test_dirs = set()

    # Find all test files
    for pattern in ["test_*.py", "*_test.py"]:
        for test_file in Path(".").rglob(pattern):
            # Skip venv and cache
            if ".venv" in str(test_file) or "__pycache__" in str(test_file):
                continue
            # Add parent directory
            test_dirs.add(test_file.parent)

    return sorted(test_dirs)


def run_tests_in_directory(directory: Path) -> Dict:
    """Run tests in a single directory."""
    print(f"\n{'='*60}")
    print(f"Testing: {directory}")
    print("=" * 60)

    result = subprocess.run(
        ["python", "-m", "pytest", str(directory), "-v", "--tb=short", "--co", "-q"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Parse output
    output = result.stdout + result.stderr

    stats = {
        "directory": str(directory),
        "collected": 0,
        "errors": 0,
        "return_code": result.returncode,
    }

    # Extract collected count
    if "collected" in output:
        for line in output.split("\n"):
            if "collected" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "collected" and i + 1 < len(parts):
                        try:
                            stats["collected"] = int(parts[i + 1])
                        except (ValueError, KeyError, IndexError):
                            pass
                    if "error" in line.lower():
                        if "/" in line:
                            error_part = line.split("/")[-1].strip()
                            if "error" in error_part:
                                try:
                                    stats["errors"] = int(error_part.split()[0])
                                except (ValueError, KeyError, IndexError):
                                    pass

    print(f"Collected: {stats['collected']} tests")
    print(f"Errors: {stats['errors']}")
    print(f"Return code: {stats['return_code']}")

    if stats["errors"] > 0:
        print("\nError details:")
        print(output[:500])

    return stats


def main():
    """Run tests directory by directory."""
    print("Finding test directories...")
    test_dirs = find_test_directories()
    print(f"Found {len(test_dirs)} directories with tests")

    all_stats = []
    total_collected = 0
    total_errors = 0

    for directory in test_dirs:
        stats = run_tests_in_directory(directory)
        all_stats.append(stats)
        total_collected += stats["collected"]
        total_errors += stats["errors"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total directories: {len(test_dirs)}")
    print(f"Total tests collected: {total_collected}")
    print(f"Total collection errors: {total_errors}")

    print("\nDirectories with errors:")
    for stats in all_stats:
        if stats["errors"] > 0:
            print(f"  - {stats['directory']}: {stats['errors']} errors")

    print("\nDirectories with successful collection:")
    for stats in all_stats:
        if stats["errors"] == 0 and stats["collected"] > 0:
            print(f"  - {stats['directory']}: {stats['collected']} tests")


if __name__ == "__main__":
    main()
