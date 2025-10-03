# Phase 1 Execution Plan: Test Coverage Baseline Establishment

This document provides a step-by-step execution plan for implementing the test coverage baseline and CI/CD infrastructure for RuleIQ.

---

## Prerequisites Checklist

Before starting, verify the following:

- [ ] Python 3.11.9 is installed
- [ ] Virtual environment exists at `.venv/`
- [ ] Node.js 22.14.0 is installed
- [ ] pnpm is installed
- [ ] Docker is installed and running
- [ ] Test database containers are available:
  - PostgreSQL on port 5433
  - Redis on port 6380
  - Neo4j on port 7688 (optional for integration tests)

**Verification Commands:**
```bash
python3 --version  # Should be 3.11.9
node --version     # Should be 22.x
pnpm --version     # Should be 8.x
docker --version
docker ps          # Check for running containers
```

**Install Dependencies:**
```bash
# Backend
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
pnpm install
cd ..
```

---

## Step 1: Backend Test Verification

**Objective**: Execute backend tests with coverage and verify artifacts are generated correctly.

### 1.1 Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 1.2 Setup Test Environment

```bash
python tests/setup_test_environment.py
```

This will:
- Initialize test databases
- Create test fixtures
- Configure test environment variables

### 1.3 Run Backend Tests with Coverage

```bash
pytest \
  --cov=services \
  --cov=api \
  --cov=core \
  --cov=utils \
  --cov=models \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=json \
  --cov-report=term-missing \
  --cov-branch \
  --junitxml=test-results.xml \
  -v
```

**Expected Output:**
- Tests execute successfully (some failures are okay to document)
- Coverage reports generated:
  - `coverage.xml` - XML format for CI/CD
  - `htmlcov/` - HTML report for human viewing
  - `coverage.json` - JSON for programmatic parsing
  - `test-results.xml` - JUnit XML for test results

### 1.4 Verify Coverage Artifacts

```bash
ls -la coverage.xml
ls -la coverage.json
ls -la htmlcov/index.html
```

### 1.5 View Coverage Report

```bash
# Open in browser
open htmlcov/index.html
# or
firefox htmlcov/index.html
# or
google-chrome htmlcov/index.html
```

### 1.6 Document Test Failures

If any tests fail, document them:

```bash
# Create failures log
pytest --tb=short > test-failures.log 2>&1 || true
cat test-failures.log
```

**Action Items:**
- [ ] Backend tests executed
- [ ] Coverage artifacts verified
- [ ] HTML coverage report reviewed
- [ ] Test failures documented (if any)

---

## Step 2: Frontend Test Verification

**Objective**: Execute frontend tests with coverage and verify artifacts are generated correctly.

### 2.1 Navigate to Frontend Directory

```bash
cd frontend
```

### 2.2 Run Vitest Unit Tests with Coverage

```bash
pnpm test:coverage
```

**Expected Output:**
- Unit tests execute
- Coverage reports generated:
  - `coverage/lcov.info` - LCOV format for CI/CD
  - `coverage/index.html` - HTML report
  - `coverage/coverage-summary.json` - JSON summary

### 2.3 Verify Frontend Coverage Artifacts

```bash
ls -la coverage/lcov.info
ls -la coverage/coverage-summary.json
ls -la coverage/index.html
```

### 2.4 Run Playwright E2E Tests

```bash
pnpm test:e2e
```

**Expected Output:**
- E2E tests execute (may take several minutes)
- Test results in `test-results/`
- HTML report in `playwright-report/`

### 2.5 View E2E Test Results

```bash
pnpm exec playwright show-report
```

### 2.6 View Frontend Coverage

```bash
# Open in browser
open coverage/index.html
```

### 2.7 Return to Project Root

```bash
cd ..
```

**Action Items:**
- [ ] Frontend unit tests executed
- [ ] Frontend coverage artifacts verified
- [ ] E2E tests executed
- [ ] HTML coverage report reviewed
- [ ] Test failures documented (if any)

---

## Step 3: Coverage Baseline Generation

**Objective**: Generate comprehensive baseline documentation from coverage artifacts.

### 3.1 Run Coverage Baseline Script

```bash
python scripts/generate_coverage_baseline.py
```

**Expected Output:**
- `docs/COVERAGE_BASELINE.md` generated
- `docs/coverage-baseline.json` generated
- Console output showing coverage percentages

### 3.2 Review Generated Baseline

```bash
cat docs/COVERAGE_BASELINE.md
```

