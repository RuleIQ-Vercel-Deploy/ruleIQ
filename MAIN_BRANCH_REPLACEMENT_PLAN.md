# Main Branch Replacement Plan
## Critical: Replacing Unsafe Main with the-bmad-experiment

**⚠️ CRITICAL**: The current `main` branch contains unsafe code and must be completely replaced with `the-bmad-experiment` branch.

---

## Current Situation

### Branch Status
- **Current Working Branch**: `the-bmad-experiment`
- **Last Safe Commit**: a4aa57210 (feat: Migrate to Neo4j AuraDB)
- **Main Branch Status**: UNSAFE - Contains code that is not compatible with this repository
- **Active Work**: Agents currently working on `the-bmad-experiment`

### Main Branch Issues
- Last commit on main: 426a4f0c4 (Create codeql.yml)
- Main branch has completely different code structure
- SonarCloud scans are running against incorrect main branch

---

## Pre-Migration Checklist

### 1. Ensure All Work is Complete
```bash
# Check for any running agents
ps aux | grep -E "agent|worker"

# Check for uncommitted changes
git status

# Verify all tests pass
make test-unit
```

### 2. Commit All Current Work
```bash
# Stage all necessary changes
git add -A

# Create comprehensive commit
git commit -m "Final commit before main branch replacement

- All agent work completed
- Tests passing
- Documentation updated
"
```

### 3. Push Current Branch
```bash
# Push the-bmad-experiment to remote
git push origin the-bmad-experiment
```

---

## Migration Steps

### Step 1: Create Backup of Current Main
```bash
# Create backup branch of current main (just in case)
git checkout main
git checkout -b main-backup-$(date +%Y%m%d-%H%M%S)
git push origin main-backup-$(date +%Y%m%d-%H%M%S)
```

### Step 2: Force Update Main Branch
```bash
# Switch to the-bmad-experiment
git checkout the-bmad-experiment

# Force main to match the-bmad-experiment exactly
git branch -f main the-bmad-experiment

# Alternative method if above doesn't work
git checkout main
git reset --hard the-bmad-experiment
```

### Step 3: Push Updated Main to Remote
```bash
# Force push the new main (requires admin permissions)
git push origin main --force-with-lease

# If force-with-lease fails, use force (more dangerous)
git push origin main --force
```

### Step 4: Update Default Branch on GitHub
1. Go to GitHub repository settings
2. Navigate to Branches
3. Change default branch from `main` to `the-bmad-experiment` temporarily
4. Delete and recreate `main` from `the-bmad-experiment`
5. Set `main` back as default branch

---

## Alternative Safe Method (If Force Push is Restricted)

### Using Pull Request
```bash
# Create new branch from the-bmad-experiment
git checkout the-bmad-experiment
git checkout -b replace-main-safely

# Push to remote
git push origin replace-main-safely

# Create PR to merge into main with "Create a merge commit" disabled
# Select "Squash and merge" or "Rebase and merge"
```

### Delete and Recreate Main
```bash
# Delete main locally
git branch -D main

# Recreate main from the-bmad-experiment
git checkout the-bmad-experiment
git checkout -b main

# Push new main
git push origin main --force-with-lease
```

---

## Post-Migration Verification

### 1. Verify Branch State
```bash
# Confirm main matches the-bmad-experiment
git diff main the-bmad-experiment
# Should show no differences

# Check commit history
git log --oneline -n 10 main
# Should show commits from the-bmad-experiment
```

### 2. Run SonarCloud Scan
```bash
# Run scan on new main branch
doppler run -- sonar-scanner \
  -Dsonar.projectKey=ruliq-compliance-platform \
  -Dsonar.organization=omara1-bakri \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.branch.name=main
```

### 3. Verify CI/CD
- Check GitHub Actions run on new main
- Verify all checks pass
- Confirm deployments work

### 4. Update Team
```markdown
## Team Notification Template

Subject: Main Branch Updated - Action Required

Team,

The main branch has been replaced with the safe code from the-bmad-experiment branch.

**Actions Required:**
1. Delete your local main branch: `git branch -D main`
2. Fetch the new main: `git fetch origin main`
3. Checkout new main: `git checkout main`
4. Rebase any feature branches: `git rebase main`

**Do NOT merge old main into your branches**

Contact me if you have any issues.
```

---

## Rollback Plan (If Needed)

### Quick Rollback
```bash
# If backup was created
git checkout main
git reset --hard main-backup-[timestamp]
git push origin main --force

# Or restore from specific commit
git checkout main  
git reset --hard 426a4f0c4  # Last known main commit
git push origin main --force
```

---

## Important Notes

1. **DO NOT** merge main into the-bmad-experiment - main is unsafe
2. **DO NOT** cherry-pick from main - all code there is incompatible
3. **ENSURE** all agents have completed work before migration
4. **BACKUP** everything before proceeding
5. **COMMUNICATE** with team before and after migration

---

## Commands Summary

```bash
# Quick migration (when ready)
git checkout the-bmad-experiment
git branch -f main the-bmad-experiment
git push origin main --force-with-lease

# Verify success
git diff main the-bmad-experiment  # Should be empty
```

---

**Created**: $(date)
**Priority**: CRITICAL
**Timeline**: Execute as soon as all agent work is complete