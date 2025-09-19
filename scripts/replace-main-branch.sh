#!/bin/bash

# Replace Main Branch Script
# CRITICAL: This script replaces the unsafe main branch with the-bmad-experiment
# Author: RuleIQ Team
# Date: September 2025

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SAFE_BRANCH="the-bmad-experiment"
TARGET_BRANCH="main"
BACKUP_PREFIX="main-backup"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Main Branch Replacement Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to confirm action (mandatory - exits on no)
confirm() {
    read -p "$1 (yes/no): " -r response
    echo
    case "${response,,}" in
        yes|y)
            return 0
            ;;
        *)
            echo -e "${YELLOW}Operation cancelled by user${NC}"
            exit 1
            ;;
    esac
}

# Function for optional confirmation (doesn't exit on no)
confirm_optional() {
    read -p "$1 (yes/no): " -r response
    echo
    case "${response,,}" in
        yes|y)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to check git status
check_git_status() {
    echo -e "${YELLOW}Checking git status...${NC}"
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo -e "${RED}ERROR: You have uncommitted changes${NC}"
        git status -s
        echo -e "${YELLOW}Please commit or stash your changes before proceeding${NC}"
        exit 1
    fi
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "${GREEN}Current branch: $CURRENT_BRANCH${NC}"
}

# Function to create backup
create_backup() {
    echo -e "${YELLOW}Creating backup of main branch...${NC}"
    
    # Create timestamp
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BACKUP_BRANCH="${BACKUP_PREFIX}-${TIMESTAMP}"
    
    # Checkout main and create backup
    if ! git checkout $TARGET_BRANCH 2>/dev/null; then
        echo -e "${YELLOW}Main branch not found locally. Fetching from remote...${NC}"
        git fetch origin $TARGET_BRANCH:$TARGET_BRANCH || {
            echo -e "${RED}ERROR: Could not fetch $TARGET_BRANCH from origin${NC}"
            exit 1
        }
        # Retry checkout after fetch
        git checkout $TARGET_BRANCH || {
            echo -e "${RED}ERROR: Could not checkout $TARGET_BRANCH after fetch${NC}"
            exit 1
        }
    fi
    
    git checkout -b $BACKUP_BRANCH
    echo -e "${GREEN}Created backup branch: $BACKUP_BRANCH${NC}"
    
    # Push backup to remote
    echo -e "${YELLOW}Pushing backup to remote...${NC}"
    git push origin $BACKUP_BRANCH
    echo -e "${GREEN}Backup pushed to remote: origin/$BACKUP_BRANCH${NC}"
    
    # Return to safe branch
    git checkout $SAFE_BRANCH
}

# Function to replace main branch
replace_main() {
    echo -e "${YELLOW}Replacing main branch with $SAFE_BRANCH...${NC}"
    
    # Ensure we're on the safe branch
    git checkout $SAFE_BRANCH || {
        echo -e "${RED}ERROR: Could not checkout $SAFE_BRANCH${NC}"
        exit 1
    }
    
    # Verify we're on the correct branch before proceeding
    CURRENT=$(git branch --show-current)
    if [[ "$CURRENT" != "$SAFE_BRANCH" ]]; then
        echo -e "${RED}ERROR: Not on $SAFE_BRANCH branch (currently on $CURRENT)${NC}"
        exit 1
    fi
    
    # Force main to match safe branch
    git branch -f $TARGET_BRANCH $SAFE_BRANCH
    echo -e "${GREEN}Local main branch updated${NC}"
}

# Function to push changes
push_changes() {
    echo -e "${YELLOW}Pushing updated main to remote...${NC}"
    echo -e "${RED}WARNING: This will force-push to origin/main${NC}"
    
    confirm "Are you absolutely sure you want to force-push to main?"
    
    # Try force-with-lease first (safer)
    git push origin $TARGET_BRANCH --force-with-lease 2>/dev/null || {
        echo -e "${YELLOW}force-with-lease failed, trying regular force...${NC}"
        confirm "force-with-lease failed. Use regular force push?"
        git push origin $TARGET_BRANCH --force
    }
    
    echo -e "${GREEN}Successfully pushed new main to remote${NC}"
}

# Function to verify changes
verify_changes() {
    echo -e "${YELLOW}Verifying changes...${NC}"
    
    # Check if main matches safe branch using --quiet
    if git diff --quiet $TARGET_BRANCH $SAFE_BRANCH; then
        echo -e "${GREEN}✓ Main branch matches $SAFE_BRANCH exactly${NC}"
    else
        echo -e "${RED}✗ Main branch does not match $SAFE_BRANCH${NC}"
        echo -e "${YELLOW}Differences found:${NC}"
        git diff --stat $TARGET_BRANCH $SAFE_BRANCH
        exit 1
    fi
    
    # Show recent commits
    echo -e "${BLUE}Recent commits on new main:${NC}"
    git log --oneline -n 5 $TARGET_BRANCH
}

# Function to run SonarCloud scan
run_sonar_scan() {
    echo -e "${YELLOW}Running SonarCloud scan on new main...${NC}"
    
    if command -v sonar-scanner &> /dev/null; then
        doppler run -- sonar-scanner \
            -Dsonar.projectKey=ruliq-compliance-platform \
            -Dsonar.organization=omara1-bakri \
            -Dsonar.host.url=https://sonarcloud.io \
            -Dsonar.branch.name=main \
            -Dsonar.qualitygate.wait=false || {
            echo -e "${YELLOW}SonarCloud scan failed, but branch replacement succeeded${NC}"
        }
    else
        echo -e "${YELLOW}sonar-scanner not found, skipping scan${NC}"
    fi
}

# Main execution
main() {
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    ⚠️  CRITICAL OPERATION ⚠️               ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║  This will completely replace the main branch with      ║${NC}"
    echo -e "${RED}║  the-bmad-experiment branch. The current main branch    ║${NC}"
    echo -e "${RED}║  contains unsafe code and must be replaced.             ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    confirm "Do you understand this will completely replace main?"
    
    # Step 1: Check status
    check_git_status
    
    # Step 2: Create backup
    confirm "Create backup of current main branch?"
    create_backup
    
    # Step 3: Replace main
    confirm "Replace main with $SAFE_BRANCH?"
    replace_main
    
    # Step 4: Push changes
    push_changes
    
    # Step 5: Verify
    verify_changes
    
    # Step 6: Optional SonarCloud scan
    if confirm_optional "Run SonarCloud scan on new main?"; then
        run_sonar_scan
    fi
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  ✓ REPLACEMENT COMPLETE                 ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║  Main branch has been successfully replaced.            ║${NC}"
    echo -e "${GREEN}║  Backup saved as: $BACKUP_BRANCH                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Notify team members about the change"
    echo "2. Monitor CI/CD pipelines"
    echo "3. Verify deployments are working"
    echo "4. Delete the-bmad-experiment branch when ready"
}

# Run main function
main "$@"