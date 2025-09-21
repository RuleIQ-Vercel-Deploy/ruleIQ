#!/bin/bash
# Execution script for sonar-backend-fixes branch

WORKTREE="/home/omar/Documents/ruleIQ.worktrees/sonar-backend"
BRANCH="sonar-backend-fixes"

echo "🔧 Starting SonarCloud Backend Fixes"
cd "$WORKTREE"

# Update branch
echo "📥 Pulling latest changes..."
git pull origin main

# Run initial analysis
echo "🔍 Running SonarCloud analysis..."
doppler run -- sonar-scanner -Dsonar.branch.name=$BRANCH

# Focus on backend Python issues
echo "🐍 Fixing Python backend issues..."
echo "Priority targets:"
echo "  - api/routers/chat.py"
echo "  - Type hints and return types"
echo "  - Async function patterns"
echo "  - Cognitive complexity"

# Instructions for Claude instance
cat << 'EOF'

CLAUDE INSTRUCTIONS FOR BACKEND FIXES:
1. Fix the critical bug in api/routers/chat.py (return type issue)
2. Search for all Python files with typing issues using:
   rg "-> None" --type py
   rg "Optional\[" --type py
3. Fix async function patterns:
   rg "async def" --type py | grep -v "await"
4. Reduce function complexity where SonarCloud indicates
5. Run tests after each fix: python -m pytest
6. Commit frequently with descriptive messages

EOF

echo "🚀 Ready for fixes. Claude instance can now proceed."