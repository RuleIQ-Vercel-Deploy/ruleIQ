#!/bin/bash
# Execution script for debug-channel branches (2, 3, 4)

# Function to setup debug channel
setup_channel() {
    local CHANNEL_NUM=$1
    local WORKTREE="/home/omar/Documents/ruleIQ.worktrees/Claude-${CHANNEL_NUM}"
    local BRANCH="debug-channel-${CHANNEL_NUM}"

    echo "🔧 Setting up Debug Channel ${CHANNEL_NUM}"
    cd "$WORKTREE"

    # Update branch
    echo "📥 Pulling latest changes..."
    git pull origin main

    # Run initial analysis
    echo "🔍 Running SonarCloud analysis..."
    doppler run -- sonar-scanner -Dsonar.branch.name=$BRANCH

    case $CHANNEL_NUM in
        2)
            echo "📋 Channel 2: Code Smells Part 1"
            cat << 'EOF'
CLAUDE INSTRUCTIONS FOR CHANNEL 2:
1. Focus on first 10 code smell issues
2. Fix duplicated code blocks
3. Organize imports properly
4. Remove dead code
5. Run tests after each fix
EOF
            ;;
        3)
            echo "📋 Channel 3: Code Smells Part 2"
            cat << 'EOF'
CLAUDE INSTRUCTIONS FOR CHANNEL 3:
1. Focus on next 10 code smell issues
2. Reduce function complexity
3. Fix naming conventions
4. Improve error handling
5. Run tests after each fix
EOF
            ;;
        4)
            echo "📋 Channel 4: Minor Issues"
            cat << 'EOF'
CLAUDE INSTRUCTIONS FOR CHANNEL 4:
1. Fix remaining code smells
2. Improve documentation
3. Ensure code formatting consistency
4. Improve test coverage
5. Run full test suite
EOF
            ;;
    esac

    echo "🚀 Channel ${CHANNEL_NUM} ready for fixes."
}

# Run setup for all channels if no argument, or specific channel if provided
if [ $# -eq 0 ]; then
    for i in 2 3 4; do
        setup_channel $i
        echo "---"
    done
else
    setup_channel $1
fi