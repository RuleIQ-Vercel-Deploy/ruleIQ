#!/usr/bin/env bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS_DIR="${PROJECT_ROOT}/test-reports/$(date +%Y%m%d_%H%M%S)"
VENV_PATH="${PROJECT_ROOT}/.venv"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

# Test results
BACKEND_EXIT_CODE=0
FRONTEND_UNIT_EXIT_CODE=0
FRONTEND_E2E_EXIT_CODE=0

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

log_success() {
    echo -e "${GREEN}✅ ${NC}$1"
}

log_warning() {
    echo -e "${YELLOW}⚠ ${NC}$1"
}

log_error() {
    echo -e "${RED}❌ ${NC}$1"
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_section "Checking Prerequisites"

    local all_checks_passed=true

    # Check Python version
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | awk '{print $2}')
        log_success "Python $python_version found"
    else
        log_error "Python 3.11+ required but not found"
        all_checks_passed=false
    fi

    # Check Node.js version
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        log_success "Node.js $node_version found"
    else
        log_error "Node.js 22+ required but not found"
        all_checks_passed=false
    fi

    # Check pnpm
    if command -v pnpm &> /dev/null; then
        local pnpm_version=$(pnpm --version)
        log_success "pnpm $pnpm_version found"
    else
        log_error "pnpm required but not found"
        all_checks_passed=false
    fi

    # Check Docker
    if command -v docker &> /dev/null; then
        log_success "Docker found"

        # Check if test containers are running
        if docker ps | grep -q "postgres.*5433"; then
            log_success "PostgreSQL test container running on port 5433"
        else
            log_warning "PostgreSQL test container not found on port 5433"
            log_info "You may need to start it: docker-compose up -d postgres-test"
        fi

        if docker ps | grep -q "redis.*6380"; then
            log_success "Redis test container running on port 6380"
        else
            log_warning "Redis test container not found on port 6380"
            log_info "You may need to start it: docker-compose up -d redis-test"
        fi
    else
        log_warning "Docker not found - service containers may not be available"
    fi

    # Check virtual environment
    if [ -d "$VENV_PATH" ]; then
        log_success "Python virtual environment found at $VENV_PATH"
    else
        log_error "Virtual environment not found at $VENV_PATH"
        all_checks_passed=false
    fi

    if [ "$all_checks_passed" = false ]; then
        log_error "Prerequisites check failed. Please fix the issues above."
        exit 1
    fi
}

# Setup reports directory
setup_reports_dir() {
    log_section "Setting Up Reports Directory"

    mkdir -p "$REPORTS_DIR"
    log_success "Created reports directory: $REPORTS_DIR"
}

# Run backend tests
run_backend_tests() {
    log_section "Running Backend Tests with Coverage"

    cd "$PROJECT_ROOT"

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"

    # Run pytest with coverage
    log_info "Executing pytest with coverage..."
    local start_time=$(date +%s)

    if pytest \
        --cov=services \
        --cov=api \
        --cov=core \
        --cov=utils \
        --cov=models \
        --cov-report=xml \
        --cov-report=html \
        --cov-report=json \
        --cov-report=term-missing \
        --cov-branch \
        --junitxml="${REPORTS_DIR}/backend-test-results.xml" \
        -v \
        2>&1 | tee "${REPORTS_DIR}/backend-tests.log"; then
        BACKEND_EXIT_CODE=0
        log_success "Backend tests completed successfully"
    else
        BACKEND_EXIT_CODE=$?
        log_error "Backend tests failed with exit code $BACKEND_EXIT_CODE"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log_info "Backend tests took ${duration}s"

    # Copy coverage artifacts
    if [ -f "coverage.xml" ]; then
        cp coverage.xml "${REPORTS_DIR}/backend-coverage.xml"
        log_success "Copied coverage.xml to reports directory"
    else
        log_warning "coverage.xml not found"
    fi

    if [ -d "htmlcov" ]; then
        cp -r htmlcov "${REPORTS_DIR}/backend-htmlcov"
        log_success "Copied HTML coverage report to reports directory"
    else
        log_warning "htmlcov/ directory not found"
    fi

    if [ -f "coverage.json" ]; then
        cp coverage.json "${REPORTS_DIR}/backend-coverage.json"
        log_success "Copied coverage.json to reports directory"
    else
        log_warning "coverage.json not found"
    fi
}

