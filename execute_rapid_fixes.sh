#!/bin/bash
# Execute rapid test fixes to achieve 80% pass rate

set -e  # Exit on error

echo "=================================================="
echo "🚀 RAPID TEST FIX EXECUTION - TARGET: 80% PASS"
echo "=================================================="
echo "Current: ~35 tests passing (1.4%)"
echo "Target: 2,040 tests passing (80%)"
echo "Gap: ~2,005 tests to fix"
echo ""

cd /home/omar/Documents/ruleIQ

# Step 1: Apply mass fixes
echo "📋 Step 1: Applying mass test fixes..."
python3 apply_mass_test_fixes.py

# Step 2: Run systematic fixer
echo ""
echo "📋 Step 2: Running systematic test fixer..."
python3 fix_tests_systematic.py

# Step 3: Run QA mission
echo ""
echo "📋 Step 3: Running QA mission controller..."
python3 qa_mission_80_percent.py

# Step 4: Quick verification
echo ""
echo "📋 Step 4: Verifying improvements..."
echo "Collection check:"
python3 -m pytest --co -q | grep -E "collected|error" || true

echo ""
echo "Quick test run (first 100 tests):"
python3 -m pytest --maxfail=100 -q --tb=line 2>&1 | head -30

echo ""
echo "=================================================="
echo "✅ Rapid fix execution complete!"
echo ""
echo "To verify full results, run:"
echo "  pytest -v                  # Full verbose test"
echo "  pytest --lf                # Run last failed"
echo "  pytest --tb=short -x       # Debug first failure"
echo "=================================================="