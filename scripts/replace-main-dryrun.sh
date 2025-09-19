#!/bin/bash

# Dry run script to show what will be replaced
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   DRY RUN - Main Branch Replacement${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Step 1: Current branch status${NC}"
echo "Current branch: $(git branch --show-current)"
echo ""

echo -e "${YELLOW}Step 2: Comparing branches${NC}"
echo "Fetching latest main..."
git fetch origin main --quiet

echo -e "\n${BLUE}Files that will be COMPLETELY REPLACED:${NC}"
echo "ALL files in main will be replaced with files from the-bmad-experiment"
echo ""

echo -e "${YELLOW}Step 3: Commit comparison${NC}"
echo -e "\n${RED}Last 5 commits on main (will be lost):${NC}"
git log --oneline origin/main -n 5

echo -e "\n${GREEN}Last 5 commits on the-bmad-experiment (will become new main):${NC}"
git log --oneline the-bmad-experiment -n 5

echo -e "\n${YELLOW}Step 4: File differences${NC}"
echo "Number of files different between branches:"
git diff --name-only origin/main the-bmad-experiment | wc -l

echo -e "\n${BLUE}Sample of files that will change:${NC}"
git diff --name-only origin/main the-bmad-experiment | head -20

echo -e "\n${YELLOW}Step 5: What will happen (DRY RUN - NO CHANGES MADE):${NC}"
echo "1. Backup branch will be created: main-backup-$(date +%Y%m%d-%H%M%S)"
echo "2. Local main will be forced to match the-bmad-experiment EXACTLY"
echo "3. Remote main will be force-pushed with the-bmad-experiment content"
echo "4. Result: main will be identical to the-bmad-experiment"
echo ""

echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║                       DRY RUN COMPLETE                   ║${NC}"
echo -e "${RED}║                                                          ║${NC}"
echo -e "${RED}║  NO CHANGES WERE MADE                                   ║${NC}"
echo -e "${RED}║  This shows what WILL happen when you run the real      ║${NC}"
echo -e "${RED}║  replacement script.                                     ║${NC}"
echo -e "${RED}║                                                          ║${NC}"
echo -e "${RED}║  Main will be COMPLETELY replaced with                  ║${NC}"
echo -e "${RED}║  the-bmad-experiment including ALL files                ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"