# Run frontend unit tests
run_frontend_unit_tests() {
    log_section "Running Frontend Unit Tests with Coverage"

    cd "$FRONTEND_DIR"

    log_info "Executing vitest with coverage..."
    local start_time=$(date +%s)

    if pnpm test:coverage 2>&1 | tee "${REPORTS_DIR}/frontend-unit-tests.log"; then
        FRONTEND_UNIT_EXIT_CODE=0
        log_success "Frontend unit tests completed successfully"
    else
        FRONTEND_UNIT_EXIT_CODE=$?
        log_error "Frontend unit tests failed with exit code $FRONTEND_UNIT_EXIT_CODE"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log_info "Frontend unit tests took ${duration}s"

    # Copy coverage artifacts
    if [ -f "coverage/lcov.info" ]; then
        mkdir -p "${REPORTS_DIR}/frontend-coverage"
        cp coverage/lcov.info "${REPORTS_DIR}/frontend-coverage/"
        log_success "Copied lcov.info to reports directory"
    else
        log_warning "coverage/lcov.info not found"
    fi

    if [ -f "coverage/coverage-summary.json" ]; then
        cp coverage/coverage-summary.json "${REPORTS_DIR}/frontend-coverage/"
        log_success "Copied coverage-summary.json to reports directory"
    else
        log_warning "coverage/coverage-summary.json not found"
    fi

    if [ -d "coverage" ]; then
        cp -r coverage "${REPORTS_DIR}/frontend-htmlcov"
        log_success "Copied HTML coverage report to reports directory"
    else
        log_warning "coverage/ directory not found"
    fi
}

# Run frontend E2E tests
run_frontend_e2e_tests() {
    log_section "Running Frontend E2E Tests (Playwright)"

    cd "$FRONTEND_DIR"

    log_info "Executing Playwright E2E tests..."
    local start_time=$(date +%s)

    if pnpm test:e2e 2>&1 | tee "${REPORTS_DIR}/frontend-e2e-tests.log"; then
        FRONTEND_E2E_EXIT_CODE=0
        log_success "Frontend E2E tests completed successfully"
    else
        FRONTEND_E2E_EXIT_CODE=$?
        log_error "Frontend E2E tests failed with exit code $FRONTEND_E2E_EXIT_CODE"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log_info "Frontend E2E tests took ${duration}s"

    # Copy E2E artifacts
    if [ -d "test-results" ]; then
        cp -r test-results "${REPORTS_DIR}/frontend-e2e-results"
        log_success "Copied E2E test results to reports directory"
    else
        log_warning "test-results/ directory not found"
    fi
}

