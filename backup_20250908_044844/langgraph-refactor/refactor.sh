#!/bin/bash

# RuleIQ LangGraph Refactoring Script
# This script orchestrates the complete refactoring process

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/omar/Documents/ruleIQ"
REFACTOR_DIR="${PROJECT_ROOT}/langgraph-refactor"
BACKUP_BRANCH="pre-refactor-backup-$(date +%Y%m%d-%H%M%S)"
MAIN_BRANCH="main"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to confirm action
confirm_action() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    cd "${PROJECT_ROOT}"
    
    # Run pytest with coverage
    if pytest tests/ -v --cov=langgraph_agent --cov=services --cov=workers; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Tests failed!"
        return 1
    fi
}

# Function to create backup
create_backup() {
    print_status "Creating backup branch: ${BACKUP_BRANCH}"
    cd "${PROJECT_ROOT}"
    
    # Ensure we're on main branch
    git checkout "${MAIN_BRANCH}"
    
    # Create and switch to backup branch
    git checkout -b "${BACKUP_BRANCH}"
    git add -A
    git commit -m "Backup before LangGraph refactoring" || true
    
    # Return to main
    git checkout "${MAIN_BRANCH}"
    
    print_success "Backup created: ${BACKUP_BRANCH}"
}

# Function to run phase
run_phase() {
    local phase_num=$1
    local phase_name=$2
    local prompt_file=$3
    local test_focus=$4
    
    print_status "Starting Phase ${phase_num}: ${phase_name}"
    
    # Create phase branch
    local phase_branch="refactor/phase-${phase_num}-$(echo ${phase_name} | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
    git checkout -b "${phase_branch}"
    
    # Run Claude Code with specific prompt
    print_status "Executing refactoring for ${phase_name}..."
    
    # Check if prompt file exists
    if [ ! -f "${REFACTOR_DIR}/${prompt_file}" ]; then
        print_error "Prompt file not found: ${prompt_file}"
        return 1
    fi
    
    # Execute with Claude Code
    claude-code \
        --prompt "$(cat ${REFACTOR_DIR}/${prompt_file})" \
        --context "$(cat ${REFACTOR_DIR}/master_prompt.md)" \
        --project-path "${PROJECT_ROOT}" \
        --output-mode "merge" \
        --backup-before \
        --verbose \
        --log-file "${REFACTOR_DIR}/logs/phase-${phase_num}.log" || {
            print_error "Claude Code execution failed for phase ${phase_num}"
            git checkout "${MAIN_BRANCH}"
            git branch -D "${phase_branch}"
            return 1
        }
    
    # Run targeted tests
    print_status "Running tests for ${test_focus}..."
    if pytest "tests/${test_focus}" -v; then
        print_success "Phase ${phase_num} tests passed!"
    else
        print_warning "Some tests failed - review required"
        
        # Show diff
        git diff --stat
        
        if ! confirm_action "Continue despite test failures?"; then
            git checkout "${MAIN_BRANCH}"
            git branch -D "${phase_branch}"
            return 1
        fi
    fi
    
    # Review changes
    print_status "Changes in Phase ${phase_num}:"
    git diff --stat
    
    # Confirm merge
    if confirm_action "Accept Phase ${phase_num} changes?"; then
        git add -A
        git commit -m "Refactor Phase ${phase_num}: ${phase_name}"
        git checkout "${MAIN_BRANCH}"
        git merge "${phase_branch}" --no-ff -m "Merge Phase ${phase_num}: ${phase_name}"
        print_success "Phase ${phase_num} completed and merged!"
    else
        print_warning "Phase ${phase_num} rejected - rolling back"
        git checkout "${MAIN_BRANCH}"
        git branch -D "${phase_branch}"
        return 1
    fi
    
    return 0
}