Review the following sections:
- Executive Summary
- Backend Coverage Breakdown
- Frontend Coverage Breakdown
- Coverage Trends
- Recommendations

### 3.3 Verify Metrics Match Coverage Reports

Compare metrics in baseline document with:
- Backend: `coverage.json`
- Frontend: `frontend/coverage/coverage-summary.json`

### 3.4 Commit Baseline Document

```bash
git add docs/COVERAGE_BASELINE.md
git add docs/coverage-baseline.json
git commit -m "docs: Establish test coverage baseline"
```

**Action Items:**
- [ ] Baseline document generated
- [ ] Metrics reviewed and verified
- [ ] Baseline committed to repository

---

## Step 4: Flaky Test Detection

**Objective**: Identify tests with inconsistent pass/fail results.

### 4.1 Run Backend Flaky Test Detection

```bash
python scripts/detect_flaky_tests.py \
  --runs 5 \
  --markers unit,integration \
  --test-type backend \
  --output both \
  --output-dir test-reports
```

**What This Does:**
- Runs backend tests 5 times
- Identifies tests that fail intermittently
- Generates markdown and JSON reports

**Expected Duration:** 15-30 minutes

### 4.2 Review Flaky Test Report

```bash
ls -la test-reports/flaky-tests-backend-*.md
cat test-reports/flaky-tests-backend-*.md
```

### 4.3 Run Frontend Flaky Test Detection (Optional)

```bash
cd frontend

# Run vitest multiple times manually
for i in {1..5}; do
  echo "Run $i/5"
  pnpm test --reporter=json --outputFile="../test-reports/vitest-run-$i.json" || true
done

cd ..
```

### 4.4 Create GitHub Issues for Flaky Tests

For each flaky test identified:

1. Go to GitHub Issues
2. Create new issue with template:

```markdown
Title: [Flaky Test] test_name_here

## Flaky Test Detected

**Test**: `full.test.path::test_name`
**Severity**: Intermittent / Always Fails / Rare
**Failure Rate**: X%

### Statistics
- Passed: X/5
- Failed: Y/5
- Avg Duration: Z.ZZZs

### Error Messages
```
[Paste error messages here]
```

### Potential Causes
- [ ] Timing/timeout issues
- [ ] Race condition
- [ ] Shared state
- [ ] External dependency

### Action Required
Fix before next release cycle.
```

### 4.5 Document Findings

Create summary:

```bash
cat > test-reports/flaky-tests-summary.md << 'EOF'
# Flaky Test Summary

**Total Backend Flaky Tests**: X
**Total Frontend Flaky Tests**: Y

## By Severity
- Always Fails (P0): Z
- Intermittent (P1): Z
- Rare: Z

## GitHub Issues Created
- #XXX: Test name 1
- #YYY: Test name 2

## Next Steps
1. Prioritize P0 (always fails)
2. Fix P1 (intermittent) within 2 weeks
3. Monitor rare failures
EOF
```

**Action Items:**
- [ ] Backend flaky detection complete
- [ ] Frontend flaky detection complete (optional)
- [ ] Flaky test reports reviewed
- [ ] GitHub issues created for critical flaky tests
- [ ] Summary documented

---

## Step 5: CI/CD Workflow Creation

**Objective**: Create GitHub Actions workflows for automated testing.

### 5.1 Verify Workflows Created

```bash
ls -la .github/workflows/
```

Should contain:
- `backend-tests.yml`
- `frontend-tests.yml`
- `coverage-report.yml`
- `flaky-test-detection.yml`

### 5.2 Test Workflows Locally (Optional)

If you have `act` installed:

```bash
# Test backend workflow
act push -j test --secret-file .secrets

# Test frontend workflow
act push -j unit-tests
```

### 5.3 Create Feature Branch

```bash
git checkout -b ci-cd/test-coverage-baseline
```

### 5.4 Commit Workflows

```bash
git add .github/workflows/
git add scripts/verify_test_execution.sh
git add scripts/detect_flaky_tests.py
git add scripts/generate_coverage_baseline.py
git commit -m "ci: Add GitHub Actions workflows for test automation"
```

**Action Items:**
- [ ] Workflows created and verified
- [ ] Feature branch created
- [ ] Workflows committed

---

## Step 6: Documentation Updates

**Objective**: Update project documentation to reflect new CI/CD infrastructure.

### 6.1 Review Generated Documentation

```bash
ls -la docs/CI_CD_GUIDE.md
ls -la docs/COVERAGE_BASELINE.md
```

