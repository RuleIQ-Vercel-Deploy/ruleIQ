#!/bin/bash
# Script to find and categorize test issues

echo "=== Finding test issues in ruleIQ ==="

# Find all test files
echo -e "\n1. Total test files:"
find tests -name "test_*.py" -type f | wc -l

# Check for common issues
echo -e "\n2. Files importing missing modules:"
grep -r "from utils.auth import" tests/ 2>/dev/null | head -5

echo -e "\n3. Files with async issues:"
grep -r "async def test_" tests/ | head -5

echo -e "\n4. Files importing database models:"
grep -r "from database import" tests/ | head -5

echo -e "\n5. Running basic import check on test files..."
for file in $(find tests -name "test_*.py" -type f | head -10); do
    echo -n "Checking $file: "
    .venv/bin/python -c "import sys; sys.path.insert(0, '.'); exec(open('$file').read())" 2>&1 | head -1 || echo "OK"
done

echo -e "\n6. Checking for fixture issues:"
grep -r "@pytest.fixture" tests/ | wc -l
echo "Total fixtures defined"

echo -e "\n7. Looking for undefined fixtures in tests:"
grep -r "def test_.*(" tests/ | grep -v "self" | head -10

echo -e "\n8. Trying a simple pytest collection:"
.venv/bin/python -m pytest --collect-only --quiet 2>&1 | grep -E "ERROR|FAILED|cannot import" | head -20