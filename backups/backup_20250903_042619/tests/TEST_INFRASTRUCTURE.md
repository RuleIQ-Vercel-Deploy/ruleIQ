# ruleIQ Test Infrastructure Setup

## ✅ Completed Setup (2025-09-02)

### 1. Test Environment Components

#### PostgreSQL Test Database
- **Container**: `ruleiq-test-postgres`
- **Port**: 5433
- **Database**: `compliance_test`
- **Credentials**: postgres/postgres
- **Status**: ✅ Running in Docker

#### Redis Test Cache
- **Container**: `ruleiq-test-redis`
- **Port**: 6380
- **Database**: 0
- **Status**: ✅ Running in Docker

#### Configuration Files
- **Main Config**: `.env.test` (created)
- **Setup Script**: `tests/setup_test_environment.py`
- **Coverage Config**: `pytest.ini` (existing)

### 2. Test Organization Structure

```
tests/
├── setup_test_environment.py   # Main setup script
├── conftest.py                 # Pytest configuration
├── TEST_INFRASTRUCTURE.md      # This document
├── unit/                       # Unit tests (isolated)
│   ├── models/
│   ├── services/
│   └── utils/
├── integration/                 # Integration tests
├── e2e/                        # End-to-end tests  
├── performance/                # Performance tests
├── security/                   # Security tests
├── ai/                         # AI-specific tests
├── database/                   # Database tests
├── fixtures/                   # Test fixtures
├── monitoring/                 # Monitoring tests
└── utils/                      # Test utilities
```

### 3. Test Coverage Status

#### Current Coverage
- **Generated**: coverage.xml with 27.73% coverage
- **Modules Covered**: 
  - core/security/credential_encryption.py: 84%
  - Other modules: Partial coverage

#### SonarCloud Integration
- **Configuration**: Updated to recognize test files
- **Test Detection**: ✅ Working (154 test files, 1,065 tests)
- **Coverage Upload**: ⚠️ Shows 0% (path mapping issue)

### 4. Running Tests

#### Quick Test Commands
```bash
# Set up test environment
python tests/setup_test_environment.py

# Run with test environment
python tests/setup_test_environment.py --run-tests

# Run specific test suites
source .env.test && pytest tests/unit -v
source .env.test && pytest tests/integration -v

# Generate coverage
source .env.test && pytest --cov=api --cov=services --cov-report=xml
```

#### Docker Management
```bash
# Start test containers
docker start ruleiq-test-postgres ruleiq-test-redis

# Stop test containers  
docker stop ruleiq-test-postgres ruleiq-test-redis

# Remove test containers
docker rm ruleiq-test-postgres ruleiq-test-redis
```

### 5. Known Issues & Solutions

#### Issue 1: Tests Require External Services
**Problem**: Many tests fail without database/Redis
**Solution**: Use Docker containers on different ports (5433, 6380)

#### Issue 2: Missing Test Fixtures
**Problem**: Some tests expect `mock_ai_client` fixture
**Solution**: Need to create comprehensive fixture file

#### Issue 3: Coverage Not Showing in SonarCloud
**Problem**: Coverage shows 0% despite generating reports
**Solution**: Path mapping issue - needs investigation

#### Issue 4: Multiple Alembic Heads
**Problem**: Database migrations had multiple heads
**Solution**: Merged with `alembic merge -m "merge_heads"`

### 6. Test Categories (pytest markers)

```ini
# From pytest.ini
unit          - Unit tests (isolated, fast, mocked)
integration   - Integration tests (API endpoints)
e2e          - End-to-end tests (complete workflows)
database     - Database-related tests
api          - API endpoint tests
auth         - Authentication tests
security     - Security vulnerability tests
ai           - AI integration tests
compliance   - Regulatory compliance tests
performance  - Performance and load tests
slow         - Tests taking >5 seconds
external     - Tests requiring external services
```

### 7. Next Steps for Full Coverage

1. **Fix Path Mapping**: Ensure coverage.xml paths match source files
2. **Create Mock Fixtures**: Add missing fixtures for AI clients
3. **Database Fixtures**: Create test data fixtures
4. **Run Full Suite**: Execute all test categories
5. **Monitor Coverage**: Track improvement over time

### 8. Maintenance Commands

```bash
# Check test database status
docker ps | grep ruleiq-test

# View test logs
docker logs ruleiq-test-postgres
docker logs ruleiq-test-redis

# Reset test database
docker exec ruleiq-test-postgres psql -U postgres -c "DROP DATABASE IF EXISTS compliance_test; CREATE DATABASE compliance_test;"

# Apply migrations
source .env.test && alembic upgrade head
```

## Summary

The test infrastructure is now properly set up with:
- ✅ Isolated test databases (PostgreSQL, Redis)
- ✅ Test environment configuration (.env.test)
- ✅ Automated setup script
- ✅ Basic coverage generation (27.73%)
- ⚠️ SonarCloud integration (needs path fixes)

The foundation is solid for running comprehensive tests and improving coverage metrics.