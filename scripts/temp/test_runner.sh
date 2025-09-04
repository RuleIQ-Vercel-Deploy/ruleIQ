#!/bin/bash
# Script to run tests and get coverage report

echo "================================"
echo "Running RuleIQ Test Suite"
echo "================================"

# Run the bulk fix script first
echo "1. Applying bulk fixes to test files..."
.venv/bin/python bulk_fix_tests.py

echo ""
echo "2. Running pytest with coverage..."
.venv/bin/python -m pytest \
    -v \
    --tb=short \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --maxfail=5 \
    -x \
    2>&1 | tee test_output.log

# Extract key metrics
echo ""
echo "================================"
echo "Test Summary"
echo "================================"

# Count results
PASSED=$(grep -c "PASSED" test_output.log || echo "0")
FAILED=$(grep -c "FAILED" test_output.log || echo "0")
SKIPPED=$(grep -c "SKIPPED" test_output.log || echo "0")
ERRORS=$(grep -c "ERROR" test_output.log || echo "0")

echo "✓ Passed: $PASSED"
echo "✗ Failed: $FAILED"
echo "⊘ Skipped: $SKIPPED"
echo "⚠ Errors: $ERRORS"

# Get coverage
COVERAGE=$(grep "TOTAL" test_output.log | awk '{print $NF}' || echo "0%")
echo ""
echo "Coverage: $COVERAGE"

# Check if we meet 70% target
COVERAGE_NUM=$(echo $COVERAGE | tr -d '%')
if [ "$COVERAGE_NUM" -ge "70" ]; then
    echo "✅ Coverage target (70%) achieved!"
else
    echo "❌ Coverage below 70% target"
fi

echo ""
echo "Full output saved to test_output.log"
echo "HTML coverage report: htmlcov/index.html"