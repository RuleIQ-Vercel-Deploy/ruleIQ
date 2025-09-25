#!/bin/bash
# Post-deployment validation script
# This script validates a deployed ruleIQ application
# Usage: ./validate-deployment.sh <deployment-url>
# The script is also integrated with scripts/deploy/execute-org-deployment.py

DEPLOYMENT_URL="${1:-https://your-app.vercel.app}"

# Check if jq is available for JSON formatting
if ! command -v jq >/dev/null 2>&1; then
    echo "⚠️  jq not found; printing raw responses"
    JQ=false
else
    JQ=true
fi

echo "🔍 Validating deployment at: $DEPLOYMENT_URL"
echo "================================================"

# Track validation results
FAILED_CHECKS=0

# Health checks
echo ""
echo "📋 Health Endpoints:"
echo "-------------------"

# Basic health check
echo -n "  • /health: "
RESPONSE=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL/health" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ OK ($HTTP_CODE)"
    if [ -n "$BODY" ]; then
        if [ "$JQ" = true ]; then
            echo "$BODY" | jq '.' | sed 's/^/    /'
        else
            echo "$BODY" | sed 's/^/    /'
        fi
    fi
else
    echo "❌ FAILED ($HTTP_CODE)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Readiness check
echo -n "  • /ready: "
RESPONSE=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL/ready" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ OK ($HTTP_CODE)"
    if [ -n "$BODY" ]; then
        if [ "$JQ" = true ]; then
            echo "$BODY" | jq '.' | sed 's/^/    /'
        else
            echo "$BODY" | sed 's/^/    /'
        fi
    fi
else
    echo "❌ FAILED ($HTTP_CODE)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Detailed health check
echo -n "  • /api/v1/health/detailed: "
RESPONSE=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL/api/v1/health/detailed" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ OK ($HTTP_CODE)"
    if [ -n "$BODY" ]; then
        if [ "$JQ" = true ]; then
            echo "$BODY" | jq '.' | sed 's/^/    /'
        else
            echo "$BODY" | sed 's/^/    /'
        fi
    fi
else
    echo "❌ FAILED ($HTTP_CODE)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Database connectivity check
echo -n "  • /api/v1/health/database: "
RESPONSE=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL/api/v1/health/database" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ OK ($HTTP_CODE)"
    if [ -n "$BODY" ]; then
        if [ "$JQ" = true ]; then
            echo "$BODY" | jq '.' | sed 's/^/    /'
        else
            echo "$BODY" | sed 's/^/    /'
        fi
    fi
else
    echo "❌ FAILED ($HTTP_CODE)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# API documentation
echo ""
echo "📚 API Documentation:"
echo "--------------------"
echo -n "  • /docs: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL/docs" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Available ($HTTP_CODE)"
else
    echo "❌ Not Available ($HTTP_CODE)"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Summary
echo ""
echo "================================================"
if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo "✅ All validation checks passed!"
    exit 0
else
    echo "⚠️  $FAILED_CHECKS validation check(s) failed"
    exit 1
fi
