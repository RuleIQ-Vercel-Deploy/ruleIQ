# CI Scripts Documentation

This directory contains utility scripts for continuous integration (CI) validation and maintenance.

## Scripts Overview

### TODO Management Scripts

#### 1. `scan_todos.py`

**Purpose**: Scans the codebase for TODO/FIXME/HACK/XXX markers and generates reports.

**Features**:
- Scans all git-tracked files
- Categorizes TODOs by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Detects issue references: `TODO(#123): Description`
- Generates reports in multiple formats (markdown, JSON, CSV)
- Enforces policy in CI/CD

**Usage**:
```bash
# Generate markdown report
python scripts/ci/scan_todos.py --format markdown --output TODO_INVENTORY.md

# Generate JSON report
python scripts/ci/scan_todos.py --format json --output TODO_INVENTORY.json

# Enforce policy (fail if non-compliant TODOs found)
python scripts/ci/scan_todos.py --enforce --severity CRITICAL --severity HIGH

# Show statistics only
python scripts/ci/scan_todos.py --stats-only

# Filter by severity
python scripts/ci/scan_todos.py --severity CRITICAL
```

**Exit codes**:
- `0`: No policy violations or successful scan
- `1`: Non-compliant TODOs found (when using `--enforce`)

#### 2. `create_todo_issues.py`

**Purpose**: Automatically creates GitHub issues for TODOs without issue references.

**Features**:
- Creates GitHub issues via API
- Groups similar TODOs to reduce issue count
- Assigns appropriate labels (severity, area, type)
- Checks for existing issues to avoid duplicates
- Generates mapping file for update script

**Usage**:
```bash
# Dry run (show what would be created)
python scripts/ci/create_todo_issues.py --token $GITHUB_TOKEN --repo OmarA1-Bakri/ruleIQ --dry-run

# Create issues for CRITICAL severity
python scripts/ci/create_todo_issues.py --token $GITHUB_TOKEN --repo OmarA1-Bakri/ruleIQ --severity CRITICAL

# Batch similar TODOs into single issues
python scripts/ci/create_todo_issues.py --token $GITHUB_TOKEN --repo OmarA1-Bakri/ruleIQ --batch-similar
```

**Environment variables**:
- `GITHUB_TOKEN`: GitHub personal access token (required)

**Exit codes**:
- `0`: All operations successful
- `1`: Failed to create one or more issues

#### 3. `update_todo_references.py`

**Purpose**: Updates TODO comments in source files to include GitHub issue references.

