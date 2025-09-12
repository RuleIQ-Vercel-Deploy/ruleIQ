#!/bin/bash
# Script to run integration tests and generate coverage report

echo "=========================================="
echo "Running RuleIQ Integration Tests"
echo "=========================================="

# Export test environment variables
export TESTING=true
export ENVIRONMENT=testing
export DATABASE_URL="postgresql://test@localhost/ruleiq_test"
export JWT_SECRET_KEY="test-secret-key-for-tests"
export REDIS_URL="redis://localhost:6379/0"

# Create test database if it doesn't exist
echo "Setting up test database..."
psql -U postgres -c "DROP DATABASE IF EXISTS ruleiq_test;" 2>/dev/null || true
psql -U postgres -c "CREATE DATABASE ruleiq_test;" 2>/dev/null || true

# Run specific test categories
echo ""
echo "1. Testing SEC-001 Authentication Fix..."
echo "------------------------------------------"
python -m pytest tests/test_sec001_auth_fix.py -v --tb=short

echo ""
echo "2. Testing Authentication Flow..."
echo "------------------------------------------"
python -m pytest tests/integration/test_auth_flow.py -v --tb=short --maxfail=3

echo ""
echo "3. Testing API Endpoints..."
echo "------------------------------------------"
python -m pytest tests/integration/test_api_endpoints.py -v --tb=short --maxfail=3

echo ""
echo "4. Testing Database Transactions..."
echo "------------------------------------------"
python -m pytest tests/integration/test_transactions.py -v --tb=short --maxfail=3

echo ""
echo "5. Generating Coverage Report..."
echo "------------------------------------------"
python -m pytest tests/integration/ \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-config=.coveragerc \
    -v

echo ""
echo "=========================================="
echo "Test Execution Complete!"
echo "Coverage report available at: htmlcov/index.html"
echo "=========================================="