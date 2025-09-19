# SonarCloud Integration Guide

## Overview
This document describes the complete SonarCloud setup and configuration for the ruleIQ project, including test coverage reporting for both frontend (TypeScript/React) and backend (Python) codebases.

## Configuration Files

### 1. sonar-project.properties
Main configuration file that defines:
- Project identification (key, organization, name)
- Source and test directories separation
- Language-specific settings
- Coverage report paths for JavaScript/TypeScript and Python
- File exclusions

### 2. GitHub Actions Workflow (.github/workflows/sonarcloud.yml)
Automated CI/CD pipeline that:
- Runs on push to main/develop branches and pull requests
- Generates test coverage for frontend (using pnpm and Vitest)
- Generates test coverage for backend (using pytest and coverage.py)
- Uploads results to SonarCloud for analysis

### 3. Testing Configurations

#### Frontend (Vitest)
- **Config**: `frontend/vitest.config.ts`
- **Coverage Provider**: V8
- **Report Formats**: text, json, html, lcov
- **Output**: `frontend/coverage/lcov.info`

#### Backend (Pytest)
- **Config**: `pytest.ini`
- **Coverage Tool**: pytest-cov
- **Report Format**: XML (Cobertura format)
- **Output**: `coverage.xml`

## Key Features Configured

### Test Coverage
- ✅ JavaScript/TypeScript coverage via Vitest with LCOV format
- ✅ Python coverage via pytest-cov with XML format
- ✅ Automatic coverage generation in CI/CD pipeline
- ✅ Coverage reports uploaded to SonarCloud

### Code Quality Analysis
- ✅ Separate source and test directories for accurate metrics
- ✅ Language-specific file suffix configuration
- ✅ Comprehensive file exclusions (node_modules, venv, build artifacts)
- ✅ Quality gate enforcement

### CI/CD Integration
- ✅ GitHub Actions integration
- ✅ Automatic analysis on push and PR
- ✅ Support for both pnpm (frontend) and pip (backend)
- ✅ Graceful handling of test failures

## Local Testing

Use the provided script to test SonarCloud configuration locally:

```bash
# Make script executable
chmod +x scripts/sonar-local.sh

# Set your SonarCloud token
export SONAR_TOKEN=your_token_here

# Run the script
./scripts/sonar-local.sh
```

Options:
1. Frontend tests only
2. Python tests only
3. Both tests
4. SonarCloud analysis only
5. Full pipeline (tests + analysis)

## Required Secrets

Configure these in GitHub repository settings:
- `SONAR_TOKEN`: Your SonarCloud authentication token
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## Verification Steps

1. **Check Coverage Generation**:
   - Frontend: `cd frontend && pnpm test:coverage`
   - Backend: `pytest --cov=services --cov-report=xml`

2. **Verify Report Files**:
   - Frontend: `frontend/coverage/lcov.info`
   - Backend: `coverage.xml`

3. **Monitor SonarCloud Dashboard**:
   - URL: https://sonarcloud.io/project/overview?id=OmarA1-Bakri_ruleIQ
   - Check coverage metrics
   - Review quality gate status
   - Analyze code smells and vulnerabilities

## Troubleshooting

### Issue: Coverage reports not found
**Solution**: Ensure tests run before SonarCloud scan and reports are generated in expected locations.

### Issue: Wrong files analyzed
**Solution**: Check `sonar.sources` and `sonar.tests` paths in sonar-project.properties.

### Issue: Coverage not appearing in SonarCloud
**Solution**: Verify coverage report paths match configuration and reports are in correct format (LCOV for JS/TS, XML for Python).

## Best Practices

1. **Always generate coverage** before SonarCloud analysis
2. **Use continue-on-error** for test steps to ensure analysis runs even if tests fail
3. **Separate source and test code** for accurate metrics
4. **Exclude generated files** and dependencies from analysis
5. **Monitor quality gates** and address issues promptly

## References

- [SonarCloud Documentation](https://docs.sonarsource.com/sonarqube-cloud/)
- [GitHub Actions for SonarCloud](https://docs.sonarsource.com/sonarqube-cloud/advanced-setup/ci-based-analysis/github-actions-for-sonarcloud/)
- [JavaScript/TypeScript Coverage](https://docs.sonarsource.com/sonarqube-cloud/enriching/test-coverage/javascript-typescript-test-coverage/)
- [Python Coverage](https://docs.sonarsource.com/sonarqube-cloud/enriching/test-coverage/python-test-coverage/)