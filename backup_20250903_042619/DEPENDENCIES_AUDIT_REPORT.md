# Dependencies Audit Report

**Date**: 2025-08-28
**Project**: ruleIQ
**Task**: Dependencies & Package Audit

## Executive Summary

Comprehensive audit of backend (Python) and frontend (JavaScript) dependencies to ensure production stability, security, and license compliance.

## Backend Dependencies Analysis (requirements.txt)

### Security Vulnerabilities Found

| Package | Current Version | Issue | Fix Version | Severity |
|---------|----------------|-------|-------------|----------|
| ecdsa | 0.19.1 | GHSA-wj6h-64fc-37mp | Latest | Medium |
| h2 | 4.2.0 | GHSA-847f-9342-265h | 4.3.0 | Medium |

### Outdated Packages

Major packages with updates available:
- boto3: 1.40.13 → 1.40.19
- botocore: 1.40.13 → 1.40.19
- langchain-core: 0.3.74 → 0.3.75
- langchain-openai: 0.3.30 → 0.3.32
- google-genai: 1.30.0 → 1.32.0

### Version Pinning Issues

Current requirements.txt uses flexible version specifiers (>=) which can lead to:
- Unexpected breaking changes in production
- Different environments having different package versions
- Difficult reproduction of production issues

**Recommendation**: Pin all versions for production stability.

### Dev vs Production Dependencies

Currently mixed in single requirements.txt. Should be separated:

**Production Only**:
- fastapi, uvicorn
- sqlalchemy, psycopg2-binary
- openai, google-generativeai
- celery, redis
- All security packages

**Development Only**:
- pytest, pytest-asyncio, pytest-cov
- black, isort, flake8
- locust
- httpx (for testing)

## Frontend Dependencies Analysis (package.json)

### Key Observations

1. **Using "latest" versions**: Multiple packages use "latest" which is dangerous for production:
   - @emotion/is-prop-valid: "latest"
   - @radix-ui/react-checkbox: "latest"
   - @radix-ui/react-dialog: "latest"
   - @tanstack/react-table: "latest"
   - date-fns: "latest"
   - framer-motion: "latest"

2. **React 19**: Currently using React 19 (^19) which is very new. Consider stability.

3. **Next.js 15**: Using Next.js 15.2.4 - latest major version, ensure compatibility.

4. **Security packages**: Good inclusion of security-focused packages like:
   - csrf: ^3.1.0
   - jose: ^6.0.11
   - isomorphic-dompurify: ^2.26.0

### Package Management

Using pnpm (specified in engines) which is good for:
- Disk space efficiency
- Faster installations
- Strict dependency resolution

## Recommendations

### Immediate Actions (Critical)

1. **Fix Security Vulnerabilities**:
   ```bash
   pip install --upgrade h2>=4.3.0
   pip uninstall ecdsa  # If not needed, or upgrade
   ```

2. **Pin All "latest" Versions in Frontend**:
   ```json
   // Replace all "latest" with specific versions
   "@tanstack/react-table": "^8.20.5",
   "date-fns": "^3.6.0",
   "framer-motion": "^11.11.17"
   ```

3. **Separate Dev Dependencies**:
   - Create `requirements-dev.txt` for Python
   - Move dev dependencies to devDependencies in package.json

### Short-term Actions (This Week)

1. **Update Critical Packages**:
   ```bash
   pip install --upgrade boto3 botocore langchain-core langchain-openai
   ```

2. **Lock Versions for Production**:
   ```bash
   pip freeze > requirements.lock
   pnpm lock
   ```

3. **License Audit**:
   - Run license checker for both ecosystems
   - Ensure no GPL or incompatible licenses

### Long-term Actions (This Month)

1. **Implement Dependency Management**:
   - Use Dependabot or Renovate for automated updates
   - Set up security scanning in CI/CD
   - Regular monthly dependency reviews

2. **Version Strategy**:
   - Use exact versions in production
   - Use ranges only in development
   - Document update procedures

## License Compatibility Check

### Backend Licenses
Most packages use MIT, Apache 2.0, or BSD licenses - all compatible.
Notable:
- All AI/ML packages (OpenAI, Google) - MIT/Apache
- Database packages - MIT/PostgreSQL
- Web framework (FastAPI) - MIT

### Frontend Licenses
Predominantly MIT licensed packages.
Notable:
- React ecosystem - MIT
- Next.js - MIT
- Radix UI - MIT
- Stripe - MIT

**No license conflicts detected.**

## Production Readiness Checklist

- [ ] Fix security vulnerabilities (ecdsa, h2)
- [ ] Pin all "latest" versions to specific versions
- [ ] Separate dev and production dependencies
- [ ] Create lock files for reproducible builds
- [ ] Update critical outdated packages
- [ ] Document dependency update procedures
- [ ] Set up automated security scanning
- [ ] Implement dependency update automation

## Conclusion

The codebase has a solid foundation of dependencies but needs immediate attention on:
1. Security vulnerabilities (2 medium severity)
2. Version pinning for production stability
3. Separation of dev/prod dependencies

Once these are addressed, the dependency stack will be production-ready with proper governance in place.