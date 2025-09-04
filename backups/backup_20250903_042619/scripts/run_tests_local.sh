#!/bin/bash
# Run tests with local test database, overriding Doppler

# Set test database URL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/compliance_test"
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5433/compliance_test"

# Disable any Doppler variables
unset DOPPLER_CONFIG
unset DOPPLER_ENVIRONMENT
unset DOPPLER_PROJECT

# Run tests
echo "Running tests with local test database..."
# Use first argument as test path if provided, otherwise default to freemium tests
TEST_PATH="${1:-tests/database/test_freemium_models.py}"
shift 2>/dev/null || true  # Remove first arg from $@ if it exists
python -m pytest "$TEST_PATH" -v "$@"