### 6.2 Update README.md

Add CI/CD badges and testing information:

```markdown
## CI/CD Status

![Backend Tests](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/backend-tests.yml/badge.svg)
![Frontend Tests](https://github.com/OmarA1-Bakri/ruleIQ/actions/workflows/frontend-tests.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-27.73%25-orange)

## Testing

See [Testing Guide](docs/TESTING_GUIDE.md) and [CI/CD Guide](docs/CI_CD_GUIDE.md) for details.

**Quick Start:**
```bash
# Backend
make test-fast

# Frontend
cd frontend && pnpm test
```

**Coverage:** [View Baseline](docs/COVERAGE_BASELINE.md)
```

### 6.3 Update TESTING_GUIDE.md

Ensure it references new CI/CD workflows and coverage baseline.

### 6.4 Commit Documentation

```bash
git add README.md
git add docs/
git commit -m "docs: Update documentation with CI/CD and coverage information"
```

**Action Items:**
- [ ] README.md updated with badges
- [ ] Documentation reviewed
- [ ] Documentation committed

---

## Step 7: Validation and Rollout

**Objective**: Test workflows in CI and merge to main branch.

### 7.1 Push Feature Branch

```bash
git push origin ci-cd/test-coverage-baseline
```

### 7.2 Create Pull Request

1. Go to GitHub repository
2. Click "Pull requests" → "New pull request"
3. Select `ci-cd/test-coverage-baseline` branch
4. Fill in PR template:

```markdown
## Test Coverage Baseline & CI/CD Implementation

This PR establishes the test coverage baseline and implements automated CI/CD pipelines.

### Changes
- ✅ GitHub Actions workflows for backend and frontend tests
- ✅ Coverage reporting and quality gates
- ✅ Flaky test detection automation
- ✅ Coverage baseline documentation
- ✅ Comprehensive CI/CD guide

### Coverage Baseline
- Backend: X.XX%
- Frontend: Y.YY%
- Target: 80%

### Testing
- [x] All scripts tested locally
- [x] Coverage artifacts generated successfully
- [x] Workflows syntax validated
- [x] Documentation reviewed

### Checklist
- [x] Coverage baseline established
- [x] Flaky tests identified and documented
- [x] CI/CD workflows created
- [x] Documentation updated
- [x] Scripts tested locally
```

### 7.3 Monitor Workflow Execution

1. Go to "Actions" tab
2. Watch workflows execute
3. Check for:
   - ✅ Backend tests pass
   - ✅ Frontend tests pass
   - ✅ Coverage reports uploaded
   - ✅ Artifacts generated

### 7.4 Review Workflow Logs

If any workflow fails:

1. Click on failed workflow
2. Click on failed job
3. Expand failed step
4. Review error message
5. Fix issue and push update

### 7.5 Fix Issues (If Any)

Common issues and fixes:

**Service container not ready:**
```yaml
# Increase health check retries
options: >-
  --health-retries 10
```

**Test timeout:**
```yaml
timeout-minutes: 45  # Increase timeout
```

**Missing secrets:**
- Add required secrets in repository settings

### 7.6 Request Review

Tag reviewers:
- Engineering lead for approval
- DevOps for CI/CD review
- QA lead for test infrastructure review

### 7.7 Merge Pull Request

Once approved and all checks pass:

1. Squash and merge
2. Delete feature branch
3. Pull latest main branch locally

```bash
git checkout main
git pull origin main
```

**Action Items:**
- [ ] Feature branch pushed
- [ ] Pull request created
- [ ] Workflows executed successfully in CI
- [ ] Issues fixed (if any)
- [ ] PR reviewed and approved
- [ ] PR merged to main

---

## Step 8: Post-Merge Verification

**Objective**: Verify CI/CD infrastructure works on main branch.

### 8.1 Verify Workflows on Main

```bash
# Make a small change to trigger workflows
echo "# CI/CD Enabled" >> README.md
git add README.md
git commit -m "docs: Note CI/CD enabled"
git push origin main
```

### 8.2 Monitor Production Workflows

1. Go to Actions tab
2. Watch workflows execute on main branch
3. Verify all pass

### 8.3 Check Coverage Report

1. Go to latest workflow run
2. Download coverage report artifact
3. Review coverage-report.md

### 8.4 Enable Branch Protection (Optional)

In repository settings, add branch protection rules:

- ✅ Require status checks to pass before merging
  - `test / unit`
  - `test / integration`
  - `unit-tests`
- ✅ Require pull request reviews before merging

