#!/bin/bash
# Run tests with coverage and report to SonarCloud

set -e  # Exit on error

echo "🧪 RuleIQ Test Suite with Coverage Reporting"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    if ! command -v doppler &> /dev/null; then
        echo -e "${YELLOW}⚠️  Doppler not found. Will use local environment.${NC}"
        USE_DOPPLER=false
    else
        USE_DOPPLER=true
    fi
    
    echo -e "${GREEN}✅ Requirements satisfied${NC}"
}

# Setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    if [ "$USE_DOPPLER" = true ]; then
        echo "   Loading secrets from Doppler..."
        export SONAR_TOKEN=$(doppler secrets get SONAR_TOKEN --plain 2>/dev/null || echo "")
        
        if [ -z "$SONAR_TOKEN" ]; then
            echo -e "${YELLOW}⚠️  SONAR_TOKEN not found in Doppler${NC}"
        fi
    fi
    
    # Create necessary directories
    mkdir -p coverage test-results htmlcov
    
    echo -e "${GREEN}✅ Environment ready${NC}"
}

# Run tests locally (without Docker)
run_local_tests() {
    echo "🏃 Running tests locally..."
    
    # Activate virtual environment
    source /home/omar/Documents/ruleIQ/.venv/bin/activate
    
    # Load Doppler secrets if available
    if [ "$USE_DOPPLER" = true ]; then
        eval $(doppler secrets download --no-file --format env)
    fi
    
    # Run pytest with coverage
    pytest \
        --cov=. \
        --cov-report=xml:coverage.xml \
        --cov-report=html:htmlcov \
        --cov-report=term \
        --junit-xml=test-results.xml \
        -v \
        --tb=short \
        --color=yes \
        || TEST_FAILED=1
    
    if [ "$TEST_FAILED" = "1" ]; then
        echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    else
        echo -e "${GREEN}✅ All tests passed!${NC}"
    fi
}

# Run tests with Docker
run_docker_tests() {
    echo "🐳 Running tests with Docker..."
    
    # Stop any existing test containers
    docker-compose -f docker-compose.test.yml down 2>/dev/null || true
    
    # Build and run tests
    docker-compose -f docker-compose.test.yml up \
        --build \
        --abort-on-container-exit \
        --exit-code-from test-runner
    
    # Copy coverage files from container
    echo "📦 Extracting coverage reports..."
    docker cp $(docker-compose -f docker-compose.test.yml ps -q test-runner):/app/coverage.xml ./coverage.xml 2>/dev/null || true
    docker cp $(docker-compose -f docker-compose.test.yml ps -q test-runner):/app/htmlcov ./htmlcov 2>/dev/null || true
    docker cp $(docker-compose -f docker-compose.test.yml ps -q test-runner):/app/test-results.xml ./test-results.xml 2>/dev/null || true
    
    # Cleanup
    docker-compose -f docker-compose.test.yml down
}

# Report to SonarCloud
report_to_sonar() {
    echo "📊 Reporting to SonarCloud..."
    
    if [ -z "$SONAR_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  Skipping SonarCloud (no token configured)${NC}"
        return
    fi
    
    # Check if coverage.xml exists
    if [ ! -f "coverage.xml" ]; then
        echo -e "${RED}❌ coverage.xml not found${NC}"
        return
    fi
    
    # Run SonarCloud scanner
    docker run \
        --rm \
        -e SONAR_HOST_URL="https://sonarcloud.io" \
        -e SONAR_TOKEN="$SONAR_TOKEN" \
        -v "${PWD}:/usr/src" \
        sonarsource/sonar-scanner-cli \
        -Dsonar.projectKey=ruleiq \
        -Dsonar.organization=ruleiq-org \
        -Dsonar.sources=. \
        -Dsonar.exclusions="**/*_test.py,**/tests/**,**/test_*.py,**/htmlcov/**,**/.venv/**" \
        -Dsonar.tests=tests \
        -Dsonar.python.coverage.reportPaths=coverage.xml \
        -Dsonar.python.xunit.reportPath=test-results.xml \
        -Dsonar.python.version=3.11
    
    echo -e "${GREEN}✅ Coverage reported to SonarCloud${NC}"
}

# Generate coverage report
generate_report() {
    echo "📈 Coverage Summary:"
    echo "===================="
    
    if [ -f "coverage.xml" ]; then
        # Extract coverage percentage from XML
        coverage=$(python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('coverage.xml')
root = tree.getroot()
rate = float(root.attrib.get('line-rate', 0)) * 100
print(f'{rate:.2f}%')
" 2>/dev/null || echo "Unknown")
        
        echo -e "Overall Coverage: ${GREEN}${coverage}${NC}"
    fi
    
    echo ""
    echo "📁 Reports available at:"
    echo "   - HTML Report: htmlcov/index.html"
    echo "   - XML Report: coverage.xml"
    echo "   - JUnit Report: test-results.xml"
    
    if [ -n "$SONAR_TOKEN" ]; then
        echo "   - SonarCloud: https://sonarcloud.io/dashboard?id=ruleiq"
    fi
}

# Main execution
main() {
    # Parse arguments
    USE_DOCKER=false
    REPORT_SONAR=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                USE_DOCKER=true
                shift
                ;;
            --sonar)
                REPORT_SONAR=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --docker    Run tests in Docker containers"
                echo "  --sonar     Report coverage to SonarCloud"
                echo "  --help      Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                    # Run tests locally"
                echo "  $0 --docker           # Run tests in Docker"
                echo "  $0 --docker --sonar   # Run in Docker and report to SonarCloud"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Run the pipeline
    check_requirements
    setup_environment
    
    if [ "$USE_DOCKER" = true ]; then
        run_docker_tests
    else
        run_local_tests
    fi
    
    if [ "$REPORT_SONAR" = true ]; then
        report_to_sonar
    fi
    
    generate_report
    
    echo ""
    echo -e "${GREEN}✨ Test pipeline complete!${NC}"
}

# Run main function
main "$@"