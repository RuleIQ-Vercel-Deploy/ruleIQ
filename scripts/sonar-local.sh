#!/bin/bash

# SonarCloud Local Testing Script
# This script helps test SonarCloud configuration locally before pushing to CI

echo "🔍 SonarCloud Local Testing Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if SONAR_TOKEN is set
if [ -z "$SONAR_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  SONAR_TOKEN not found in environment${NC}"
    echo "Please set it using: export SONAR_TOKEN=your_token_here"
    echo "Or load from .env file: source .env"
    exit 1
fi

# Function to run frontend tests with coverage
run_frontend_tests() {
    echo -e "\n${GREEN}📦 Running Frontend Tests with Coverage...${NC}"
    cd frontend

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        pnpm install
    fi

    # Run tests with coverage
    pnpm run test:coverage

    # Check if coverage report was generated
    if [ -f "coverage/lcov.info" ]; then
        echo -e "${GREEN}✅ Frontend coverage report generated${NC}"
    else
        echo -e "${RED}❌ Frontend coverage report not found${NC}"
    fi

    cd ..
}

# Function to run Python tests with coverage
run_python_tests() {
    echo -e "\n${GREEN}🐍 Running Python Tests with Coverage...${NC}"

    # Activate virtual environment if it exists
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi

    # Install test dependencies
    pip install -q pytest pytest-cov coverage

    # Run tests with coverage
    pytest --cov=services --cov=api --cov=core \
           --cov-report=xml --cov-report=html \
           --cov-report=term || true

    # Check if coverage report was generated
    if [ -f "coverage.xml" ]; then
        echo -e "${GREEN}✅ Python coverage report generated${NC}"
    else
        echo -e "${RED}❌ Python coverage report not found${NC}"
    fi
}

# Function to run SonarCloud analysis
run_sonar_analysis() {
    echo -e "\n${GREEN}🚀 Running SonarCloud Analysis...${NC}"

    # Check if sonar-scanner is installed
    if ! command -v sonar-scanner &> /dev/null; then
        echo -e "${YELLOW}Installing SonarCloud Scanner...${NC}"

        # Download and extract scanner
        wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
        unzip -q sonar-scanner-cli-5.0.1.3006-linux.zip
        export PATH=$PATH:$PWD/sonar-scanner-5.0.1.3006-linux/bin
    fi

    # Run analysis
    sonar-scanner \
        -Dsonar.host.url=https://sonarcloud.io \
        -Dsonar.token=$SONAR_TOKEN \
        -Dsonar.projectKey=OmarA1-Bakri_ruleIQ \
        -Dsonar.organization=omara1-bakri

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ SonarCloud analysis completed successfully${NC}"
        echo -e "View results at: https://sonarcloud.io/project/overview?id=OmarA1-Bakri_ruleIQ"
    else
        echo -e "${RED}❌ SonarCloud analysis failed${NC}"
    fi
}

# Main execution
echo -e "\n${YELLOW}Select what to run:${NC}"
echo "1) Frontend tests only"
echo "2) Python tests only"
echo "3) Both tests"
echo "4) SonarCloud analysis only"
echo "5) Full pipeline (tests + analysis)"
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        run_frontend_tests
        ;;
    2)
        run_python_tests
        ;;
    3)
        run_frontend_tests
        run_python_tests
        ;;
    4)
        run_sonar_analysis
        ;;
    5)
        run_frontend_tests
        run_python_tests
        run_sonar_analysis
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✨ Done!${NC}"