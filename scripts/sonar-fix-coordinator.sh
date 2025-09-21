#!/bin/bash
# Master Coordinator Script for Parallel SonarCloud Fixes
# This script coordinates all Claude instances to work in parallel

set -e

MAIN_DIR="/home/omar/Documents/ruleIQ"
SCRIPT_DIR="${MAIN_DIR}/scripts"

echo "🚀 RuleIQ SonarCloud Fix Coordinator"
echo "======================================"
echo ""

# Function to check worktree status
check_worktree() {
    local worktree=$1
    local branch=$2
    if [ -d "$worktree" ]; then
        echo "✅ $branch: Ready at $worktree"
        cd "$worktree"
        git status --short
    else
        echo "❌ $branch: Worktree not found at $worktree"
        return 1
    fi
}

# Function to launch Claude instance instruction
launch_claude() {
    local worktree=$1
    local branch=$2
    local script=$3

    echo ""
    echo "📋 Instructions for Claude instance in $branch:"
    echo "================================================"
    echo "1. Open a new Claude Code instance"
    echo "2. Navigate to: cd $worktree"
    echo "3. Run: $script"
    echo "4. Follow the instructions in the script output"
    echo "5. Focus on your assigned SonarCloud issues only"
    echo ""
}

# Verify all worktrees
echo "🔍 Verifying all worktrees..."
echo "------------------------------"

check_worktree "/home/omar/Documents/ruleIQ.worktrees/sonar-backend" "sonar-backend-fixes"
check_worktree "/home/omar/Documents/ruleIQ.worktrees/sonar-frontend" "sonar-frontend-fixes"
check_worktree "/home/omar/Documents/ruleIQ.worktrees/sonar-security" "sonar-security-fixes"
check_worktree "/home/omar/Documents/ruleIQ.worktrees/Claude-2" "debug-channel-2"
check_worktree "/home/omar/Documents/ruleIQ.worktrees/Claude-3" "debug-channel-3"
check_worktree "/home/omar/Documents/ruleIQ.worktrees/Claude-4" "debug-channel-4"

echo ""
echo "🎯 Launch Instructions for Each Claude Instance"
echo "=============================================="

# High Priority
echo ""
echo "HIGH PRIORITY - Launch These First:"
launch_claude "/home/omar/Documents/ruleIQ.worktrees/sonar-security" "sonar-security-fixes" "bash ${SCRIPT_DIR}/run-sonar-security.sh"
launch_claude "/home/omar/Documents/ruleIQ.worktrees/sonar-backend" "sonar-backend-fixes" "bash ${SCRIPT_DIR}/run-sonar-backend.sh"
launch_claude "/home/omar/Documents/ruleIQ.worktrees/sonar-frontend" "sonar-frontend-fixes" "bash ${SCRIPT_DIR}/run-sonar-frontend.sh"

# Medium Priority
echo ""
echo "MEDIUM PRIORITY - Launch After High Priority:"
launch_claude "/home/omar/Documents/ruleIQ.worktrees/Claude-2" "debug-channel-2" "bash ${SCRIPT_DIR}/run-debug-channels.sh 2"
launch_claude "/home/omar/Documents/ruleIQ.worktrees/Claude-3" "debug-channel-3" "bash ${SCRIPT_DIR}/run-debug-channels.sh 3"

# Low Priority
echo ""
echo "LOW PRIORITY - Launch Last:"
launch_claude "/home/omar/Documents/ruleIQ.worktrees/Claude-4" "debug-channel-4" "bash ${SCRIPT_DIR}/run-debug-channels.sh 4"

# Monitoring section
echo ""
echo "📊 Monitoring Progress"
echo "====================="
echo ""
echo "Run these commands to monitor progress:"
echo ""
echo "# Check all branch statuses:"
echo "git worktree list"
echo ""
echo "# Monitor SonarCloud analysis:"
echo "watch 'doppler run -- sonar-scanner -Dsonar.branch.name=main 2>&1 | grep -E \"issues|bugs|vulnerabilities\"'"
echo ""
echo "# View task assignments:"
echo "cat ${MAIN_DIR}/SONAR_FIX_ASSIGNMENTS.md"
echo ""

# Merge coordination
echo ""
echo "🔄 Merge Coordination"
echo "===================="
echo ""
echo "After all fixes are complete, merge in this order:"
echo "1. git merge origin/sonar-security-fixes  # CRITICAL - First"
echo "2. git merge origin/sonar-backend-fixes   # Major bugs"
echo "3. git merge origin/sonar-frontend-fixes  # TypeScript issues"
echo "4. git merge origin/debug-channel-2       # Code smells pt 1"
echo "5. git merge origin/debug-channel-3       # Code smells pt 2"
echo "6. git merge origin/debug-channel-4       # Minor issues"
echo ""

echo "✨ Coordinator ready! Launch your Claude instances now."