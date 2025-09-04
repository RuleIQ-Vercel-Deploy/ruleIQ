#!/bin/bash

echo "==================================================================================="
echo "⚡ SONARCLOUD GRADE IMPROVEMENT - AGGRESSIVE REFACTORING"
echo "==================================================================================="
echo "Starting at: $(date)"
echo ""

# Navigate to project directory
cd /home/omar/Documents/ruleIQ

echo "📊 Current Status:"
echo "- Only 2 of 816 functions refactored (0.25%)"
echo "- Current Grade: E"
echo "- Target: Grade D or better by end of day"
echo ""

echo "🚀 Phase 1: Running aggressive batch refactoring..."
python3 scripts/aggressive_batch_refactor.py

echo ""
echo "✅ Phase 1 Complete"
echo ""

echo "🧪 Phase 2: Running quick test validation..."
# Run a subset of tests to verify nothing is broken
python3 -m pytest tests/test_minimal.py -q --tb=no 2>/dev/null

echo ""
echo "📈 Phase 3: Checking results..."
if [ -f "aggressive_refactoring_report.json" ]; then
    echo "Report generated. Analyzing..."
    python3 -c "
import json
with open('aggressive_refactoring_report.json', 'r') as f:
    report = json.load(f)
    print(f'✅ Functions refactored: {report.get(\"functions_refactored\", 0)}')
    print(f'📁 Files modified: {report.get(\"files_modified\", 0)}')
    print(f'📊 Progress: {report.get(\"estimated_improvement\", {}).get(\"progress_percentage\", 0):.1f}%')
"
fi

echo ""
echo "==================================================================================="
echo "Completed at: $(date)"
echo ""

echo "🎯 Next Steps:"
echo "1. Review modified files for correctness"
echo "2. Run full test suite if needed"
echo "3. Commit changes and push to trigger SonarCloud analysis"
echo "4. Monitor SonarCloud dashboard for grade improvement"
echo ""
echo "To run another batch with lower threshold:"
echo "  python3 scripts/aggressive_batch_refactor.py"
echo "==================================================================================="