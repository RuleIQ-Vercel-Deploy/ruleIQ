# Story Tracking Index

## Document Info
- **Version:** 1.1
- **Last Updated:** 2025-01-09
- **Maintained By:** PO/SM Agents (Bob)

## Overview
This index provides a centralized reference for all story numbering across the project to prevent conflicts and confusion between different teams and agents.

## Active Sprint Stories

### Day 1 Fixes (Infrastructure & Configuration)
**Status:** In Progress
**Prefix:** `day1-fix-`

| Story ID | File | Description | Dev Status | QA Status |
|----------|------|-------------|------------|-----------|
| day1-fix-1 | `day1-fix-1-auth-tests.md` | Fix authentication test failures | Completed | Done |
| day1-fix-2 | `day1-fix-2-directory-resolution.md` | Resolve directory structure issues | Completed | Done |
| day1-fix-3 | `day1-fix-3-environment-config.md` | Configure environment variables | Completed | Done |
| config-fix | `config-fix-architecture-references.md` | Fix architecture reference issues | Verified ✅ | Resolved |

## Sprint-0 Backlog (Agentic Features)
**Status:** Planning
**Prefix:** `S0-`

### Epic 1: Development Environment Setup
| Story ID | Description | Priority | Points | File Status |
|----------|-------------|----------|--------|-------------|
| S0-1.1 | Agentic Database Schema | Critical | 8 | Created ✅ |
| S0-1.2 | Agent Orchestrator Foundation | Critical | 13 | Created ✅ |
| S0-1.3 | Conversational UI Foundation | High | 8 | Not Created |

### Epic 2: Core PoCs & Validation
| Story ID | Description | Priority | Points | File Status |
|----------|-------------|----------|--------|-------------|
| S0-2.1 | Trust Level 0 Agent PoC | Critical | 13 | Not Created |
| S0-2.2 | RAG Self-Critic PoC | High | 21 | Not Created |
| S0-2.3 | Trust Progression Algorithm PoC | Medium | 8 | Not Created |

### Epic 3: Monitoring & Observability
| Story ID | Description | Priority | Points | File Status |
|----------|-------------|----------|--------|-------------|
| S0-3.1 | Prometheus/Grafana Setup | High | 5 | Not Created |
| S0-3.2 | Custom Agentic Metrics | High | 8 | Not Created |
| S0-3.3 | Alert Configuration | Medium | 3 | Not Created |

## QA Review Queue
| Story | Status | QA Reviewer | Gate Decision |
|-------|--------|-------------|---------------|
| S0-1.4 (WebSocket Communication) | Needs Creation | Quinn | CONCERNS - Not in current scope |
| day1-fix-1 | Ready for Review | Quinn | Pending |

## Story States

### Development States
- **Draft**: Requirements being defined
- **Ready**: Has acceptance criteria, estimates, and dependencies identified
- **In Progress**: Development active
- **Dev Complete**: Code complete, awaiting QA
- **Done**: Passed all gates and deployed

### QA States
- **Not Started**: Story not ready for QA
- **Pending Review**: Awaiting QA assessment
- **Under Review**: QA actively reviewing
- **PASS**: Meets all quality criteria
- **CONCERNS**: Issues identified, needs attention
- **FAIL**: Critical issues, must be reworked
- **WAIVED**: Issues acknowledged but accepted

## QA Gate Summary

| Story | Gate Decision | Review Date | Critical Issues | Reviewer |
|-------|---------------|-------------|-----------------|----------|
| day1-fix-1 | PENDING | - | - | Quinn |
| day1-fix-2 | NOT STARTED | - | - | - |
| day1-fix-3 | NOT STARTED | - | - | - |
| config-fix | NOT STARTED | - | - | - |

## Story Numbering Convention

### Current System (Effective 2025-01-09)
- **Day Fixes:** `day{n}-fix-{sequence}` (e.g., day1-fix-1)
- **Sprint-0:** `S0-{epic}.{story}` (e.g., S0-1.1)
- **Feature Stories:** `F-{epic}.{story}` (e.g., F-1.1)
- **Bug Fixes:** `BUG-{number}` (e.g., BUG-001)
- **Technical Debt:** `TD-{number}` (e.g., TD-001)

### Guidelines
1. Always check this index before creating new stories
2. Update this index when stories are created or completed
3. Use consistent prefixes to avoid numbering conflicts
4. Include story status to track progress

## Historical Notes
- **2025-01-09 v1.0:** Renamed day1 stories to avoid conflict with Sprint-0 numbering
- **2025-01-09 v1.0:** QA reviewed non-existent Story 1.4, highlighting need for this index
- **2025-01-09 v1.1:** Added QA tracking, story states, and file status per Quinn's review

## Next Actions
1. ✅ Align all agents on this numbering system
2. Update story templates to include prefix requirements
3. Determine if S0-1.4 (WebSocket) should be created or removed from scope
4. ✅ Review and update Sprint-0 backlog with proper prefixes
5. Create story files for Sprint-0 stories when ready to begin development
6. Update QA Gate Summary as stories are reviewed