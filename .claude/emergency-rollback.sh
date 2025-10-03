#!/bin/bash

# Emergency Rollback Script
# Use this when refactoring has gone wrong

echo "========================================="
echo "   🚨 EMERGENCY ROLLBACK SCRIPT 🚨"
echo "========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${RED}This script will restore backup files.${NC}"
echo "Looking for recent backups..."

# Find all backup files from today
today=$(date +%Y%m%d)
backup_files=$(find . -name "*.backup-${today}*" -type f 2>/dev/null)

if [ -z "$backup_files" ]; then
    echo -e "${YELLOW}No backup files from today found.${NC}"
    echo "Looking for older backups..."
    backup_files=$(find . -name "*.backup-*" -type f 2>/dev/null | head -20)
fi

if [ -z "$backup_files" ]; then
    echo -e "${RED}No backup files found!${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Found backup files:${NC}"
echo "$backup_files" | head -20

echo -e "\n${YELLOW}Do you want to:${NC}"
echo "1. Restore ALL backups from today"
echo "2. Restore specific file"
echo "3. List all available backups"
echo "4. Cancel"
echo -n "Choice (1-4): "
read choice

case $choice in
    1)
        echo -e "\n${YELLOW}Restoring all backups from today...${NC}"
        for backup in $backup_files; do
            original="${backup%.backup-*}"
            if [ -f "$backup" ]; then
                echo "Restoring: $original"
                cp "$backup" "$original"
            fi
        done
        echo -e "${GREEN}✅ Restoration complete!${NC}"
        ;;
    2)
        echo -n "Enter the file path to restore: "
        read filepath
        backup=$(find . -name "${filepath}.backup-*" -type f | tail -1)
        if [ -f "$backup" ]; then
            cp "$backup" "$filepath"
            echo -e "${GREEN}✅ Restored $filepath from $backup${NC}"
        else
            echo -e "${RED}No backup found for $filepath${NC}"
        fi
        ;;
    3)
        echo -e "\n${YELLOW}All available backups:${NC}"
        find . -name "*.backup-*" -type f | sort
        ;;
    4)
        echo "Rollback cancelled."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Test if application works after rollback
echo -e "\n${YELLOW}Testing application after rollback...${NC}"
if python3 -c "import main" 2>/dev/null; then
    echo -e "${GREEN}✅ Application imports successfully!${NC}"
else
    echo -e "${RED}⚠️  Application still has issues${NC}"
fi

echo -e "\n${YELLOW}Rollback operation completed.${NC}"
echo "$(date): Emergency rollback performed" >> .claude/refactoring-log.txt