# RuleIQ Minimal Context

## Critical Workflow
1. Check Archon tasks: `mcp__archon__list_tasks`
2. Research: `mcp__archon__perform_rag_query`
3. Code with Serena: `mcp__serena__find_symbol`
4. Test: `make test-fast` or `pnpm test`
5. Update task: `mcp__archon__manage_task`

## Essential Commands
```bash
# Backend
source .venv/bin/activate
doppler run -- python main.py
make test-fast
ruff check . && ruff format .

# Frontend
cd frontend
pnpm dev --turbo
pnpm test && pnpm lint && pnpm typecheck
```

## Key Locations
- API: `api/routers/*.py`
- Services: `services/*.py`
- Frontend: `frontend/app/(dashboard)/`
- Components: `frontend/components/ui/`

## Critical Patterns
- Field mappers for DB truncation
- Circuit breaker for AI services
- JWT + AES-GCM + RBAC auth
- Rate limits: 100/min general, 20/min AI

## Status
- 98% Production Ready
- 671+ Tests Passing
- <200ms API Response