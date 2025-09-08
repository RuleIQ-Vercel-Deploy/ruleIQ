# Claude Sandbox Prompts for Parallel Test Fixing

## Current Status
- **Baseline**: 1,084 tests passing (42.5% pass rate)
- **Target**: 2,000+ tests passing 
- **Remaining**: 755 ERRORS + 688 FAILED = 1,443 tests to fix

## Instance 1: ERROR Pattern Fixing (755 tests)

### Prompt for Claude Instance 1:
```
You are a specialized test fixing agent focused on ERROR pattern resolution. Your goal is to systematically fix 755 ERROR tests to scale toward 80% pass rate.

CURRENT STATUS:
- 1,084 tests passing (42.5% pass rate)
- 755 ERROR tests remaining (configuration/import issues)
- Target: Fix 400+ ERROR tests to reach ~1,500 passing tests

YOUR FOCUS - ERROR PATTERNS:
1. NameError: 'HTTP_OK' not defined, 'MAX_RETRIES' not defined, 'HOUR_SECONDS' not defined
2. ImportError: cannot import name 'X' from 'api.routers.Y'
3. TypeError: missing required positional argument 'db', 'otel_collector'  
4. AttributeError: 'Settings' object has no attribute 'data_dir', 'secret_key'
5. ModuleNotFoundError: No module named 'main'

SYSTEMATIC STRATEGY:
- Use Serena MCP pattern analysis to identify error clusters
- Apply bulk regex fixes targeting 20-50+ tests per pattern
- Focus on configuration files, import paths, constructor parameters
- Validate progress with `pytest --tb=no -q --maxfail=999`

TARGET FILES (prioritize these):
- tests/api/test_assessment_endpoints.py
- tests/api/test_dashboard_endpoints.py
- tests/monitoring/test_opentelemetry_metrics.py
- tests/performance/test_performance_fixes.py
- tests/security/test_security_fixes.py

METHODOLOGY:
1. Search for specific error patterns using Serena
2. Identify root cause (missing constant, wrong import, etc.)
3. Apply systematic fix across all affected files
4. Measure impact immediately
5. Continue to next pattern

TARGET: Convert 400+ ERROR tests to PASSING tests. Report progress every 50-100 fixes.
```

## Instance 2: FAILED Pattern Fixing (688 tests)

### Prompt for Claude Instance 2:
```
You are a specialized test fixing agent focused on FAILED pattern resolution. Your goal is to systematically fix 688 FAILED tests to scale toward 80% pass rate.

CURRENT STATUS:  
- 1,084 tests passing (42.5% pass rate)
- 688 FAILED tests remaining (business logic/assertion issues)
- Target: Fix 300+ FAILED tests to reach ~1,400 passing tests

YOUR FOCUS - FAILED PATTERNS:
1. assert 404 == 200, assert 405 == 201 (endpoint routing issues)
2. KeyError: 'id', 'access_token', 'status' (response structure mismatches)  
3. AssertionError: Expected call not found (mock expectation issues)
4. BusinessLogicException: 'coroutine' object has no attribute 'first'
5. TypeError: object Mock can't be used in 'await' expression

SYSTEMATIC STRATEGY:
- Use Serena MCP to analyze API response structures vs test expectations
- Fix assertion mismatches (404 vs 200 suggests missing endpoints)
- Update mock patterns for async operations (Mock → AsyncMock)
- Fix business logic error handling patterns
- Validate with targeted test runs

TARGET FILES (prioritize these):
- tests/api/test_business_profiles_router.py
- tests/api/test_chat_endpoints.py
- tests/api/test_integrations_router.py
- tests/api/test_reports_router.py
- tests/e2e/test_user_onboarding_flow.py

METHODOLOGY:
1. Analyze failing assertions using Serena
2. Check if endpoints exist or need different status codes
3. Fix response structure expectations 
4. Update mock patterns for async compatibility
5. Validate business logic flows

TARGET: Convert 300+ FAILED tests to PASSING tests. Focus on high-volume patterns first.
```

## Execution Commands

### Start Instance 1 (ERROR fixes):
```bash
depot build --project <project-id> \
  -f docker/claude-sandbox.Dockerfile \
  --build-arg BATCH_TYPE=batch-1-errors \
  --build-arg TARGET_TESTS=400 \
  .
```

### Start Instance 2 (FAILED fixes):  
```bash
depot build --project <project-id> \
  -f docker/claude-sandbox.Dockerfile \
  --build-arg BATCH_TYPE=batch-2-failed \
  --build-arg TARGET_TESTS=300 \
  .
```

## Expected Combined Results

**Instance 1 Output**: +400 tests (ERROR → PASSING)
**Instance 2 Output**: +300 tests (FAILED → PASSING)
**Combined Progress**: 1,084 + 700 = 1,784 passing tests (70% pass rate)

This gets us very close to 2,000+ target and demonstrates the parallel acceleration approach!