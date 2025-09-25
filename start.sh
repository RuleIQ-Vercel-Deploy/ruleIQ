#!/bin/sh

# Exit on error
set -e

echo "Starting RuleIQ API on port ${PORT:-8080}..."

# Set default environment variables if not provided
export PYTHONUNBUFFERED=1
export PORT=${PORT:-8080}

# Check if critical environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL is not set, using default"
    export DATABASE_URL="postgresql://user:pass@localhost/db"
fi

# Cloud Run detection
if [ -n "$K_SERVICE" ] || [ -n "$CLOUD_RUN_JOB" ]; then
    echo "Detected Cloud Run environment, using optimized settings"
    # Start the application with Cloud Run optimizations
    echo "Starting uvicorn with api.main:app on 0.0.0.0:${PORT}"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port ${PORT} \
        --workers 1 \
        --timeout-keep-alive 30 \
        --limit-concurrency 1000 \
        --log-level info \
        --access-log
else
    # Standard startup
    echo "Starting uvicorn with api.main:app on 0.0.0.0:${PORT}"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port ${PORT} \
        --workers 1 \
        --log-level info \
        --access-log \
        --use-colors
fi