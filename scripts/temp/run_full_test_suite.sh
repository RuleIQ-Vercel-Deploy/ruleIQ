#!/bin/bash

# Quick test runner
echo "Running comprehensive test suite setup and execution..."
.venv/bin/python install_and_test.py 2>&1 | tee full_test_run.log

# Extract summary
echo ""
echo "=== QUICK SUMMARY ==="
grep -E "(Tests collectible|passed|failed|error)" full_test_run.log | tail -5

# Check if we need to see specific failures
if grep -q "FAILED\|ERROR" full_test_run.log; then
    echo ""
    echo "=== TOP FAILURES ==="
    grep "FAILED\|ERROR" full_test_run.log | head -10
fi

echo ""
echo "Full output saved to: full_test_run.log"