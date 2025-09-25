# Codacy Integration Setup Guide

## Overview

This guide will help you set up Codacy integration with the RuleIQ project's GitHub Actions workflows. Codacy provides automated code review, quality analysis, and coverage reporting.

## Prerequisites

1. **Codacy Account**: Sign up at [codacy.com](https://www.codacy.com) if you don't have an account
2. **Repository Access**: Connect your GitHub repository to Codacy
3. **GitHub Advanced Security**: Required for private repositories to use SARIF upload (Code scanning)

## Step 1: Connect Repository to Codacy

1. Log in to your Codacy account at [app.codacy.com](https://app.codacy.com)
2. Click on "Add repository" or "+"
3. Select your GitHub organization
4. Find and select the RuleIQ repository
5. Follow the setup wizard to configure initial settings

## Step 2: Configure Tokens

You have two options for authentication tokens:

### Option A: Project Token (Recommended for single repository)

1. Navigate to your project in Codacy
2. Go to **Settings** → **Integrations** → **Project API**
3. Copy the **Project Token**
4. Add it as a GitHub repository secret:
   ```bash
   gh secret set CODACY_PROJECT_TOKEN --body "your-project-token-here"
   ```

### Option B: Account API Token (For organization-wide usage)

1. Go to your Codacy account settings
2. Navigate to **Access Management** → **API Tokens**
3. Click **Create API token**
4. Give it a descriptive name (e.g., "GitHub Actions")
5. Copy the generated token
6. Add it as a GitHub organization secret:
   ```bash
   gh secret set CODACY_API_TOKEN --org your-org --body "your-account-token-here"
   ```

## Step 3: GitHub Repository Configuration

### Add Secrets via GitHub UI

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add one of the following:
   - Name: `CODACY_PROJECT_TOKEN`, Value: Your project token
   - OR Name: `CODACY_API_TOKEN`, Value: Your account API token

### Enable GitHub Advanced Security (Private Repos Only)

For private repositories, enable GitHub Advanced Security:

1. Go to **Settings** → **Security & analysis**
2. Enable **GitHub Advanced Security**
3. Enable **Code scanning**

## Step 4: Workflow Integration Details

The Codacy integration has been added to the following workflows:

### 1. Security Workflow (`security.yml`)
- **Purpose**: Static code analysis with SARIF upload to GitHub Security tab
- **Job**: `codacy-analysis`
- **Features**:
  - Runs Codacy Analysis CLI
  - Uploads results to GitHub Security tab
  - Compatible with GitHub code scanning

### 2. CI Pipeline (`ci.yml`)
- **Purpose**: Coverage reporting for continuous integration
- **Job**: Enhanced `backend-tests` job
- **Features**:
  - Uploads Python test coverage to Codacy
  - Runs alongside existing codecov integration

### 3. Test Workflow (`test.yml`)
- **Purpose**: Comprehensive coverage reporting
- **Jobs**: Enhanced `backend-unit-tests` and `frontend-tests`
- **Features**:
  - Uploads Python coverage for multiple versions (3.11, 3.12)
  - Uploads JavaScript/TypeScript coverage for Node 18 and 20
  - Matrix build support

### 4. Quality Gate Workflow (`codacy-quality-gate.yml`)
- **Purpose**: Dedicated quality gate enforcement
- **Jobs**:
  - `codacy-analysis`: Comprehensive code analysis
  - `coverage-validation`: Coverage threshold validation
  - `quality-gate-check`: Overall quality assessment
- **Features**:
  - PR comments with quality status
  - Multi-language support (Python, JavaScript/TypeScript)
  - Quality gate pass/fail determination

## Step 5: Configure Quality Gates

1. In Codacy, go to your project dashboard
2. Navigate to **Settings** → **Quality Settings**
3. Configure the following:

### Code Coverage Settings
- **Coverage threshold**: Set minimum coverage (e.g., 80%)
- **Coverage variation**: Maximum allowed coverage decrease (e.g., 1%)
- **Diff coverage**: Minimum coverage for new/changed code (e.g., 90%)

### Code Quality Settings
- **Issues threshold**: Maximum number of issues allowed
- **Complexity threshold**: Maximum cyclomatic complexity
- **Duplication threshold**: Maximum code duplication percentage

### Pull Request Settings
1. Go to **Settings** → **Integrations** → **GitHub**
2. Enable:
   - ✅ Pull Request comments
   - ✅ Pull Request status
   - ✅ Coverage status
   - ✅ Quality status

## Step 6: Verify Integration

### Test the Workflows

1. Create a test branch:
   ```bash
   git checkout -b test/codacy-integration
   ```

2. Make a small code change and push:
   ```bash
   git add .
   git commit -m "test: Verify Codacy integration"
   git push origin test/codacy-integration
   ```

3. Open a pull request

4. Verify the following:
   - GitHub Actions workflows run successfully
   - Codacy comments appear on the PR
   - SARIF results appear in the Security tab
   - Coverage reports appear in Codacy dashboard

### Check Codacy Dashboard

1. Go to your [Codacy project dashboard](https://app.codacy.com)
2. Verify:
   - Code quality metrics are displayed
   - Coverage percentage is shown
   - Issues are identified and categorized
   - File-level analysis is available

## Step 7: Coverage Report Requirements

Ensure your test suites generate the required coverage reports:

### Python Coverage
- **Format**: `coverage.xml` (Cobertura format)
- **Generation**: Already configured in workflows using `pytest-cov`
- **Command**: `pytest --cov=api --cov=services --cov-report=xml`

### JavaScript/TypeScript Coverage
- **Format**: `lcov.info` (LCOV format)
- **Location**: `frontend/coverage/lcov.info`
- **Generation**: Configured in `package.json` test scripts
- **Command**: `pnpm run test:unit --coverage`

## Troubleshooting

### Common Issues and Solutions

#### 1. Token Authentication Errors
**Error**: "Could not authenticate with Codacy"
**Solution**:
- Verify the token is correctly set in GitHub secrets
- Check token permissions in Codacy
- Ensure you're using the correct token type (project vs API)

#### 2. Coverage Upload Failures
**Error**: "Failed to upload coverage"
**Solutions**:
- Verify coverage files are generated:
  ```bash
  ls coverage.xml  # Python
  ls frontend/coverage/lcov.info  # JavaScript
  ```
- Check file paths in workflow match actual locations
- Ensure tests run successfully before coverage upload

#### 3. SARIF Upload Issues
**Error**: "Error uploading SARIF"
**Solutions**:
- Enable GitHub Advanced Security for private repos
- Check `security-events: write` permission in workflow
- Verify SARIF file is generated correctly

#### 4. No Codacy Comments on PR
**Solutions**:
- Check PR integration settings in Codacy
- Verify `pull-requests: write` permission in workflow
- Ensure workflow runs on `pull_request` events

#### 5. Quality Gate Not Running
**Solutions**:
- Check if secrets are available:
  ```yaml
  if: env.CODACY_PROJECT_TOKEN != '' || env.CODACY_API_TOKEN != ''
  ```
- Verify workflow triggers are correct
- Check workflow syntax with `actionlint`

### Debug Mode

To enable verbose logging in Codacy actions:

1. Set `verbose: true` in the action configuration
2. Check GitHub Actions logs for detailed output
3. Look for specific error messages in Codacy dashboard

## Monitoring and Maintenance

### Regular Tasks

1. **Weekly**: Review Codacy dashboard for new issues
2. **Per Sprint**: Adjust quality gates based on project progress
3. **Monthly**: Review and update code patterns and rules
4. **Quarterly**: Audit and update security rules

### Metrics to Monitor

- **Code Coverage Trend**: Should increase or remain stable
- **Technical Debt**: Should decrease over time
- **Issue Count**: Track new vs fixed issues
- **Complexity**: Monitor cyclomatic complexity trends
- **Duplication**: Keep below 5% threshold

### Best Practices

1. **Fix issues promptly**: Address Codacy issues in the same PR
2. **Maintain coverage**: Never merge PRs that decrease coverage significantly
3. **Review patterns**: Periodically review and adjust Codacy patterns
4. **Team training**: Ensure team understands Codacy feedback
5. **Gradual improvement**: Set realistic quality gates and improve gradually

## Integration with Other Tools

Codacy integrates well with:

- **SonarCloud**: Both can run simultaneously for comprehensive analysis
- **CodeQL**: Complementary security analysis
- **Codecov**: Parallel coverage reporting
- **GitHub Security**: SARIF results appear in Security tab

## Support and Resources

- **Codacy Documentation**: [docs.codacy.com](https://docs.codacy.com)
- **API Reference**: [api.codacy.com/doc](https://api.codacy.com/doc)
- **Support**: [support.codacy.com](https://support.codacy.com)
- **Community Forum**: [community.codacy.com](https://community.codacy.com)
- **Status Page**: [status.codacy.com](https://status.codacy.com)

## Appendix: Workflow Files

The following workflow files have been updated with Codacy integration:

- `.github/workflows/security.yml` - Security scanning with SARIF upload
- `.github/workflows/ci.yml` - CI pipeline with coverage reporting
- `.github/workflows/test.yml` - Comprehensive test coverage
- `.github/workflows/codacy-quality-gate.yml` - Dedicated quality gate

Each workflow is configured with:
- Proper token authentication
- Error handling with `continue-on-error: true`
- Conditional execution based on token availability
- Secure action pinning with commit SHAs
- Minimal required permissions

---

*Last updated: September 2025*
*Version: 1.0.0*