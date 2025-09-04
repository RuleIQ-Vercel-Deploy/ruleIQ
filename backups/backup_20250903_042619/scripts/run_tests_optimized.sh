#!/bin/bash

# Optimized test execution script with multiple profiles
# Usage: ./scripts/run_tests_optimized.sh [profile]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the profile argument
PROFILE=${1:-"fast"}

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    print_status "Activating virtual environment..."
    source .venv/bin/activate
fi

# Function to run tests with timing
run_timed_tests() {
    local test_cmd="$1"
    local description="$2"
    
    print_status "Running: $description"
    print_status "Command: $test_cmd"
    
    # Capture start time
    start_time=$(date +%s)
    
    # Run the tests
    if eval "$test_cmd"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        print_status "✓ $description completed in ${duration}s"
        return 0
    else
        print_error "✗ $description failed"
        return 1
    fi
}

# Test execution profiles
case "$PROFILE" in
    "fast")
        print_status "Running FAST tests only (development mode)"
        run_timed_tests \
            "pytest -m 'not slow and not integration and not e2e' -n auto --dist worksteal --tb=short --maxfail=1" \
            "Fast unit tests"
        ;;
    
    "unit")
        print_status "Running all UNIT tests"
        run_timed_tests \
            "pytest -m 'unit' -n auto --dist worksteal --tb=short" \
            "Unit tests"
        ;;
    
    "integration")
        print_status "Running INTEGRATION tests"
        run_timed_tests \
            "pytest -m 'integration' -n 4 --dist worksteal" \
            "Integration tests"
        ;;
    
    "ci")
        print_status "Running CI test suite (unit + integration)"
        run_timed_tests \
            "pytest -m 'not e2e and not slow' -n auto --dist worksteal --cov=. --cov-report=xml --junit-xml=test-results.xml" \
            "CI test suite"
        ;;
    
    "full")
        print_status "Running FULL test suite"
        run_timed_tests \
            "pytest -n auto --dist worksteal --cov=. --cov-report=html --cov-report=term-missing" \
            "Full test suite"
        ;;
    
    "debug")
        print_status "Running tests in DEBUG mode (no parallelization)"
        run_timed_tests \
            "pytest -vv --tb=long --capture=no" \
            "Debug mode tests"
        ;;
    
    "profile")
        print_status "Running tests with PROFILING"
        run_timed_tests \
            "pytest --profile --profile-svg -n 1 --durations=50" \
            "Profiled tests"
        print_status "Profile saved to prof/combined.svg"
        ;;
    
    "slow")
        print_status "Running SLOW tests only"
        run_timed_tests \
            "pytest -m 'slow' -n 2" \
            "Slow tests"
        ;;
    
    "failed")
        print_status "Running previously FAILED tests"
        run_timed_tests \
            "pytest --lf -n auto --dist worksteal" \
            "Failed tests rerun"
        ;;
    
    "collect")
        print_status "Collecting tests only (no execution)"
        run_timed_tests \
            "pytest --collect-only -q" \
            "Test collection"
        ;;
    
    *)
        print_error "Unknown profile: $PROFILE"
        echo ""
        echo "Available profiles:"
        echo "  fast        - Quick unit tests for development (default)"
        echo "  unit        - All unit tests"
        echo "  integration - Integration tests only"
        echo "  ci          - CI pipeline tests (unit + integration)"
        echo "  full        - Complete test suite with coverage"
        echo "  debug       - Debug mode (no parallelization, verbose)"
        echo "  profile     - Run with profiling enabled"
        echo "  slow        - Run only slow tests"
        echo "  failed      - Rerun failed tests from last run"
        echo "  collect     - Collect tests without running"
        echo ""
        echo "Usage: $0 [profile]"
        exit 1
        ;;
esac

# Print summary
echo ""
print_status "Test execution complete!"

# If coverage was generated, show summary
if [[ -f "coverage.xml" ]]; then
    print_status "Coverage report generated: coverage.xml"
    python -m coverage report --skip-covered --skip-empty | head -20
fi

# Show slowest tests if durations were captured
if [[ "$PROFILE" != "collect" ]]; then
    echo ""
    print_status "Slowest tests from this run:"
    pytest --co -q | grep -E "^[0-9]+\.[0-9]+s" | head -10 || true
fi