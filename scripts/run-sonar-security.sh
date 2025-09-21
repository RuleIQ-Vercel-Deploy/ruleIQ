#!/bin/bash
# Execution script for sonar-security-fixes branch

WORKTREE="/home/omar/Documents/ruleIQ.worktrees/sonar-security"
BRANCH="sonar-security-fixes"

echo "🔒 Starting SonarCloud Security Fixes"
cd "$WORKTREE"

# Update branch
echo "📥 Pulling latest changes..."
git pull origin main

# Run initial analysis
echo "🔍 Running SonarCloud analysis..."
doppler run -- sonar-scanner -Dsonar.branch.name=$BRANCH

# Focus on security issues
echo "🛡️ Fixing Security Issues..."
echo "Priority targets:"
echo "  - Security hotspots"
echo "  - SQL injection vulnerabilities"
echo "  - XSS vulnerabilities"
echo "  - Authentication issues"

# Instructions for Claude instance
cat << 'EOF'

CLAUDE INSTRUCTIONS FOR SECURITY FIXES:
1. Review all security hotspots in SonarCloud
2. Search for SQL injection risks:
   rg "f-string.*SELECT|f-string.*INSERT|f-string.*UPDATE|f-string.*DELETE" --type py
   rg "\.format.*SELECT|\.format.*INSERT" --type py
3. Check for XSS vulnerabilities:
   rg "dangerouslySetInnerHTML" frontend/ --type tsx
   rg "innerHTML" frontend/ --type ts --type tsx
4. Review authentication:
   rg "jwt|token|auth|password" --type py --type ts
5. Fix sensitive data exposure:
   rg "console.log.*password|console.log.*token|console.log.*secret" --type ts
6. Run security tests after fixes
7. Document all security improvements

EOF

echo "🚀 Ready for fixes. Claude instance can now proceed."