#!/bin/bash
# Execute test fixes to achieve 80% pass rate

echo "🚀 EXECUTING RAPID TEST FIXES FOR RULEIQ"
echo "=========================================="
echo "Target: 80% pass rate (2,040/2,550 tests)"
echo ""

# Change to project directory
cd /home/omar/Documents/ruleIQ

# Step 1: Run the systematic fixer first
echo "📋 Step 1: Running systematic test fixer..."
python3 fix_tests_systematic.py

# Step 2: Run the QA mission controller
echo ""
echo "📋 Step 2: Running QA mission controller..."
python3 qa_mission_80_percent.py

# Step 3: Quick verification of improvements
echo ""
echo "📋 Step 3: Verifying test collection..."
python3 -m pytest --co -q | grep "collected"

# Step 4: Run a sample of tests to check pass rate
echo ""
echo "📋 Step 4: Running sample test batch (first 100)..."
python3 -m pytest --maxfail=100 -q --tb=no 2>&1 | head -20

echo ""
echo "=========================================="
echo "✅ Test fix execution complete!"
echo "Run 'pytest -v' for full test results"