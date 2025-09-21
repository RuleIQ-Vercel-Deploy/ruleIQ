# SonarCloud Fix Task Assignments

## Overview
Parallel execution of SonarCloud fixes across 6 worktree branches to maximize efficiency.

## Branch Assignments

### 1. sonar-backend-fixes (/home/omar/Documents/ruleIQ.worktrees/sonar-backend)
**Priority: HIGH - Critical Bugs**
- [ ] Fix api/routers/chat.py - Return type 'IQComplianceAgent' instead of 'NoneType'
- [ ] Fix Python typing inconsistencies across backend
- [ ] Fix async function misuse patterns
- [ ] Reduce cognitive complexity in backend functions
- [ ] Fix regex duplications

### 2. sonar-frontend-fixes (/home/omar/Documents/ruleIQ.worktrees/sonar-frontend)
**Priority: HIGH - TypeScript Issues**
- [ ] Fix frontend/app/api/pusher/auth/route.ts - Remove unused variables
- [ ] Fix frontend/app/api/pusher/trigger/route.ts - Remove unused variables
- [ ] Fix complexity issues in React components
- [ ] Remove all unused imports
- [ ] Fix nested ternary operations
- [ ] Remove unnecessary type assertions

### 3. sonar-security-fixes (/home/omar/Documents/ruleIQ.worktrees/sonar-security)
**Priority: CRITICAL - Security Hotspots**
- [ ] Review and fix all security hotspots
- [ ] Fix any SQL injection vulnerabilities
- [ ] Fix XSS vulnerabilities
- [ ] Review authentication/authorization issues
- [ ] Fix sensitive data exposure

### 4. debug-channel-2 (/home/omar/Documents/ruleIQ.worktrees/Claude-2)
**Priority: MEDIUM - Code Smells (Part 1)**
- [ ] Fix first 10 code smell issues
- [ ] Focus on duplicated code blocks
- [ ] Fix import organization issues
- [ ] Remove dead code

### 5. debug-channel-3 (/home/omar/Documents/ruleIQ.worktrees/Claude-3)
**Priority: MEDIUM - Code Smells (Part 2)**
- [ ] Fix next 10 code smell issues
- [ ] Focus on function complexity
- [ ] Fix naming conventions
- [ ] Improve error handling patterns

### 6. debug-channel-4 (/home/omar/Documents/ruleIQ.worktrees/Claude-4)
**Priority: LOW - Minor Issues**
- [ ] Fix remaining code smells
- [ ] Documentation improvements
- [ ] Code formatting consistency
- [ ] Test coverage improvements

## Execution Commands

Each Claude instance should run these commands in their respective worktree:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Run SonarCloud analysis for your branch
doppler run -- sonar-scanner -Dsonar.branch.name=<branch-name>

# 3. Fix assigned issues

# 4. Run tests
npm test # for frontend
python -m pytest # for backend

# 5. Commit changes
git add -A
git commit -m "fix: SonarCloud issues for <category>"

# 6. Push to origin
git push origin <branch-name>
```

## Merge Strategy

1. Complete all fixes in parallel
2. Run SonarCloud analysis on each branch
3. Merge in this order:
   - sonar-security-fixes → main (FIRST - Critical)
   - sonar-backend-fixes → main
   - sonar-frontend-fixes → main
   - debug-channel-2 → main
   - debug-channel-3 → main
   - debug-channel-4 → main

## Success Criteria

- Zero Critical issues
- Zero Major bugs
- Reduce Code Smells by 80%
- All tests passing
- SonarCloud Quality Gate: Passed