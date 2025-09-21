# Worktree 4: File Inclusion & Test Security

## 🔴 High Priority
1. **Exposed secret in sonar scan debug**
   - File: `sonar-scan-debug.txt`
   - Action: Remove file, add to .gitignore

2. **Exposed secrets in purge scripts**
   - Files: `purge_secrets.sh`, `GOOGLE_AI_INTEGRATION.md` (6 secrets)
   - Action: Sanitize scripts, use secure deletion

3. **Exposed secrets in Archon config**
   - Files: `archon_supabase_config.txt` (duplicated)
   - Action: Move to secure configuration

## 🟠 Medium Priority
4. **Potential file inclusion attack**
   - Files: `reporting_nodes_real.py`, `reporting_nodes.py` (15+ files)
   - Action: Validate file paths, prevent directory traversal

5. **Generic passwords in vulnerability fixes**
   - Files: `fix_security_vulnerabilities.py` (duplicated)
   - Action: Remove example passwords

6. **GCP API key in validation report**
   - Files: `doppler_validation_report.md` (duplicated)
   - Action: Redact keys in documentation

7. **JWT tokens in Archon fixes**
   - Files: `fix_archon_docs.py` (multiple)
   - Action: Use token management system

## 🟡 Low Priority
8. **Exposed secrets in RAG client**
   - Files: `abacus_rag_client.py`, `ruff.log` (16 secrets)
   - Action: Clean up logs, secure API keys

9. **Exposed secrets in test results**
   - Files: `results.json`, `newman-environment-with-secrets.json` (21 secrets)
   - Action: Sanitize test outputs

10. **Exposed secrets in penetration testing**
   - Files: `PENETRATION_TESTING_SCENARIOS.md` (4 secrets, duplicated)
   - Action: Use example values in docs

11. **OpenAI sensitive info in logs**
   - Action: Configure OpenAI client to filter logs

12. **Generic API keys in test files**
   - Files: `locustfile.py`, `test_auth_flow.py`, `test_user_management_endpoints.py`
   - Action: Use environment-specific test keys