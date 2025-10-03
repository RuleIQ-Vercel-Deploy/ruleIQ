# CI/CD Guide

## Overview

This guide documents the automated testing and continuous integration infrastructure for RuleIQ. The CI/CD pipeline ensures code quality through automated test execution, coverage tracking, and quality gate enforcement.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflows                 │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌──────────────┐
│ Backend Tests │    │Frontend Tests │    │ Flaky Tests  │
│  (pytest)     │    │(vitest+pwt)   │    │  Detection   │
└───────┬───────┘    └───────┬───────┘    └──────────────┘
        │                    │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Coverage Report│
        │  & Quality Gates│
        └────────────────┘
```

---

## GitHub Actions Workflows

### 1. Backend Tests (`backend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual dispatch with test mode selection

**What It Does:**
- Spins up service containers (PostgreSQL, Redis, Neo4j)
- Runs pytest with coverage across multiple test groups in parallel:
  - Unit tests
  - Integration tests
  - AI tests
  - API tests
  - Security tests
- Generates coverage reports (XML, HTML, JSON)
- Uploads coverage to Codecov
- Posts coverage summary as PR comment
- Enforces baseline coverage threshold (27.73%)

**Test Groups (Matrix Strategy):**
```yaml
matrix:
  test-group: [unit, integration, ai, api, security]
```

Each group runs independently, allowing:
- Parallel execution for faster feedback
- Individual failure isolation
- Targeted re-runs

**Service Containers:**
- PostgreSQL 15 on port 5433
- Redis 7 on port 6380
- Neo4j 5 on port 7688 (for integration tests)

**Environment Variables:**
```yaml
TESTING: true
DATABASE_URL: postgresql://test_user:test_password@localhost:5433/ruleiq_test
REDIS_URL: redis://localhost:6380
NEO4J_URI: bolt://localhost:7688
JWT_SECRET_KEY: (from secrets or test default)
```

**Artifacts:**
- Coverage reports (30-day retention)
- Test results (JUnit XML)
- Test logs on failure (14-day retention)

### 2. Frontend Tests (`frontend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` (when `frontend/` changes)
- Pull requests affecting `frontend/` directory
- Manual dispatch with test type selection

**What It Does:**

**Unit Tests (Vitest):**
- Runs vitest with coverage
- Generates coverage in LCOV, JSON, and HTML formats
- Uploads coverage to Codecov
- Posts coverage summary as PR comment

**E2E Tests (Playwright):**
- Runs across multiple browsers (Chromium, Firefox)
- Matrix strategy allows browser-specific failures
- Captures screenshots and videos on failure
- Generates HTML test reports

**Performance Checks:**
- Builds production bundle
- Checks bundle size (threshold: 5MB)
- Reports performance metrics

**Artifacts:**
- Coverage reports (30-day retention)
- E2E test results and reports (30-day retention)
- Failure screenshots/videos (14-day retention)

### 3. Coverage Report (`coverage-report.yml`)

**Triggers:**
- After `backend-tests.yml` and `frontend-tests.yml` complete
- Weekly schedule (Sunday 2 AM UTC)
- Manual dispatch

**What It Does:**
- Downloads coverage artifacts from backend and frontend workflows
- Parses coverage data:
  - Backend: `coverage.xml` and `coverage.json`
  - Frontend: `coverage-summary.json` and `lcov.info`
- Calculates combined project coverage
- Checks quality gates:
  - Backend baseline: 27.73%
  - Tolerance: -2% maximum drop
- Posts comprehensive coverage summary to PR
- Generates historical tracking data

**Quality Gate Enforcement:**
```bash
if backend_coverage < 25.73%:  # 27.73% - 2% tolerance
    fail_workflow()
```

### 4. Flaky Test Detection (`flaky-test-detection.yml`)

**Triggers:**
- Nightly schedule (2 AM UTC daily)
- Manual dispatch with configurable runs

**What It Does:**
- Runs backend tests 10 times (configurable)
- Runs frontend tests 5 times
- Identifies tests with inconsistent results
- Categorizes by severity:
  - Always fails (P0)
  - Intermittent ≥50% failure (P1)
  - Rare <50% failure
- Creates GitHub issues for flaky tests
- Generates detailed reports

**Output:**
- Markdown reports with failure patterns
- JSON data for programmatic analysis
- Automated GitHub issue creation

---

## Running Tests Locally

### Backend Tests

**Quick test (fast unit tests):**
```bash
make test-fast
```

**Full test suite:**
```bash
make test-full
```

**With coverage:**
```bash
pytest --cov=services --cov=api --cov=core --cov=utils --cov=models \
       --cov-report=html --cov-report=xml --cov-branch
```

**Specific test group:**
```bash
pytest -m unit -v  # unit tests only
pytest -m integration -v  # integration tests only
```