### 8.5 Schedule Flaky Test Detection

Verify nightly flaky test detection workflow:

- Check scheduled workflow settings
- Verify cron schedule (2 AM UTC daily)
- Wait for first automated run

**Action Items:**
- [ ] Workflows verified on main branch
- [ ] Coverage reports accessible
- [ ] Branch protection enabled (optional)
- [ ] Scheduled workflows verified

---

## Success Criteria

Mark each as complete when verified:

### Test Execution
- [ ] All backend tests execute successfully (or failures documented)
- [ ] All frontend tests execute successfully (or failures documented)
- [ ] E2E tests execute successfully (or failures documented)

### Coverage Artifacts
- [ ] Backend coverage.xml generated
- [ ] Backend htmlcov/ directory created
- [ ] Backend coverage.json generated
- [ ] Frontend coverage/lcov.info generated
- [ ] Frontend coverage/coverage-summary.json generated

### Baseline Documentation
- [ ] docs/COVERAGE_BASELINE.md exists and populated
- [ ] Metrics match actual coverage reports
- [ ] Baseline committed to repository

### Flaky Test Detection
- [ ] Backend flaky tests identified
- [ ] Frontend flaky tests identified (if applicable)
- [ ] GitHub issues created for critical flaky tests
- [ ] Flaky test summary documented

### CI/CD Workflows
- [ ] backend-tests.yml executes successfully on push
- [ ] frontend-tests.yml executes successfully on push
- [ ] coverage-report.yml aggregates coverage correctly
- [ ] flaky-test-detection.yml scheduled for nightly runs

### Quality Gates
- [ ] Coverage thresholds enforced (27.73% baseline)
- [ ] PR comments post coverage summaries
- [ ] Workflow fails if coverage drops >2%

### Artifacts
- [ ] Coverage artifacts uploaded (30-day retention)
- [ ] Test results uploaded (JUnit XML)
- [ ] Flaky test reports uploaded (90-day retention)
- [ ] Historical coverage data tracked

### Documentation
- [ ] docs/CI_CD_GUIDE.md complete and accurate
- [ ] docs/TESTING_GUIDE.md updated
- [ ] README.md updated with badges and testing info
- [ ] All documentation reviewed and committed

---

## Rollback Plan

If critical issues arise after deployment:

### 1. Disable Workflows Temporarily

Edit each workflow file and add to top:

```yaml
on:
  workflow_dispatch:  # Manual only
```

Commit and push to disable automatic triggers.

### 2. Revert to Manual Testing

```bash
# Use local testing scripts
./scripts/verify_test_execution.sh
```

### 3. Fix Issues in Feature Branch

```bash
git checkout -b fix/ci-cd-issues
# Make fixes
git commit -m "fix: Address CI/CD workflow issues"
git push origin fix/ci-cd-issues
```

### 4. Test Fixes

Create PR with fixes and verify workflows execute correctly before merging.

### 5. Re-enable Workflows

Remove workflow_dispatch restriction and restore original triggers.

---

## Troubleshooting

### Common Issues

**Issue: Coverage shows 0% despite tests passing**

Solution:
- Check coverage.xml and verify source paths
- Ensure coverage packages installed (pytest-cov, @vitest/coverage-v8)
- Review .coveragerc and vitest.config.ts

**Issue: Service containers not connecting**

Solution:
- Check health checks in workflow
- Verify connection strings use localhost:PORT
- Increase health check retries

**Issue: Tests timeout in CI**

Solution:
- Increase timeout-minutes in workflow
- Check for network-dependent tests
- Add retries for flaky tests

**Issue: Artifacts not uploading**

Solution:
- Verify artifact paths exist
- Check workflow syntax for upload-artifact step
- Review workflow logs for upload errors

---

## Next Steps After Phase 1

Once Phase 1 is complete:

1. **Phase 2**: Increase test coverage
   - Focus on critical paths (auth, compliance, payments)
   - Add integration tests
   - Expand E2E coverage

2. **Phase 3**: Optimize CI/CD
   - Reduce workflow execution time
   - Add caching strategies
   - Parallelize more test groups

3. **Phase 4**: Quality improvements
   - Fix all flaky tests
   - Increase coverage thresholds gradually
   - Add performance benchmarks

---

## Contact & Support

- **CI/CD Questions**: DevOps team
- **Test Infrastructure**: QA lead
- **Coverage Issues**: Engineering manager
- **Workflow Failures**: Check GitHub Actions logs first

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30
**Status**: Ready for Execution