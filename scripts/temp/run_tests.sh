#!/bin/bash

# RuleIQ Test Runner Script
# Handles all test setup and execution

set -e  # Exit on error

echo "=== RuleIQ Test Suite Runner ==="
echo "Working directory: $(pwd)"
date

# Step 1: Install missing dependencies
echo -e "\n=== Installing missing dependencies ==="
if [ -f requirements-missing.txt ]; then
    .venv/bin/pip install -r requirements-missing.txt
else
    echo "requirements-missing.txt not found, skipping"
fi

# Step 2: Run fix_test_imports.py
echo -e "\n=== Running fix_test_imports.py ==="
if [ -f fix_test_imports.py ]; then
    .venv/bin/python fix_test_imports.py
else
    echo "fix_test_imports.py not found, skipping"
fi

# Step 3: Check Docker containers
echo -e "\n=== Checking Docker containers ==="
if docker ps | grep -q ruleiq-test-postgres; then
    echo "Test PostgreSQL container is running"
else
    echo "Starting test PostgreSQL container..."
    docker run -d \
        --name ruleiq-test-postgres \
        -e POSTGRES_DB=test_ruleiq \
        -e POSTGRES_USER=test_user \
        -e POSTGRES_PASSWORD=test_password \
        -p 5433:5432 \
        postgres:15-alpine || echo "PostgreSQL container may already exist"
fi

if docker ps | grep -q ruleiq-test-redis; then
    echo "Test Redis container is running"
else
    echo "Starting test Redis container..."
    docker run -d \
        --name ruleiq-test-redis \
        -p 6380:6379 \
        redis:7-alpine || echo "Redis container may already exist"
fi

# Wait for containers to be ready
echo -e "\n=== Waiting for containers to be ready ==="
sleep 3

# Step 4: Run the test suite
echo -e "\n=== Running full test suite ==="
echo "Command: .venv/bin/python -m pytest -v --tb=short"
.venv/bin/python -m pytest -v --tb=short 2>&1 | tee test_output.log

# Parse results
echo -e "\n=== Test Results Summary ==="
grep -E "(passed|failed|error|skipped)" test_output.log | tail -1

echo -e "\n=== Script completed ==="
date