**Using test groups (parallel):**
```bash
make test-groups-parallel  # All groups in parallel
make test-group-unit       # Unit tests only
make test-group-ai         # AI tests only
```

**View coverage report:**
```bash
open htmlcov/index.html
```

### Frontend Tests

**Unit tests with coverage:**
```bash
cd frontend
pnpm test:coverage
```

**E2E tests:**
```bash
cd frontend
pnpm test:e2e
```

**Specific browser:**
```bash
pnpm test:e2e --project=chromium
```

**View coverage report:**
```bash
open frontend/coverage/index.html
```

### Comprehensive Verification

**Run all tests and generate coverage:**
```bash
./scripts/verify_test_execution.sh
```

This script:
- Checks prerequisites (Python, Node.js, Docker)
- Verifies service containers are running
- Runs backend tests with coverage
- Runs frontend tests with coverage
- Generates comprehensive summary report

---

## Coverage Requirements

### Current Baseline

| Component | Baseline | Target (12 months) |
|-----------|----------|-------------------|
| Backend   | 27.73%   | 80%               |
| Frontend  | TBD      | 80%               |
| Combined  | TBD      | 80%               |

### Quality Gates

**In CI/CD:**
- Backend coverage must not drop below 25.73% (27.73% - 2% tolerance)
- Pull requests that decrease coverage require justification
- Coverage reports are posted automatically on PRs

**For New Code:**
- Aim for 80% coverage on new files
- Critical paths (auth, payments, compliance) require >90%
- Use `# pragma: no cover` sparingly with justification

### Requesting Coverage Exceptions

If you need to reduce coverage temporarily:

1. Document the reason in PR description
2. Create a follow-up issue to restore coverage
3. Tag reviewers for approval
4. Add timeline for remediation

---

## Quality Gates

### What Causes PR to Fail

1. **Coverage Drop**: Backend coverage drops >2% without justification
2. **Test Failures**: Any test suite fails
3. **Flaky Tests**: PR introduces new flaky tests
4. **Build Failures**: Backend or frontend build fails
5. **Lint Errors**: Code style violations

### How to Fix Failing Quality Gates

**Coverage Gate Failed:**
```bash
# 1. Check coverage diff
pytest --cov --cov-report=html
open htmlcov/index.html

# 2. Add tests for uncovered code
# 3. Run coverage check locally
python scripts/generate_coverage_baseline.py

# 4. Commit and push
```

**Test Failures:**
```bash
# 1. Run failing tests locally
pytest tests/path/to/test_file.py::test_name -v

# 2. Debug and fix
# 3. Verify fix
pytest tests/path/to/test_file.py -v

# 4. Run full suite
make test-fast
```

**Flaky Tests:**
```bash
# 1. Detect flaky tests locally
python scripts/detect_flaky_tests.py --runs 5 --markers unit

# 2. Fix timing issues, race conditions, or shared state
# 3. Re-run detection
# 4. Document fix in PR
```

### Requesting Override

If a quality gate must be overridden:

1. Add `[skip-coverage-check]` to PR title
2. Provide detailed justification in PR description
3. Request review from team lead
4. Create follow-up issue for remediation

---

## Artifacts and Reports

### Where to Find Reports

**In GitHub Actions:**
- Go to workflow run
- Click "Summary"
- Scroll to "Artifacts" section
- Download artifacts:
  - `backend-coverage-*`
  - `frontend-unit-coverage`
  - `e2e-results-*`
  - `coverage-report-*`

**Coverage Report Structure:**
```
coverage-report-12345/
├── coverage-report.md           # Summary
├── backend-coverage-artifacts/
│   ├── coverage.xml
│   ├── coverage.json
│   └── htmlcov/
└── frontend-coverage-artifacts/
    └── coverage/
        ├── lcov.info
        ├── coverage-summary.json
        └── index.html
```

### Viewing Playwright Reports

**In CI artifacts:**
```
e2e-results-chromium/
├── e2e-report/
│   └── index.html        # Interactive HTML report
└── e2e-results/
    ├── screenshots/      # Failure screenshots
    └── videos/          # Test execution videos
```

**Locally:**
```bash
cd frontend
pnpm test:e2e
pnpm exec playwright show-report
```

### Coverage Trends

**Historical tracking:**
- Coverage artifacts retained for 90 days
- Weekly summary generated by scheduled workflow
- Trends tracked in workflow artifacts

---

## Troubleshooting

### Common CI Failures

**1. Service Container Not Ready**

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
- Check service health in workflow logs
- Increase health check retries in workflow
- Verify connection string in environment variables

**2. Test Timeout**

**Symptoms:**
```
FAILED tests/test_slow.py::test_something - Timeout
```