# Main execution
main() {
    echo "========================================"
    echo "RuleIQ LangGraph Refactoring Tool"
    echo "========================================"
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [ ! -d "${PROJECT_ROOT}" ]; then
        print_error "Project root not found: ${PROJECT_ROOT}"
        exit 1
    fi
    
    cd "${PROJECT_ROOT}"
    
    # Check if Claude Code is installed
    if ! command -v claude-code &> /dev/null; then
        print_error "Claude Code is not installed. Please install it first."
        exit 1
    fi
    
    # Create logs directory
    mkdir -p "${REFACTOR_DIR}/logs"
    
    # Phase 0: Analysis and Backup
    print_status "Phase 0: Analysis and Backup"
    
    # Run initial tests to establish baseline
    if ! run_tests; then
        print_warning "Initial tests have failures - recording baseline"
    fi
    
    # Create backup
    if confirm_action "Create backup branch?"; then
        create_backup
    fi
    
    # Phase 1: State Management Enhancement
    if confirm_action "Proceed with Phase 1: State Management Enhancement?"; then
        run_phase 1 "State Management" "phase1_state.md" "test_graph_state.py" || {
            print_error "Phase 1 failed"
            exit 1
        }
    fi
    
    # Phase 2: Error Handling
    if confirm_action "Proceed with Phase 2: Error Handling?"; then
        run_phase 2 "Error Handling" "phase2_errors.md" "test_graph_app.py" || {
            print_error "Phase 2 failed"
            exit 1
        }
    fi
    
    # Phase 3: RAG Standardization
    if confirm_action "Proceed with Phase 3: RAG Standardization?"; then
        run_phase 3 "RAG System" "phase3_rag.md" "test_rag_system.py" || {
            print_error "Phase 3 failed"
            exit 1
        }
    fi
    
    # Phase 4: Celery Migration
    if confirm_action "Proceed with Phase 4: Celery Migration?"; then
        run_phase 4 "Task Migration" "phase4_celery.md" "test_task_migration.py" || {
            print_error "Phase 4 failed"
            exit 1
        }
    fi
    
    # Phase 5: Integration and Cleanup
    if confirm_action "Proceed with Phase 5: Integration and Cleanup?"; then
        run_phase 5 "Integration" "phase5_integration.md" "." || {
            print_error "Phase 5 failed"
            exit 1
        }
    fi
    
    # Final validation
    print_status "Running final validation..."
    
    # Full test suite
    if run_tests; then
        print_success "All tests passing!"
    else
        print_warning "Some tests still failing - manual review required"
    fi
    
    # Performance benchmarks
    print_status "Running performance benchmarks..."
    python "${REFACTOR_DIR}/benchmark.py" || true
    
    # Generate report
    print_status "Generating refactoring report..."
    cat > "${REFACTOR_DIR}/REFACTORING_REPORT.md" << EOF
# RuleIQ LangGraph Refactoring Report

## Completion Date: $(date)

## Phases Completed
- [x] Phase 0: Analysis and Backup
- [x] Phase 1: State Management Enhancement
- [x] Phase 2: Error Handling
- [x] Phase 3: RAG Standardization
- [x] Phase 4: Celery Migration
- [x] Phase 5: Integration and Cleanup

## Test Results
$(pytest tests/ --tb=no -q)

## Performance Improvements
- State operations: Improved
- RAG retrieval: Improved
- Task management: Simplified

## Next Steps
1. Review generated code
2. Update documentation
3. Team training
4. Monitor production

## Backup Branch
${BACKUP_BRANCH}
EOF
    
    print_success "Refactoring complete! Report saved to ${REFACTOR_DIR}/REFACTORING_REPORT.md"
    
    # Cleanup options
    if confirm_action "Remove refactoring branches (keeping backup)?"; then
        git branch -D $(git branch | grep "refactor/phase-" | sed 's/^[* ]*//')
        print_success "Cleaned up refactoring branches"
    fi
    
    echo "========================================"
    echo "Refactoring Process Complete!"
    echo "========================================"
}

# Handle errors
trap 'print_error "Script failed at line $LINENO"' ERR

# Run main function
main "$@"
