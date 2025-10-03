# Neon Test Database Branch Setup

**Date**: 2025-09-30
**Purpose**: Create a dedicated test database branch in Neon for pytest execution

---

## Problem Statement

Current test configuration (`.env.test`) points to `localhost:5433` which isn't running, causing all pytest tests to skip.

```bash
# Current .env.test (BROKEN)
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/compliance_test
```

**Solution**: Create a Neon branch for testing that mirrors production structure but is isolated.

---

## Setup Instructions

### Step 1: Authenticate with Neon CLI

```bash
neonctl auth
```

This will open a browser for OAuth authentication.

### Step 2: List Your Projects

```bash
neonctl projects list
```

Expected output should show your project: `ep-sweet-truth-a89at3wo`

### Step 3: Create Test Branch

```bash
# Create a branch named "test" from main branch
neonctl branches create --project-id ep-sweet-truth-a89at3wo --name test --parent main
```

Alternative if you need to specify the parent:
```bash
neonctl branches create --project-id ep-sweet-truth-a89at3wo --name test
```

### Step 4: Get Connection String for Test Branch

```bash
neonctl connection-string --project-id ep-sweet-truth-a89at3wo --branch test --role neondb_owner
```

This will output something like:
```
postgresql://neondb_owner:npg_xxxxx@ep-sweet-truth-a89at3wo-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
```

### Step 5: Update .env.test

Replace the DATABASE_URL in `.env.test` with the test branch connection string:

```bash
# Before
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/compliance_test

# After (with your actual credentials)
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_xxxxx@ep-sweet-truth-a89at3wo-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require&options=endpoint%3Dep-sweet-truth-a89at3wo-test
```

**Note**: Make sure to add `+asyncpg` after `postgresql` for SQLAlchemy compatibility.

### Step 6: Initialize Test Database Schema

```bash
source .venv/bin/activate

# Set environment to use test database
export TESTING=true
export DATABASE_URL="<your-test-branch-connection-string>"

# Run database initialization
python database/init_db.py
```

### Step 7: Verify Tests Run

```bash
pytest tests/unit/ai/test_evidence_service_functional.py -v
```

All tests should now execute instead of skipping!

---

## Automated Script (Alternative)

If you want to automate this, here's a script:

```bash
#!/bin/bash
# setup-neon-test-branch.sh

set -e

PROJECT_ID="ep-sweet-truth-a89at3wo"
BRANCH_NAME="test"

echo "🔧 Creating Neon test branch..."

# Create branch
neonctl branches create \
  --project-id "$PROJECT_ID" \
  --name "$BRANCH_NAME" \
  --parent main

echo "✅ Branch created: $BRANCH_NAME"

# Get connection string
echo "📋 Fetching connection string..."
CONNECTION_STRING=$(neonctl connection-string \
  --project-id "$PROJECT_ID" \
  --branch "$BRANCH_NAME" \
  --role neondb_owner)

# Convert to asyncpg format
ASYNCPG_URL=$(echo "$CONNECTION_STRING" | sed 's/postgresql:/postgresql+asyncpg:/')

echo "✅ Connection string obtained"
echo ""
echo "📝 Update .env.test with this connection string:"
echo ""
echo "DATABASE_URL=$ASYNCPG_URL&channel_binding=require"
echo ""
echo "🔧 Next steps:"
echo "1. Update .env.test with the connection string above"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: python database/init_db.py (with TEST env)"
echo "4. Run: pytest tests/unit/ai/test_evidence_service_functional.py -v"
```

---

## Benefits of Neon Branch for Testing

1. **Isolation**: Test data doesn't affect production
2. **Reset**: Can easily delete and recreate branch
3. **Speed**: No need to run local PostgreSQL
4. **CI/CD**: Can use same approach in GitHub Actions
5. **Parity**: Test against same PostgreSQL version as production

---

## Branch Management

### List All Branches
```bash
neonctl branches list --project-id ep-sweet-truth-a89at3wo
```

### Delete Test Branch (to reset)
```bash
neonctl branches delete --project-id ep-sweet-truth-a89at3wo --branch test
```

### Reset Test Data
```bash
# Delete and recreate
neonctl branches delete --project-id ep-sweet-truth-a89at3wo --branch test
neonctl branches create --project-id ep-sweet-truth-a89at3wo --name test --parent main

# Reinitialize schema
python database/init_db.py
```

---

## Cost Considerations

Neon branches are:
- ✅ Included in free tier (one branch free)
- ✅ Only charged when actively querying
- ✅ Auto-suspend when idle
- ✅ Share compute with parent branch in free tier

For this project, a test branch should have **minimal to zero additional cost**.

---

## Troubleshooting

### Issue: "Branch already exists"
```bash
neonctl branches delete --project-id ep-sweet-truth-a89at3wo --branch test
# Then create again
```

### Issue: "Project not found"
```bash
# List all projects to find correct ID
neonctl projects list
```

### Issue: "Connection string not working"
- Ensure `+asyncpg` is in the URL
- Ensure `sslmode=require` is present
- Ensure `channel_binding=require` is present
- Check if endpoint parameter is needed

### Issue: "Tests still skip"
```bash
# Check if .env.test is being loaded
pytest tests/unit/ai/test_evidence_service_functional.py -v --envfile .env.test
```

---

## Alternative: Use Doppler for Test Secrets

If you use Doppler for production, create a `test` config:

```bash
doppler setup --config test
doppler secrets set DATABASE_URL="<neon-test-branch-url>" --config test

# Run tests with Doppler
doppler run --config test -- pytest tests/unit/ai/
```

---

## Next Steps After Setup

Once test branch is configured:

1. ✅ All pytest tests will run (no more skipping)
2. ✅ Can verify functional tests pass via pytest
3. ✅ Can integrate into CI/CD pipeline
4. ✅ Future ported methods can be tested immediately

---

**Status**: Ready to execute - requires user to run neonctl commands with their credentials.