**Solution:**
```python
# Increase timeout in test
@pytest.mark.timeout(30)
def test_something():
    pass
```

Or adjust workflow timeout:
```yaml
timeout-minutes: 30
```

**3. Coverage Upload Failed**

**Symptoms:**
```
Error uploading coverage to Codecov
```

**Solution:**
- Check `CODECOV_TOKEN` secret is set
- Verify coverage files exist
- Check Codecov service status

**4. Flaky Test in CI**

**Symptoms:**
- Test passes locally but fails in CI
- Test fails intermittently

**Solution:**
```bash
# Reproduce locally
python scripts/detect_flaky_tests.py --runs 10 --markers unit

# Common fixes:
# - Add explicit waits (not sleep)
# - Mock external services
# - Fix shared state between tests
# - Increase timeouts for CI environment
```

### Reproducing CI Environment Locally

**Using Docker:**
```bash
# Start service containers
docker-compose up -d postgres-test redis-test neo4j-test

# Set environment variables
export TESTING=true
export DATABASE_URL=postgresql://test_user:test_password@localhost:5433/ruleiq_test
export REDIS_URL=redis://localhost:6380

# Activate virtualenv
source .venv/bin/activate

# Run tests
pytest -v
```

**Using act (GitHub Actions local runner):**
```bash
# Install act: https://github.com/nektos/act

# Run backend-tests workflow
act -j test --secret-file .secrets

# Run specific job
act -j unit-tests
```

### Debugging Test Failures

**1. Enable verbose logging:**
```bash
pytest -vv --log-cli-level=DEBUG tests/path/to/test.py
```

**2. Run single test:**
```bash
pytest tests/path/to/test.py::TestClass::test_method -v
```

**3. Use pytest debugger:**
```bash
pytest --pdb tests/path/to/test.py
```

**4. Check test fixtures:**
```bash
pytest --fixtures tests/path/to/test.py
```

### Who to Contact

- **CI/CD Issues**: DevOps team
- **Test Infrastructure**: QA lead
- **Coverage Questions**: Engineering manager
- **Flaky Tests**: Test owner (check git blame)

---

## Maintenance

### Updating Test Dependencies

**Backend:**
```bash
# Update requirements
pip install --upgrade pytest pytest-cov

# Freeze dependencies
pip freeze > requirements.txt

# Test locally
make test-fast

# Update workflow if needed
# .github/workflows/backend-tests.yml
```

**Frontend:**
```bash
cd frontend

# Update dependencies
pnpm update @vitest/coverage-v8 playwright

# Update lockfile
pnpm install

# Test locally
pnpm test
pnpm test:e2e
```

### Adding New Test Workflows

1. Create workflow file in `.github/workflows/`
2. Follow existing workflow patterns
3. Test with manual dispatch first
4. Document in this guide
5. Update README badges

### Modifying Coverage Thresholds

**Increasing thresholds:**

1. Update baseline in workflows:
   ```yaml
   # .github/workflows/coverage-report.yml
   BASELINE=27.73  # Change to new baseline
   ```

2. Update documentation:
   - `docs/COVERAGE_BASELINE.md`
   - `docs/TESTING_GUIDE.md`
   - `README.md`

3. Communicate to team
4. Monitor for issues
5. Adjust tolerance if needed

### Reviewing CI/CD Configuration

**Schedule:**
- Quarterly review of all workflows
- Update dependencies and actions
- Review and adjust timeouts
- Optimize parallel execution
- Update documentation

**Checklist:**
- [ ] All workflows passing consistently
- [ ] No frequent timeout issues
- [ ] Coverage trends moving upward
- [ ] Flaky test count decreasing
- [ ] Artifact retention appropriate
- [ ] Documentation up to date

---

## Best Practices

1. **Write Tests First**: Follow TDD for new features
2. **Keep Tests Fast**: Unit tests should run in <5 minutes
3. **Mock External Services**: Don't rely on third-party APIs in tests
4. **Use Fixtures**: Leverage pytest fixtures for setup/teardown
5. **Test in Isolation**: No shared state between tests
6. **Document Test Intent**: Clear test names and docstrings
7. **Monitor Flaky Tests**: Fix immediately when detected
8. **Maintain Coverage**: Don't let coverage drop
9. **Review Coverage Reports**: Check coverage diff in PRs
10. **Optimize CI Time**: Parallelize when possible

---

## Related Documentation

- [Testing Guide](./TESTING_GUIDE.md) - Test writing best practices
- [Coverage Baseline](./COVERAGE_BASELINE.md) - Current coverage metrics
- [API Endpoints Documentation](./API_ENDPOINTS_DOCUMENTATION.md)
- [README](../README.md) - Project overview and quick start

---

**Last Updated**: 2025-01-XX
**Next Review**: Quarterly