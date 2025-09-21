# Worktree 1: Critical Dependencies & Authentication Security

## 🚨 Critical Priority
1. **SSRF vulnerability in langchain-community**
   - Status: PR open
   - Action: Review and merge PR, update dependency

2. **SQL Injection attack possible in langchain**
   - Status: PR open
   - Action: Review and merge PR, update dependency

## 🔴 High Priority
3. **Remote Code Execution risk – use of pickle**
   - Files: `optimization.py`, `agent_manager.py`
   - Action: Replace pickle with safe serialization (JSON/msgpack)

4. **Exposed secrets in app.log.1**
   - Files: `app.log.1` (4 secrets)
   - Action: Purge secrets, add to .gitignore, rotate credentials

## 🟠 Medium Priority
5. **Cryptographic signature forgery in python-jose**
   - Action: Update python-jose to latest version

6. **JWT tokens exposed in migration scripts**
   - Files: `migrate_archon_data.py`
   - Action: Remove hardcoded tokens, use env variables

7. **Generic password fields**
   - Files: `debug_api_analysis.py`
   - Action: Remove or mask sensitive fields

## 🟡 Low Priority
8. **Generic API Keys in test files**
   - Files: `test_api_performance.py`, `test_websocket_security.py`
   - Action: Use mock values in tests

9. **Sensitive info exposure in sentry-sdk**
   - Action: Configure Sentry to filter sensitive data

10. **Test environment secrets**
   - Files: `.env.test`
   - Action: Use example values, document in .env.example