# Generate summary report
generate_summary() {
    log_section "Generating Summary Report"

    cd "$PROJECT_ROOT"

    local summary_file="${REPORTS_DIR}/SUMMARY.md"

    cat > "$summary_file" << EOF
# Test Execution Summary

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Reports Directory**: \`$REPORTS_DIR\`

---

## Test Results

### Backend Tests (pytest)
- **Status**: $([ $BACKEND_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED (exit code: $BACKEND_EXIT_CODE)")
- **Log**: \`backend-tests.log\`
- **Coverage Reports**:
  - XML: \`backend-coverage.xml\`
  - HTML: \`backend-htmlcov/index.html\`
  - JSON: \`backend-coverage.json\`

### Frontend Unit Tests (vitest)
- **Status**: $([ $FRONTEND_UNIT_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED (exit code: $FRONTEND_UNIT_EXIT_CODE)")
- **Log**: \`frontend-unit-tests.log\`
- **Coverage Reports**:
  - LCOV: \`frontend-coverage/lcov.info\`
  - JSON: \`frontend-coverage/coverage-summary.json\`
  - HTML: \`frontend-htmlcov/index.html\`

### Frontend E2E Tests (Playwright)
- **Status**: $([ $FRONTEND_E2E_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED (exit code: $FRONTEND_E2E_EXIT_CODE)")
- **Log**: \`frontend-e2e-tests.log\`
- **Test Results**: \`frontend-e2e-results/\`

---

## Coverage Summary

EOF

    # Parse backend coverage if available
    if [ -f "${REPORTS_DIR}/backend-coverage.json" ]; then
        if command -v python3 &> /dev/null; then
            python3 << PYTHON >> "$summary_file"
import json
with open("${REPORTS_DIR}/backend-coverage.json") as f:
    cov = json.load(f)
    total = cov.get("totals", {})
    print(f"### Backend Coverage")
    print(f"- **Line Coverage**: {total.get('percent_covered', 0):.2f}%")
    print(f"- **Branch Coverage**: {total.get('percent_covered_display', 'N/A')}")
    print()
PYTHON
        fi
    else
        echo "Backend coverage data not available." >> "$summary_file"
        echo "" >> "$summary_file"
    fi

    # Parse frontend coverage if available
    if [ -f "${REPORTS_DIR}/frontend-coverage/coverage-summary.json" ]; then
        if command -v python3 &> /dev/null; then
            python3 << PYTHON >> "$summary_file"
import json
with open("${REPORTS_DIR}/frontend-coverage/coverage-summary.json") as f:
    cov = json.load(f)
    total = cov.get("total", {})
    print(f"### Frontend Coverage")
    print(f"- **Line Coverage**: {total.get('lines', {}).get('pct', 0):.2f}%")
    print(f"- **Branch Coverage**: {total.get('branches', {}).get('pct', 0):.2f}%")
    print(f"- **Function Coverage**: {total.get('functions', {}).get('pct', 0):.2f}%")
    print()
PYTHON
        fi
    else
        echo "Frontend coverage data not available." >> "$summary_file"
        echo "" >> "$summary_file"
    fi

    cat >> "$summary_file" << EOF
---

## Next Steps

EOF

    if [ $BACKEND_EXIT_CODE -ne 0 ] || [ $FRONTEND_UNIT_EXIT_CODE -ne 0 ] || [ $FRONTEND_E2E_EXIT_CODE -ne 0 ]; then
        cat >> "$summary_file" << EOF
1. ❗ **Fix Failing Tests**: Review logs and fix test failures before proceeding.
2. Run \`scripts/detect_flaky_tests.py\` to identify intermittent failures.
3. Update baseline metrics once all tests pass consistently.

EOF
    else
        cat >> "$summary_file" << EOF
1. ✅ All tests passed! Run \`python scripts/generate_coverage_baseline.py\` to establish baseline.
2. Run \`python scripts/detect_flaky_tests.py\` to detect intermittent test failures.
3. Proceed with CI/CD workflow setup.

EOF
    fi

    cat >> "$summary_file" << EOF
---

## Viewing Reports

### Backend Coverage
Open in browser: \`file://$REPORTS_DIR/backend-htmlcov/index.html\`

### Frontend Coverage
Open in browser: \`file://$REPORTS_DIR/frontend-htmlcov/index.html\`

### E2E Test Results
Open in browser: \`file://$REPORTS_DIR/frontend-e2e-results/e2e-report/index.html\`

EOF

    log_success "Summary report generated: $summary_file"

    # Display summary to console
    echo ""
    cat "$summary_file"
}

# Main execution
main() {
    log_section "RuleIQ Test Verification Script"
    log_info "Starting comprehensive test execution and coverage verification"

    check_prerequisites
    setup_reports_dir
    run_backend_tests
    run_frontend_unit_tests
    run_frontend_e2e_tests
    generate_summary

    log_section "Test Verification Complete"

    # Determine overall exit code
    if [ $BACKEND_EXIT_CODE -ne 0 ] || [ $FRONTEND_UNIT_EXIT_CODE -ne 0 ] || [ $FRONTEND_E2E_EXIT_CODE -ne 0 ]; then
        log_error "Some test suites failed. Review reports at: $REPORTS_DIR"
        exit 1
    else
        log_success "All test suites passed! Reports available at: $REPORTS_DIR"
        exit 0
    fi
}

# Run main function
main "$@"