# RuleIQ Diagnostic Scripts

This directory contains validation and diagnostic scripts for the RuleIQ application.

## Available Scripts

### 1. test_startup.py
Validates that the FastAPI application can start successfully and all critical components are properly initialized.

**Usage:**
```bash
python scripts/diagnostics/test_startup.py
```

**Checks:**
- Environment variables
- Database connectivity
- API initialization
- Redis connection (optional)
- Service initialization

### 2. validate_endpoints.py
Validates all API endpoints by checking accessibility, authentication requirements, response schemas, and error handling.

**Usage:**
```bash
python scripts/diagnostics/validate_endpoints.py [--base-url URL]
```

**Options:**
- `--base-url`: Base URL of the API (default: http://localhost:8000)

**Checks:**
- Health endpoints
- Authentication endpoints
- Business logic endpoints
- Admin endpoints
- WebSocket endpoints

### 3. database_health_check.py
Comprehensive database health monitoring and diagnostics.

**Usage:**
```bash
python scripts/diagnostics/database_health_check.py
```

**Checks:**
- Database connectivity
- Connection pool health
- Table statistics
- Index usage
- Active queries
- Lock monitoring
- Redis health (if configured)

## CI Integration

These scripts are integrated into the CI pipeline and run automatically on:
- Push to main/develop branches
- Pull requests

The CI workflow includes:
1. Unit tests (pytest)
2. Diagnostic tests
3. Validation scripts with a running PostgreSQL service

## Running Locally

### Prerequisites
```bash
pip install -r requirements.txt
pip install httpx pytest pytest-cov
```

### Environment Variables
Create a `.env` file with:
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=testing
REDIS_URL=redis://localhost:6379  # Optional
```

### Run All Validations
```bash
# Start the API server first (in another terminal)
uvicorn main:app --reload

# Run startup validation
python scripts/diagnostics/test_startup.py

# Run endpoint validation
python scripts/diagnostics/validate_endpoints.py

# Run database health check
python scripts/diagnostics/database_health_check.py
```

### Run Pytest Tests
```bash
# Run all diagnostic tests
pytest tests/diagnostics/ -v

# Run specific test file
pytest tests/diagnostics/test_startup_validation.py -v
```

## Output

All scripts generate:
1. Console output with colored status indicators
2. JSON report files:
   - `validation_report.json` (endpoint validation)
   - `database_health_report.json` (database health)

## Exit Codes

- `0`: All checks passed
- `1`: One or more checks failed

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Verify DATABASE_URL is correct
   - Ensure PostgreSQL is running
   - Check network connectivity

2. **Endpoint validation fails**
   - Ensure API server is running
   - Check correct base URL
   - Verify authentication credentials

3. **Import errors**
   - Install all required dependencies
   - Ensure project root is in PYTHONPATH