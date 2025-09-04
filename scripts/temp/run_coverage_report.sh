#!/bin/bash

# Run Coverage Report Script
# QA Specialist - RuleIQ P3 Task

echo "==================================="
echo "RuleIQ Test Coverage Report"
echo "Date: $(date)"
echo "==================================="

# Ensure we're in the project root
cd /home/omar/Documents/ruleIQ

# Activate virtual environment
source venv_linux/bin/activate

# Install coverage tools if not already installed
pip install pytest-cov pytest-html pytest-json-report --quiet

# Clear previous coverage data
rm -f .coverage
rm -rf htmlcov
rm -f coverage.xml
rm -f coverage.json

# Run tests with coverage
echo ""
echo "Running tests with coverage analysis..."
echo "-----------------------------------"

# Run tests with multiple output formats
pytest tests/ \
    --cov=services \
    --cov=api \
    --cov=utils \
    --cov=database \
    --cov=middleware \
    --cov=monitoring \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml \
    --cov-report=json:coverage.json \
    --tb=short \
    --maxfail=10 \
    -v 2>&1 | tee test_results.log

# Extract coverage percentage
COVERAGE=$(python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])" 2>/dev/null || echo "0")

echo ""
echo "==================================="
echo "Coverage Summary"
echo "==================================="
echo "Overall Coverage: ${COVERAGE}%"
echo ""

# Show coverage by module
echo "Coverage by Module:"
echo "-----------------------------------"
python -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    for file in sorted(data['files'].keys())[:20]:  # Show top 20 files
        cov = data['files'][file]['summary']['percent_covered']
        print(f'{file:60} {cov:>6.1f}%')
" 2>/dev/null || echo "Unable to parse coverage data"

echo ""
echo "==================================="
echo "Test Statistics"
echo "==================================="

# Count test results
PASSED=$(grep -c "PASSED" test_results.log 2>/dev/null || echo "0")
FAILED=$(grep -c "FAILED" test_results.log 2>/dev/null || echo "0")
ERRORS=$(grep -c "ERROR" test_results.log 2>/dev/null || echo "0")

echo "Tests Passed: $PASSED"
echo "Tests Failed: $FAILED"
echo "Tests Errors: $ERRORS"

echo ""
echo "HTML Report: file:///home/omar/Documents/ruleIQ/htmlcov/index.html"
echo "XML Report: coverage.xml (for CI/CD integration)"
echo "JSON Report: coverage.json (for detailed analysis)"

# Check if we meet the target
if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
    echo ""
    echo "✅ SUCCESS: Target coverage of 80% achieved!"
else
    echo ""
    echo "⚠️  Current coverage: ${COVERAGE}%"
    echo "📈 Target coverage: 80%"
    echo "Gap to target: $(echo "80 - $COVERAGE" | bc)%"
fi

echo ""
echo "==================================="