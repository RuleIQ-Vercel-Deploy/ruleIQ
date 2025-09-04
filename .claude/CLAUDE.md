# RuleIQ Project Rules

## ⛔ CRITICAL SAFETY RULES - NEVER VIOLATE

### DESTRUCTIVE ACTIONS REQUIRING EXPLICIT APPROVAL
1. **NO mass refactoring** without explicit permission
2. **NO bulk file modifications** (>5 files requires approval)
3. **NO automated "fix-all" scripts** without approval
4. **NO structural changes** (moving code between files) without approval
5. **ALWAYS test** after EACH file modification
6. **ALWAYS create backups** before changes

### REFACTORING SAFEGUARDS
- See `.claude/REFACTORING_SAFEGUARDS.md` for detailed rules
- Use `.claude/refactoring-guard.py` before any refactoring
- One file at a time, test after each change
- Stop immediately if syntax errors occur

## Mission
Execute 49 prioritized tasks (P0-P7) for the RuleIQ compliance automation platform with strict quality gates and timeframe enforcement.

## Priority Gates (STRICTLY ENFORCED)
- **P0 Must Complete Before P1**: No P1 work until ALL P0 tasks pass
- **Sequential Gating**: Each priority level blocks the next
- **No Exceptions**: Even if resources available, respect gates

## Timeframes (ENFORCE STRICTLY)
- **P0**: 24 hours max per task, escalate at 12 hours
- **P1**: 48 hours max per task, escalate at 36 hours
- **P2**: 1 week max per task, escalate at 5 days
- **P3-P7**: Per roadmap schedule

## Task Merges (APPLY IMMEDIATELY)
- d10c4062 → c81e1108 (GitHub Actions duplicate)
- d3d23042 → 2f2f8b57 (Dead code elimination duplicate)

## Quality Standards
- Every task must pass acceptance criteria
- No regressions on completed work
- Tests must pass before marking complete
- Documentation updated with changes

## Communication Protocol
- Update task state immediately on status change
- Log all decisions and blockers
- Escalate proactively, not reactively
- Daily status reports required

## Available Agents
- orchestrator: Master coordinator
- backend-specialist: Python/FastAPI/DB
- qa-specialist: Testing and coverage
- security-auditor: Vulnerabilities
- frontend-specialist: React/Next.js
- infrastructure: Docker/CI/CD
- documentation: Docs and guides
- compliance-uk: UK regulations
- graphrag-specialist: AI/Knowledge graphs