**Features**:
- Updates TODO comments in place
- Supports multiple comment styles (#, //, /* */, <!-- -->)
- Batch update from mapping file
- Interactive mode for manual review
- Dry run mode for safety

**Usage**:
```bash
# Batch update from mapping file
python scripts/ci/update_todo_references.py --mapping issues.json

# Interactive mode
python scripts/ci/update_todo_references.py --interactive

# Update specific TODO
python scripts/ci/update_todo_references.py --file services/ai/assistant.py --line 234 --issue 567

# Dry run
python scripts/ci/update_todo_references.py --mapping issues.json --dry-run
```

**Exit codes**:
- `0`: All updates successful
- `1`: One or more updates failed

### CI Validation Scripts

### 1. `validate_ci_dependencies.py`

**Purpose**: Validates that all required dependencies for CI are properly installed and configured.

**What it checks**:
- Python package imports (FastAPI, SQLAlchemy, pytest, etc.)
- Database connectivity (PostgreSQL and Redis sockets)
- Required environment variables
- Port availability
- Requirements files existence
- Critical application module imports

**Usage**:
```bash
python scripts/ci/validate_ci_dependencies.py
```

**Exit codes**:
- `0`: All validations passed
- `1`: One or more validations failed

**Environment variables**:
- `DATABASE_URL`: PostgreSQL connection string (required)
- `REDIS_URL`: Redis connection string (required)
- `SECRET_KEY`: Application secret key (required)
- `JWT_SECRET_KEY`: JWT signing key (required)
- `ENVIRONMENT`: Runtime environment (required)

### 2. `fix_broken_ci_steps.py`

**Purpose**: Analyzes GitHub Actions workflow files to detect and optionally fix common issues.

**Features**:
- Detects missing file references in workflow steps
- Identifies missing checkout actions
- Finds undefined environment variables
- Suggests fixes for identified issues
- Can automatically apply certain fixes (with `--fix` flag)

**Usage**:
```bash
# Report issues only (no changes made)
python scripts/ci/fix_broken_ci_steps.py --report-only

# Attempt to fix issues automatically
python scripts/ci/fix_broken_ci_steps.py --fix

# Analyze workflows in a different directory
python scripts/ci/fix_broken_ci_steps.py --report-only --repo-root /path/to/repo
```

**What it fixes**:
- Adds file existence guards to prevent failures on missing scripts
- Suggests adding checkout steps when needed
- Identifies environment variables that need definition

**Exit codes**:
- `0`: No issues found
- `1`: Issues detected (whether fixed or not)

## Root-Level Validation Scripts

### 1. `validate_endpoints.py`

**Location**: Repository root (`/validate_endpoints.py`)

**Purpose**: Validates API endpoints using FastAPI's TestClient for in-process testing.

**Features**:
- Tests core endpoints (`/health`, `/ready`, `/openapi.json`)
- Discovers and tests all GET endpoints without path parameters
- Validates OpenAPI spec JSON structure
- Supports external server testing via `BASE_URL` environment variable
- Handles authentication for protected endpoints

**Usage**:
```bash
# Test with in-process TestClient (default)
python validate_endpoints.py

# Test against external server
BASE_URL=http://localhost:8000 python validate_endpoints.py

# With authentication token
AUTH_TOKEN=your_token_here python validate_endpoints.py

# Filter specific endpoints
ENDPOINT_FILTER="/api/users,/api/posts" python validate_endpoints.py
```

**Environment variables**:
- `BASE_URL`: External server URL (optional, uses TestClient if not set)
- `AUTH_TOKEN`: Bearer token for authenticated endpoints (optional)
- `ENDPOINT_FILTER`: Comma-separated list of endpoints to test (optional)

### 2. `database_health_check.py`

**Location**: Repository root (`/database_health_check.py`)

**Purpose**: Validates database connectivity and performs health checks.

**Features**:
- Tests PostgreSQL connectivity and operations
  - Connection test
  - SELECT queries
  - Transaction operations (BEGIN, INSERT, ROLLBACK)
- Tests Redis connectivity and operations
  - PING command
  - SET/GET/DEL operations
  - Server info retrieval
- Measures response times
- Supports verbose output for debugging

**Usage**:
```bash
# Basic health check
python database_health_check.py

# Verbose output
python database_health_check.py --verbose

# Custom timeout
python database_health_check.py --timeout 30

# Environment variable for verbose
VERBOSE=true python database_health_check.py
```

**Environment variables**:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:pass@localhost/db`)
- `REDIS_URL`: Redis connection string (e.g., `redis://localhost:6379`)
- `VERBOSE`: Set to "true" for detailed output (optional)

**Exit codes**:
- `0`: All database checks passed
- `1`: One or more database checks failed

## TODO Management Workflow Integration

The TODO management scripts are integrated into development workflows:

### Pre-commit Hooks (`.pre-commit-config.yaml`):
```yaml
- id: enforce-todo-policy
  name: Enforce TODO policy (require issue references)
  entry: python scripts/ci/scan_todos.py --enforce --severity CRITICAL --severity HIGH
  language: system
  pass_filenames: false
  always_run: true

- id: validate-todo-format
  name: Validate TODO format
  entry: bash -c 'if git diff --cached --name-only | xargs grep -nE "(TODO|FIXME|HACK|XXX)(?!\(#\d+\))" 2>/dev/null | grep -v "tests/" | grep -v "\.md"; then echo "ERROR: Found TODO without issue reference. Format: TODO(#123): Description"; exit 1; fi || exit 0'
  language: system
  pass_filenames: false
```

### GitHub Actions (`.github/workflows/todo-enforcement.yml`):
- Runs on every push and pull request
- Generates weekly TODO inventory reports (Mondays at 9 AM UTC)
- Posts helpful comments on PRs with violations
- Creates automated weekly report issues

See [TODO Management Guide](../../docs/TODO_MANAGEMENT_GUIDE.md) for complete documentation.

## CI Workflow Integration

These scripts are integrated into the GitHub Actions workflows:

### In `.github/workflows/ci.yml`:
```yaml
- name: Validate CI dependencies
  run: |
    test -f scripts/ci/validate_ci_dependencies.py && \
    python scripts/ci/validate_ci_dependencies.py || \
    echo "Script missing; skipping"

- name: Check database health
  run: |
    test -f database_health_check.py && \
    python database_health_check.py | tee db_health.log || \
    echo "Script missing; skipping"

- name: Validate API endpoints
  run: |
    test -f validate_endpoints.py && \
    python validate_endpoints.py | tee endpoint_validation.log || \
    echo "Script missing; skipping"
```

### Artifact Collection:
Validation outputs are captured and uploaded as artifacts for debugging:

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: validation-logs
    path: |
      endpoint_validation.log
      db_health.log
```

## Best Practices

1. **Run validation early**: Place validation steps early in the CI pipeline to fail fast
2. **Use guards**: Always use file existence checks to prevent CI failures on missing scripts
3. **Capture output**: Use `tee` to both display and save output for artifact upload
4. **Environment isolation**: Ensure CI environment variables don't leak sensitive data
5. **Progressive enhancement**: Scripts should degrade gracefully when optional dependencies are missing

## Troubleshooting

### Common Issues:

1. **"Module not found" errors**:
   - Ensure all requirements are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

2. **Database connection failures**:
   - Verify DATABASE_URL and REDIS_URL are correctly set
   - Ensure database services are running
   - Check network connectivity and firewall rules

3. **Port conflicts**:
   - The scripts check for port availability but don't fail if ports are in use
   - This is expected if services are already running

4. **Workflow parsing errors**:
   - Ensure workflow YAML files are valid
   - Use a YAML linter to check syntax

## Contributing

When adding new validation scripts:
1. Follow the existing pattern of exit codes (0 for success, 1 for failure)
2. Support both CLI arguments and environment variables for configuration
3. Provide clear output with emoji indicators for status
4. Include the script in this documentation
5. Add appropriate guards in CI workflows

## License

These scripts are part of the RuleIQ project and follow the same license terms.