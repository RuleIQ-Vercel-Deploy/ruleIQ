# Worktree 2: XML/XSS Security & Infrastructure Secrets

## 🔴 High Priority
1. **Unsafe XML parsing (XXE risk)**
   - File: `regulation_api_client.py`
   - Action: Use defusedxml library, disable external entities

2. **Exposed secrets in environment templates**
   - Files: `env.comprehensive.template`, `env.template` (15 secrets)
   - Action: Replace with placeholders, add to security docs

3. **Exposed secrets in blocker files**
   - Files: `blocker_issues_detailed.json` (50+ secrets, duplicated)
   - Action: Sanitize JSON files, remove sensitive data

## 🟠 Medium Priority
4. **DoS vulnerability in starlette**
   - Action: Update starlette to patched version

5. **Unsafe GitHub Actions trigger**
   - File: `deployment.yml`
   - Action: Pin actions, add permission restrictions

6. **Exposed secrets in .env**
   - File: `.env` (10 secrets)
   - Action: Remove from git, use .env.example

7. **GCP API key exposed**
   - Files: `basic_results.json` (duplicated)
   - Action: Revoke and rotate GCP keys

## 🟡 Low Priority
8. **XSS risk via Jinja2 template**
   - File: `report_generator.py`
   - Action: Enable autoescape, sanitize inputs

9. **Potential SSRF via user input**
   - File: `regulation_api_client.py`
   - Action: Validate URLs, whitelist domains

10. **Base64 encoded passwords**
   - Files: `layout.js.html`, `page.js.html`
   - Action: Remove encoded credentials

11. **Monitor state secrets**
   - File: `monitor_state.json` (11 secrets)
   - Action: Move to secure storage