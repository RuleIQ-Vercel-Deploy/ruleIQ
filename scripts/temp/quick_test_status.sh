#!/bin/bash

# Quick test status check
echo "=== Quick Test Status Check ==="
date

# 1. Install missing deps quickly
echo -e "\n📦 Installing missing dependencies..."
.venv/bin/pip install -q -r requirements-missing.txt 2>/dev/null || echo "Some deps failed"

# 2. Ensure Docker containers are running
echo -e "\n🐳 Checking Docker containers..."

# PostgreSQL
if ! docker ps | grep -q ruleiq-test-postgres; then
    echo "Starting PostgreSQL..."
    docker start ruleiq-test-postgres 2>/dev/null || \
    docker run -d --name ruleiq-test-postgres \
        -e POSTGRES_DB=test_ruleiq \
        -e POSTGRES_USER=test_user \
        -e POSTGRES_PASSWORD=test_password \
        -p 5433:5432 \
        postgres:15-alpine
fi

# Redis  
if ! docker ps | grep -q ruleiq-test-redis; then
    echo "Starting Redis..."
    docker start ruleiq-test-redis 2>/dev/null || \
    docker run -d --name ruleiq-test-redis \
        -p 6380:6379 \
        redis:7-alpine
fi

sleep 2

# 3. Run diagnostic
echo -e "\n📊 Running diagnostic..."
.venv/bin/python diagnose_test_issues.py

# 4. Quick collection count
echo -e "\n📈 Final test collection count:"
.venv/bin/python -m pytest --collect-only -q 2>&1 | grep collected || echo "Collection failed"

echo -e "\n✅ Status check complete"