# Aikido Security Fix Implementation Plan

## Overview
This document outlines the comprehensive plan to address all security vulnerabilities identified by Aikido across the RuleIQ codebase. Issues are organized by priority and include detailed remediation steps.

## Execution Strategy
1. **Phase 1**: High Priority (Critical vulnerabilities)
2. **Phase 2**: Medium Priority (Moderate risk)
3. **Phase 3**: Low Priority (Best practices)
4. **Phase 4**: Verification & Testing

---

## 🔴 HIGH PRIORITY FIXES (Execute First)

### 1. XXE (XML External Entity) Vulnerability
**File**: `api/background/regulation_api_client.py`
**Risk**: Unsafe XML parsing can lead to data exfiltration
**Fix**:
```python
# Install: pip install defusedxml
from defusedxml import ElementTree as ET
# Replace all xml.etree.ElementTree usage with defusedxml
```
**Verification**: Test XML parsing with malicious payloads

### 2. Exposed Secrets in Environment Templates
**Files**: `env.comprehensive.template`, `env.template`
**Count**: 15 exposed secrets
**Fix**:
- Replace actual values with placeholders: `YOUR_API_KEY_HERE`
- Add security documentation explaining secure secret management
- Create `.env.example` with safe placeholders
**Verification**: Scan files for sensitive patterns

### 3. Exposed Secrets in Blocker Files
**Files**: `blocker_issues_detailed.json` (50+ duplicated secrets)
**Fix**:
- Sanitize JSON files using regex replacement
- Remove all API keys, tokens, passwords
- Replace with mock values for testing
**Verification**: grep for common secret patterns

### 4. Exposed Secrets in Run Scripts
**Files**: `run-sonarcloud.sh`, `SONARCLOUD_SETUP.md` (9 secrets)
**Fix**:
- Move all secrets to environment variables
- Update scripts to use: `${SONAR_TOKEN}`
- Document in `.env.example`
**Verification**: Ensure scripts run with env vars only

### 5. UK Compliance File Secrets
**Files**: `uk_4b79635888269eb10ad301333016f878.json` (3 duplicated)
**Fix**:
- Sanitize compliance data
- Move sensitive config to secure storage
- Use reference IDs instead of actual secrets
**Verification**: Review JSON for any remaining secrets

### 6. Doppler Script Security
**File**: `doppler-neo4j-configure.sh`
**Fix**:
- Use Doppler CLI properly: `doppler run -- command`
- Remove hardcoded credentials
- Document Doppler setup process
**Verification**: Test script with Doppler integration

---

## 🟠 MEDIUM PRIORITY FIXES

### 7. DoS Vulnerability in Starlette
**Action**: Update dependency
```bash
pip install --upgrade starlette>=0.27.0
```
**Verification**: Check `pip list | grep starlette`

### 8. Insecure GitHub Actions
**File**: `deployment.yml` and all workflow files
**Fix**:
```yaml
# Pin actions to specific commits
uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab # v3.5.2

# Add permissions block
permissions:
  contents: read
  pull-requests: write
```
**Verification**: Validate all workflows have pinned versions

### 9. .env File in Repository
**Files**: `.env` (10 secrets)
**Fix**:
```bash
# Add to .gitignore
echo ".env" >> .gitignore
# Remove from git history
git rm --cached .env
# Create template
cp .env .env.example
# Sanitize .env.example
```
**Verification**: Ensure .env not tracked

### 10. GCP API Key Rotation
**Files**: `basic_results.json`
**Fix**:
- Revoke exposed keys in GCP Console
- Generate new keys
- Store in secure secret manager
- Update application to use env vars
**Verification**: Test with new keys

### 11. Generic API Keys in Documentation
**Files**: `security-scan.md`, `test-harness.md`
**Fix**:
- Replace with documentation placeholders
- Use format: `<YOUR_API_KEY>`
**Verification**: grep for actual keys

### 12. Python Script Credentials
**Files**: `check_sonar_results.py`, `get_detailed_blockers.py`, `ingestion_fixed.py`, `regulation_scraper.py`
**Fix**:
```python
import os
api_key = os.environ.get('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable required")
```
**Verification**: Test scripts with env vars

---

## 🟡 LOW PRIORITY FIXES

### 13. XSS Risk in Jinja2
**File**: `report_generator.py`
**Fix**:
```python
from jinja2 import Environment, FileSystemLoader
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True  # Enable autoescape
)
# Sanitize all user inputs before rendering
```
**Verification**: Test with XSS payloads

### 14. SSRF Protection
**File**: `regulation_api_client.py`
**Fix**:
```python
from urllib.parse import urlparse

ALLOWED_DOMAINS = ['api.example.com', 'trusted-service.com']

def validate_url(url):
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError(f"Domain {parsed.hostname} not allowed")
    return url
```
**Verification**: Test with malicious URLs

### 15. Base64 Encoded Passwords
**Files**: `layout.js.html`, `page.js.html`
**Fix**:
- Remove all base64 encoded credentials
- Use proper authentication flow
**Verification**: Search for base64 patterns

### 16. Monitor State Secrets
**File**: `monitor_state.json` (11 secrets)
**Fix**:
- Move to secure key-value store (Redis/Vault)
- Encrypt sensitive fields
**Verification**: Ensure file contains no plain secrets

### 17. Pin GitHub Actions
**Files**: All `.github/workflows/*.yml` files
**Fix**:
```bash
# Use a tool like pin-github-action
npm install -g pin-github-action
pin-github-action .github/workflows/
```
**Verification**: All actions have commit SHAs

### 18. JWT Tokens in Supabase
**Files**: `setup_supabase_schema.py`, `import_full_documents.py`
**Fix**:
```python
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
```
**Verification**: No hardcoded JWTs

### 19. Test File Credentials
**Files**: `test_credential_encryption.py`, `auth.test.ts`
**Fix**:
- Use mock values: `MOCK_API_KEY_12345`
- Use test fixtures
**Verification**: Tests pass with mocks

---

## Implementation Order

### Day 1: Critical Security (High Priority)
1. XXE vulnerability fix
2. Environment template sanitization
3. Blocker file cleanup
4. Script secret removal
5. UK compliance sanitization
6. Doppler configuration

### Day 2: Infrastructure Security (Medium Priority)
7. Starlette update
8. GitHub Actions security
9. .env file removal
10. GCP key rotation
11. Documentation sanitization
12. Python script credentials

### Day 3: Best Practices (Low Priority)
13. XSS protection
14. SSRF validation
15. Base64 password removal
16. Monitor state encryption
17. GitHub Actions pinning
18. Supabase JWT security
19. Test credential mocking

---

## Verification Checklist

- [ ] Run Aikido security scan after each phase
- [ ] No secrets in git history (use git-secrets)
- [ ] All tests pass with new configuration
- [ ] Documentation updated with security practices
- [ ] CI/CD pipelines functional
- [ ] Production deployment successful

## Rollback Plan

If any fix causes issues:
1. Revert specific commit
2. Restore from backup (for data files)
3. Re-run previous working configuration
4. Document issue for alternative approach

## Security Tools Setup

```bash
# Install security scanning tools
pip install safety bandit
npm install -g snyk

# Git secrets prevention
brew install git-secrets
git secrets --install
git secrets --register-aws
```

## Post-Implementation

1. Schedule weekly security scans
2. Set up automated secret detection in CI
3. Create security incident response plan
4. Train team on secure coding practices

---

**APPROVAL REQUIRED**: Please review this plan before proceeding with implementation.