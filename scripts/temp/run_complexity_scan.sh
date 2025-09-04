#!/bin/bash
# Run complexity scan and refactoring

echo "🔍 Running RuleIQ Complexity Scanner..."
echo "======================================="

cd /home/omar/Documents/ruleIQ

# Make scripts executable
chmod +x scripts/sonar/*.py

# Run the complexity scanner
python3 scripts/sonar/refactor_complexity.py

echo ""
echo "📊 Scan complete! Check refactoring_tasks.txt for details."
echo ""
echo "To start refactoring, run:"
echo "  python3 scripts/sonar/aggressive_refactor.py"