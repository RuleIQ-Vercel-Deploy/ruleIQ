#!/bin/bash
# Run the fix script and then test

echo "================================"
echo "RuleIQ Test Fix and Run"
echo "================================"

# Make scripts executable
chmod +x fix_critical_tests.py
chmod +x bulk_fix_tests.py
chmod +x analyze_test_errors.py

# Run critical fixes
echo "Step 1: Applying critical test fixes..."
.venv/bin/python fix_critical_tests.py

echo ""
echo "Step 2: Running bulk fixes..."
.venv/bin/python bulk_fix_tests.py

echo ""
echo "Step 3: Analyzing remaining errors..."
.venv/bin/python analyze_test_errors.py

echo ""
echo "Step 4: Running pytest collection test..."
.venv/bin/python -m pytest --collect-only --quiet 2>&1 | head -20

echo ""
echo "Step 5: Running actual tests with coverage..."
.venv/bin/python -m pytest \
    -v \
    --tb=short \
    --cov=. \
    --cov-report=term \
    --maxfail=10 \
    -x \
    2>&1 | tee pytest_output.log

# Show summary
echo ""
echo "================================"
echo "Test Summary"
echo "================================"

# Extract stats if available
if [ -f pytest_output.log ]; then
    echo "Test Results:"
    grep -E "passed|failed|skipped|error" pytest_output.log | tail -5
    
    echo ""
    echo "Coverage:"
    grep "TOTAL" pytest_output.log || echo "Coverage data not available"
fi

echo ""
echo "Fix and test run complete!"