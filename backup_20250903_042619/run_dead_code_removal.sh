#!/bin/bash

cd /home/omar/Documents/ruleIQ

echo "=================================================="
echo "DEAD CODE REMOVAL - P1 TASK EXECUTION"
echo "Task ID: 2f2f8b57 (merged with d3d23042)"
echo "Priority: P1 - CRITICAL"
echo "=================================================="
echo ""

# First, run the analysis
echo "📊 Running dead code analysis..."
python3 scripts/execute_dead_code_analysis.py

echo ""
echo "=================================================="
echo "EXECUTING REMOVAL (DRY RUN)"
echo "=================================================="
echo ""

# Run removal in dry-run mode
python3 scripts/dead_code_removal.py

echo ""
echo "=================================================="
echo "READY FOR ACTUAL REMOVAL"
echo "=================================================="
echo ""
echo "To execute actual removal, run:"
echo "  python3 scripts/dead_code_removal.py --execute"
echo ""
echo "This will:"
echo "  1. Create a backup"
echo "  2. Remove all identified dead code"
echo "  3. Run tests to verify nothing broke"
echo "  4. Generate a detailed report"
echo ""