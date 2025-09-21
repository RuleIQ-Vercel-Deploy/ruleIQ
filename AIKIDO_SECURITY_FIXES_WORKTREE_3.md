# Worktree 3: Script Secrets & Database Security

## 🔴 High Priority
1. **Exposed secrets in run scripts**
   - Files: `run-sonarcloud.sh`, `SONARCLOUD_SETUP.md` (9 secrets)
   - Action: Move secrets to env vars, update documentation

2. **Exposed secrets in UK compliance files**
   - Files: `uk_4b79635888269eb10ad301333016f878.json` (3 secrets, duplicated)
   - Action: Sanitize compliance data, use config management

3. **Exposed secret in Doppler script**
   - File: `doppler-neo4j-configure.sh`
   - Action: Use Doppler secrets management properly

## 🟠 Medium Priority
4. **Generic API Key in security scan**
   - File: `security-scan.md`
   - Action: Replace with documentation placeholders

5. **Generic password in test harness**
   - File: `test-harness.md`
   - Action: Use example credentials in docs

6. **Exposed secrets in check scripts**
   - Files: `check_sonar_results.py`, `get_detailed_blockers.py`
   - Action: Remove hardcoded credentials

7. **Generic passwords in scrapers**
   - Files: `ingestion_fixed.py`, `regulation_scraper.py`
   - Action: Use secure credential storage

## 🟡 Low Priority
8. **3rd party GitHub Actions not pinned**
   - Files: `ci.yml`, `deploy-production.yml` (20+ files)
   - Action: Pin all actions to specific commits

9. **JWT tokens in Supabase setup**
   - Files: `setup_supabase_schema.py`, `import_full_documents.py`
   - Action: Use environment variables

10. **Exposed secrets in test files**
   - Files: `test_credential_encryption.py` (duplicated)
   - Action: Use mock values

11. **Generic API keys in auth tests**
   - Files: `auth.test.ts` (duplicated)
   - Action: Replace with test fixtures