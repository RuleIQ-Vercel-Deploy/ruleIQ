#!/bin/bash
# Quick script to exit Docker terminal and open local terminal

echo "====================================="
echo "Switching to Local Terminal"
echo "====================================="

if [ -f /.dockerenv ]; then
    echo "✅ Currently in Docker container"
    echo "📝 Instructions to switch to local:"
    echo "   1. Close this terminal (type 'exit' or click the trash icon)"
    echo "   2. Open a new terminal with Ctrl+Shift+\` "
    echo "   3. Select 'RuleIQ Local' if prompted for terminal profile"
    echo ""
    echo "To prevent Docker terminal from opening:"
    echo "   - In Docker extension, right-click running containers"
    echo "   - Select 'Stop' on any ruleIQ containers"
else
    echo "✅ Already in local environment"
    cd /home/omar/Documents/ruleIQ
    source .venv/bin/activate 2>/dev/null && echo "✅ Virtual environment activated"
    echo "📁 Working directory: $(pwd)"
fi
