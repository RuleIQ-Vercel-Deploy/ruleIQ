#!/bin/bash

# Pre-Refactoring Safety Checklist
# This script MUST be run before any refactoring operation

echo "========================================="
echo "   PRE-REFACTORING SAFETY CHECKLIST"
echo "========================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Test current syntax
echo -e "\n${YELLOW}Check 1: Testing Python syntax...${NC}"
if python3 -m py_compile main.py 2>/dev/null; then
    echo -e "${GREEN}✅ main.py syntax is valid${NC}"
else
    echo -e "${RED}❌ main.py has syntax errors - DO NOT PROCEED${NC}"
    exit 1
fi

# Check 2: Count Python files
echo -e "\n${YELLOW}Check 2: Counting Python files...${NC}"
py_files=$(find . -name "*.py" -type f | grep -v "__pycache__" | grep -v ".backup" | wc -l)
echo "Total Python files: $py_files"

# Check 3: Test imports
echo -e "\n${YELLOW}Check 3: Testing critical imports...${NC}"
if python3 -c "from api import routers" 2>/dev/null; then
    echo -e "${GREEN}✅ API routers import successfully${NC}"
else
    echo -e "${RED}❌ API routers import failed${NC}"
fi

if python3 -c "from database import models" 2>/dev/null; then
    echo -e "${GREEN}✅ Database models import successfully${NC}"
else
    echo -e "${RED}❌ Database models import failed${NC}"
fi

# Check 4: Create safety timestamp
echo -e "\n${YELLOW}Check 4: Creating safety timestamp...${NC}"
timestamp=$(date +%Y%m%d-%H%M%S)
echo $timestamp > .claude/last-refactoring-check.txt
echo "Timestamp: $timestamp"

# Check 5: Warning prompt
echo -e "\n${YELLOW}=========================================${NC}"
echo -e "${YELLOW}    REFACTORING SAFETY RULES${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""
echo "1. ONLY modify ONE file at a time"
echo "2. TEST after each modification"
echo "3. CREATE backup before changes"
echo "4. STOP if syntax errors occur"
echo "5. GET APPROVAL for >5 files"
echo ""
echo -e "${RED}REMEMBER: The last mass refactoring broke everything!${NC}"
echo ""

# Check 6: Confirmation
echo -e "${YELLOW}Are you SURE you want to proceed with refactoring?${NC}"
echo "Type 'YES_I_UNDERSTAND' to continue: "
read confirmation

if [ "$confirmation" != "YES_I_UNDERSTAND" ]; then
    echo -e "${GREEN}Refactoring cancelled - Good choice!${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Proceeding with caution...${NC}"
echo "Remember to:"
echo "  1. Backup files first"
echo "  2. Test after EVERY change"
echo "  3. Stop if errors occur"

# Log the refactoring attempt
echo "$(date): Refactoring initiated after checklist" >> .claude/refactoring-log.txt

exit 0