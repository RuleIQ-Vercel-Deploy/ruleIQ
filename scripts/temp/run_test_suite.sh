#!/bin/bash
# Master script to fix and run the test suite

echo "================================"
echo "RULEIQ TEST SUITE RUNNER"
echo "Target: 70% Coverage"
echo "================================"

# Make all scripts executable
chmod +x *.py
chmod +x *.sh

# Step 1: Execute comprehensive fixes
echo -e "\n📝 Executing comprehensive test fixes..."
.venv/bin/python execute_test_fixes.py

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n✅ TEST SUITE SUCCESSFUL - 70% Coverage Achieved!"
else
    echo -e "\n⚠️ Coverage below 70% - Additional work needed"
    
    # Show quick stats
    echo -e "\nQuick Test Stats:"
    .venv/bin/python -c "
import subprocess
result = subprocess.run(['.venv/bin/python', '-m', 'pytest', '--co', '-q'], 
                       capture_output=True, text=True)
for line in result.stdout.splitlines()[-5:]:
    print(line)
"
fi

echo -e "\n================================"
echo "Test suite execution complete"
echo "HTML Report: htmlcov/index.html"
echo "================================"