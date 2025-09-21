#!/bin/bash
# Execution script for sonar-frontend-fixes branch

WORKTREE="/home/omar/Documents/ruleIQ.worktrees/sonar-frontend"
BRANCH="sonar-frontend-fixes"

echo "🎨 Starting SonarCloud Frontend Fixes"
cd "$WORKTREE"

# Update branch
echo "📥 Pulling latest changes..."
git pull origin main

# Run initial analysis
echo "🔍 Running SonarCloud analysis..."
doppler run -- sonar-scanner -Dsonar.branch.name=$BRANCH

# Focus on frontend TypeScript issues
echo "📘 Fixing TypeScript frontend issues..."
echo "Priority targets:"
echo "  - frontend/app/api/pusher/auth/route.ts"
echo "  - frontend/app/api/pusher/trigger/route.ts"
echo "  - Unused imports and variables"
echo "  - Component complexity"

# Instructions for Claude instance
cat << 'EOF'

CLAUDE INSTRUCTIONS FOR FRONTEND FIXES:
1. Fix unused variables in Pusher routes
2. Search and fix all unused imports:
   rg "^import.*from" frontend/ --type ts --type tsx | grep -E "unused"
3. Fix nested ternary operators:
   rg "\?" frontend/ --type ts --type tsx | grep "\?"
4. Remove unnecessary type assertions:
   rg " as " frontend/ --type ts --type tsx
5. Run tests after each fix: cd frontend && npm test
6. Run type check: cd frontend && npm run typecheck
7. Commit frequently with descriptive messages

EOF

echo "🚀 Ready for fixes. Claude instance can now proceed."