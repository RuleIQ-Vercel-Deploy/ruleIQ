# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies including additional build tools for asyncpg
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    libffi-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel for cache-busting and better dependency resolution
RUN python -m pip install --upgrade pip setuptools wheel

# Copy constraints file for dependency version control
COPY constraints.txt .

# Install Python dependencies
# Use optimized requirements for Cloud Run with constraints
COPY requirements-cloudrun.txt .
RUN pip install --no-cache-dir --verbose -r requirements-cloudrun.txt -c constraints.txt

# Verify that critical database dependencies are properly installed
RUN python -c "import asyncpg; print('asyncpg installed successfully')"
RUN python -c "import psycopg; print('psycopg installed successfully')"
RUN python -c "import sqlalchemy; print('sqlalchemy installed successfully')"

# Comprehensive dependency check for all database-related packages
RUN python - << 'PY'
import sys
try:
    import asyncpg
    import psycopg
    import sqlalchemy
    from sqlalchemy.ext.asyncio import create_async_engine
    print('All database dependencies verified successfully')

    # Test psycopg async driver fallback if asyncpg is not available
    # This simulates the fallback scenario
    test_url = "postgresql+psycopg://user:pass@localhost/test"
    try:
        # This will fail during build but validates that psycopg driver is available
        engine = create_async_engine(test_url, connect_args={})
        print('psycopg async driver verified (can be used as fallback)')
    except Exception as e:
        # Expected to fail during build due to no database connection
        if 'psycopg' in str(e.__class__.__module__):
            print('psycopg async driver is available and loaded')
        else:
            print(f'psycopg async driver verification: {e.__class__.__name__}')

except ImportError as e:
    print(f'Database dependency verification failed: {e}')
    sys.exit(1)
PY

# Copy project files
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Add health check for container health monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health/live || exit 1

# Run uvicorn with Cloud Run optimizations
# Use single worker for Cloud Run (handles concurrency at container level)
# Add graceful shutdown handling with proper signal forwarding
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--access-log", "--log-level", "info"]
