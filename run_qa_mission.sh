#!/bin/bash
#===============================================================================
# QA MISSION RUNNER - ACHIEVE 80% TEST PASS RATE
#===============================================================================

echo "========================================="
echo "🚀 RuleIQ QA Mission Runner"
echo "   Target: 80% test pass rate"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/home/omar/Documents/ruleIQ"
cd "$PROJECT_ROOT"

# Step 1: Run the systematic fixer
echo -e "\n${YELLOW}Step 1: Running systematic test fixer...${NC}"
python3 fix_tests_systematic.py

# Step 2: Run the QA mission script
echo -e "\n${YELLOW}Step 2: Running QA mission analysis...${NC}"
python3 qa_mission_80_percent.py

# Step 3: Collect tests to verify fixes
echo -e "\n${YELLOW}Step 3: Verifying test collection...${NC}"
pytest --co -q > test_collection.log 2>&1
COLLECTED=$(grep -o "collected [0-9]*" test_collection.log | grep -o "[0-9]*")
echo -e "${GREEN}✅ Successfully collected $COLLECTED tests${NC}"

# Step 4: Run quick test sample to estimate pass rate
echo -e "\n${YELLOW}Step 4: Running test sample...${NC}"
pytest --tb=no -q --maxfail=100 > test_sample.log 2>&1

# Count results
PASSED=$(grep -o '\.' test_sample.log | wc -l)
FAILED=$(grep -o 'F' test_sample.log | wc -l)
ERRORS=$(grep -o 'E' test_sample.log | wc -l)
TOTAL=$((PASSED + FAILED + ERRORS))

if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc)
    echo -e "${GREEN}Sample Results:${NC}"
    echo "  Passed: $PASSED"
    echo "  Failed: $FAILED"
    echo "  Errors: $ERRORS"
    echo "  Pass Rate: ${PASS_RATE}%"
    
    # Estimate total
    if [ $COLLECTED -gt 0 ]; then
        ESTIMATED_PASSING=$(echo "scale=0; $COLLECTED * $PASS_RATE / 100" | bc)
        TARGET_80=$(echo "scale=0; $COLLECTED * 80 / 100" | bc)
        echo -e "\n${YELLOW}Estimated for all tests:${NC}"
        echo "  Total Tests: $COLLECTED"
        echo "  Estimated Passing: $ESTIMATED_PASSING"
        echo "  Target (80%): $TARGET_80"
        
        if [ $(echo "$PASS_RATE >= 80" | bc) -eq 1 ]; then
            echo -e "\n${GREEN}🎉 SUCCESS! Achieved ${PASS_RATE}% pass rate!${NC}"
        else
            GAP=$((TARGET_80 - ESTIMATED_PASSING))
            echo -e "\n${YELLOW}⚠️ Need to fix approximately $GAP more tests${NC}"
        fi
    fi
fi

# Step 5: Generate actionable next steps
echo -e "\n${YELLOW}=========================================${NC}"
echo -e "${YELLOW}📋 NEXT STEPS TO REACH 80%:${NC}"
echo -e "${YELLOW}=========================================${NC}"

echo -e "\n1. Find and fix first failure:"
echo "   pytest -x --tb=short"

echo -e "\n2. Focus on last failed tests:"
echo "   pytest --lf -v"

echo -e "\n3. Test specific areas:"
echo "   pytest tests/unit/ -v          # Unit tests first"
echo "   pytest tests/integration/ -v   # Then integration"
echo "   pytest tests/fixtures/ -v      # Check fixtures"

echo -e "\n4. Run with specific markers:"
echo "   pytest -m \"not slow\" -v       # Skip slow tests"
echo "   pytest -m \"not external\" -v   # Skip external dependencies"

echo -e "\n5. Debug specific test file:"
echo "   pytest tests/test_specific.py -vv --tb=long"

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}📊 Full Report: qa_mission_report.md${NC}"
echo -e "${GREEN}=========================================${NC}"