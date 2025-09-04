#!/bin/bash

echo "=================================================="
echo "QUICK DEAD CODE SCAN FOR RULEIQ"
echo "=================================================="

cd /home/omar/Documents/ruleIQ

echo ""
echo "📦 PYTHON ANALYSIS"
echo "--------------------------------------------------"

# Check for Celery remnants
echo "🔍 Checking for Celery remnants..."
grep -r "celery" --include="*.py" . 2>/dev/null | grep -v "venv" | grep -v "__pycache__" | head -20

echo ""
echo "🔍 Checking for commented code blocks in Python..."
find . -name "*.py" -type f ! -path "./venv/*" ! -path "./__pycache__/*" -exec grep -l "^#.*def \|^#.*class \|^#.*import " {} \; | head -10

echo ""
echo "🔍 Checking for TODO/FIXME/HACK comments..."
grep -r "TODO\|FIXME\|HACK\|XXX" --include="*.py" . 2>/dev/null | grep -v "venv" | wc -l
echo "Total TODO/FIXME/HACK comments found"

echo ""
echo "📦 JAVASCRIPT/TYPESCRIPT ANALYSIS"
echo "--------------------------------------------------"

echo "🔍 Checking for unused imports in frontend..."
cd frontend 2>/dev/null || echo "Frontend directory not accessible"

# Check for console.log statements (should be removed in production)
echo "🔍 Checking for console.log statements..."
grep -r "console.log" --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v "node_modules" | grep -v ".next" | wc -l
echo "console.log statements found"

echo ""
echo "🔍 Checking for commented JSX/TSX code..."
grep -r "^[[:space:]]*//.*<\|^[[:space:]]*/\*.*<" --include="*.jsx" --include="*.tsx" . 2>/dev/null | grep -v "node_modules" | head -10

cd ..

echo ""
echo "📦 CONFIGURATION ANALYSIS"
echo "--------------------------------------------------"

echo "🔍 Checking .env files for unused variables..."
if [ -f .env ]; then
    echo "Variables defined in .env:"
    grep -c "^[A-Z]" .env
fi

echo ""
echo "🔍 Checking for duplicate dependencies..."
if [ -f requirements.txt ]; then
    echo "Python dependencies:"
    sort requirements.txt | uniq -d | head -5
fi

echo ""
echo "📦 FILE ANALYSIS"
echo "--------------------------------------------------"

echo "🔍 Finding empty Python files..."
find . -name "*.py" -type f -empty ! -path "./venv/*" | head -10

echo ""
echo "🔍 Finding very large files (potential cleanup targets)..."
find . -type f -size +500k ! -path "./venv/*" ! -path "./node_modules/*" ! -path "./.git/*" | head -10

echo ""
echo "🔍 Finding old backup files..."
find . -name "*.bak" -o -name "*.backup" -o -name "*.old" -o -name "*~" | head -10

echo ""
echo "=================================================="
echo "QUICK SCAN COMPLETE"
echo "==================================================">