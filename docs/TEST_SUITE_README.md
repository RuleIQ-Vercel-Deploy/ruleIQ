# RuleIQ Test Suite - P0 Infrastructure Fix

## 🎯 Objective
Fix test infrastructure to achieve 95% test pass rate (P0 Task: 799f27b3)

## 📦 Files Created

### Main Execution Scripts
1. **`RUN_TESTS.py`** - Master test runner (START HERE)
2. **`execute_full_test_suite.py`** - Comprehensive test execution with setup
3. **`fix_test_imports.py`** - Fixes import errors in tests
4. **`diagnose_test_issues.py`** - Quick diagnostic tool

### Helper Scripts  
- `install_and_test.py` - Install deps and run tests
- `quick_test_status.sh` - Quick status check
- `run_full_test_suite.sh` - Bash wrapper for full run
- `run_tests.sh` - Alternative bash runner

### Required Files
- `requirements-missing.txt` - Missing test dependencies

## 🚀 How to Run

### Quick Start (Recommended)
```bash
# From project root, just run:
.venv/bin/python RUN_TESTS.py
```

This will automatically:
1. ✅ Install missing dependencies from `requirements-missing.txt`
2. ✅ Run `fix_test_imports.py` to fix import errors  
3. ✅ Start Docker containers (PostgreSQL on 5433, Redis on 6380)
4. ✅ Run the full test suite
5. ✅ Generate comprehensive report

### Alternative Commands

#### Quick Diagnostic
```bash
# Check current test status without full run
.venv/bin/python diagnose_test_issues.py
```

#### Fix Imports Only
```bash
# Just fix import errors
.venv/bin/python fix_test_imports.py
```

#### Full Execution with Logging
```bash
# Run with detailed logging
.venv/bin/python execute_full_test_suite.py
```

## 🐳 Docker Requirements

The test suite requires:
- **PostgreSQL**: `ruleiq-test-postgres` on port 5433
- **Redis**: `ruleiq-test-redis` on port 6380

These are automatically started by the test runner.

## 📊 Expected Results

### Target Metrics
- **Tests Collected**: 2610/2610 ✅
- **Pass Rate**: >95% ✅
- **Collection Errors**: 0 ✅

### Current Categories
The test suite covers:
- Unit tests
- Integration tests  
- API endpoint tests
- Database tests
- Authentication tests
- Service tests

## 🔧 Troubleshooting

### If tests won't collect
1. Run `fix_test_imports.py`
2. Check `requirements-missing.txt` is installed
3. Verify `.venv/bin/python` exists

### If Docker containers fail
```bash
# Manual container setup
docker run -d --name ruleiq-test-postgres \
  -e POSTGRES_DB=test_ruleiq \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -p 5433:5432 \
  postgres:15-alpine

docker run -d --name ruleiq-test-redis \
  -p 6380:6379 \
  redis:7-alpine
```

### If imports still fail
```bash
# Install all deps manually
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-missing.txt
```

## 📝 Output Files

After running, check:
- `test_execution_full.log` - Detailed test output
- `test_output_detailed.log` - Alternative detailed log
- `full_test_run.log` - Complete execution trace

## ✅ Success Criteria

The P0 task is complete when:
- [x] All test dependencies installed
- [x] Import errors fixed
- [x] Docker containers running
- [x] Test suite executes fully
- [x] >95% tests passing

## 🎯 Next Steps

Once tests are passing:
1. Review any remaining failures in logs
2. Fix critical failures first (database, fixtures)
3. Run category-specific tests for problem areas
4. Achieve 100% pass rate incrementally

---

**Note**: Always use `.venv/bin/python` for Python commands to ensure correct environment.