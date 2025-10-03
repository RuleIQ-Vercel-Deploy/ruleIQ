# Large File Refactoring - Implementation Guide

## Overview

This guide provides step-by-step instructions for completing the large file refactoring initiative. The baseline metrics have been established and directory structures created. This document details how to extract specific functions into the new modular structure.

**Refactoring Status:** 🔄 In Progress

## Quick Reference

| File | Status | Modules | Complexity |
|------|--------|---------|------------|
| chat.py | 🔄 Structure Created | 6 routers | High |
| langgraph_metrics.py | ⏳ Pending | 8 modules | Medium |
| export.ts | ⏳ Pending | 7 modules | High |
| freemium-store.ts | ⏳ Pending | 8 slices | Medium |

## Phase 1: Chat Router Refactoring (CURRENT)

### Directory Structure Created ✅

```
api/routers/chat/
├── __init__.py          # Aggregator (CREATED)
├── conversations.py     # TO CREATE
├── messages.py          # TO CREATE
├── evidence.py          # TO CREATE
├── analytics.py         # TO CREATE
├── iq_agent.py          # TO CREATE
└── placeholder_endpoints.py  # TO CREATE
```

### Step-by-Step Extraction

#### 1. Extract Conversations Router

**Source:** `api/routers/chat.py` lines 48-481

**Target:** `api/routers/chat/conversations.py`

**Endpoints to Extract:**
```python
# Line 48-244: POST /conversations
@router.post("/conversations", response_model=dict, dependencies=[Depends(validate_request)])
async def create_conversation(...)

# Line 246-312: GET /conversations
@router.get("/conversations", response_model=ConversationListResponse, ...)
async def list_conversations(...)

# Line 314-355: GET /conversations/{conversation_id}
@router.get("/conversations/{conversation_id}", response_model=ConversationResponse, ...)
async def get_conversation(...)

# Line 451-481: DELETE /conversations/{conversation_id}
@router.delete("/conversations/{conversation_id}", ...)
async def delete_conversation(...)
```

**Required Imports:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.auth import get_current_active_user
from api.dependencies.security_validation import validate_request
from api.utils.security_validation import SecurityValidator
from database.user import User
from database.business_profile import BusinessProfile
from database.chat_conversation import ChatConversation, ConversationStatus
from database.chat_message import ChatMessage
from database.db_setup import get_async_db
from api.schemas.chat import (
    ConversationListResponse,
    ConversationResponse,
    ConversationSummary,
    CreateConversationRequest,
)
from services.ai import ComplianceAssistant
```

**Template:**
```python
\"\"\"
Chat Conversations Router

Handles conversation CRUD operations:
- Create new conversation
- List user conversations
- Get conversation details
- Delete conversation

Extracted from api/routers/chat.py (lines 48-481)
\"\"\"

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat - Conversations"])

# TODO: Extract 4 endpoint functions from original chat.py

__all__ = ['router']
```

#### 2. Extract Messages Router

**Source:** `api/routers/chat.py` lines 358-449

**Target:** `api/routers/chat/messages.py`

**Endpoints:**
- Line 358-449: `POST /conversations/{conversation_id}/messages`

#### 3. Extract Evidence Router

**Source:** `api/routers/chat.py` lines 484-1222

**Target:** `api/routers/chat/evidence.py`

**Endpoints:** 10 evidence-related endpoints (see baseline metrics for details)

#### 4. Extract Analytics Router

**Source:** `api/routers/chat.py` lines 782-1381

**Target:** `api/routers/chat/analytics.py`

**Endpoints:** 9 analytics/monitoring endpoints

#### 5. Extract IQ Agent Router

**Source:** `api/routers/chat.py` lines 1383-1606

**Target:** `api/routers/chat/iq_agent.py`

**Endpoints:**
- Global IQ Agent initialization
- POST /iq/message
- GET /iq/status

#### 6. Update Aggregator

**File:** `api/routers/chat/__init__.py`

After all routers are extracted, uncomment the import statements in `__init__.py`:

```python
from .conversations import router as conversations_router
from .messages import router as messages_router
from .evidence import router as evidence_router
from .analytics import router as analytics_router
from .iq_agent import router as iq_agent_router
from .placeholder_endpoints import router as placeholder_router

# Include all sub-routers
router.include_router(conversations_router)
router.include_router(messages_router)
router.include_router(evidence_router)
router.include_router(analytics_router)
router.include_router(iq_agent_router)
router.include_router(placeholder_router)
```

#### 7. Rename Original File

```bash
mv api/routers/chat.py api/routers/chat_legacy.py
```

Add deprecation notice at top of `chat_legacy.py`:
```python
\"\"\"
⚠️ LEGACY FILE - DO NOT USE DIRECTLY

This file has been refactored into focused domain modules in api/routers/chat/
Preserved for reference only.

Date: 2025-10-01
Refactoring Ticket: Phase 4 - Large File Refactoring
\"\"\"
```

## Phase 2: LangGraph Metrics Refactoring

### Directory Structure Created ✅

```
app/core/monitoring/trackers/
├── __init__.py              # Aggregator
├── types.py                 # Shared enums/dataclasses
├── node_tracker.py          # NodeExecutionTracker
├── workflow_tracker.py      # WorkflowMetricsTracker
├── state_tracker.py         # StateTransitionTracker
├── checkpoint_tracker.py    # CheckpointMetrics
├── memory_tracker.py        # MemoryUsageTracker
├── error_tracker.py         # ErrorMetricsCollector
└── performance_analyzer.py  # PerformanceAnalyzer
```

### Extraction Steps

#### 1. Extract Shared Types

**Source:** `app/core/monitoring/langgraph_metrics.py` lines 17-57

**Target:** `app/core/monitoring/types.py`

**Content:**
- NodeStatus enum (lines 17-26)
- WorkflowStatus enum (lines 27-33)
- NodeExecution dataclass (lines 35-45)
- WorkflowExecution dataclass (lines 47-57)

#### 2. Extract Individual Trackers

| Tracker | Source Lines | Target File |
|---------|--------------|-------------|
| NodeExecutionTracker | 58-357 | node_tracker.py |
| WorkflowMetricsTracker | 358-710 | workflow_tracker.py |
| StateTransitionTracker | 711-935 | state_tracker.py |
| CheckpointMetrics | 984-1246 | checkpoint_tracker.py |
| MemoryUsageTracker | 1247-1508 | memory_tracker.py |
| ErrorMetricsCollector | 1509-1673 | error_tracker.py |
| PerformanceAnalyzer | 1674-1764 | performance_analyzer.py |

#### 3. Update Main File

**File:** `app/core/monitoring/langgraph_metrics.py`

- Remove all class definitions (lines 17-1764)
- Keep only `LangGraphMetricsCollector` (lines 1765-1897)
- Import from new modules:

```python
from .types import NodeStatus, WorkflowStatus, NodeExecution, WorkflowExecution
from .trackers import (
    NodeExecutionTracker,
    WorkflowMetricsTracker,
    StateTransitionTracker,
    CheckpointMetrics,
    MemoryUsageTracker,
    ErrorMetricsCollector,
    PerformanceAnalyzer
)
```

## Phase 3: Export Utils Refactoring

### Directory Structure Created ✅

```
frontend/lib/utils/export/
├── index.ts            # Main router/aggregator
├── types.ts            # Shared types
├── constants.ts        # Theme colors
├── utils.ts            # Shared utilities
├── excel-exporter.ts   # XLSX export
├── pdf-exporter.ts     # PDF export
└── csv-exporter.ts     # CSV export
```

### Extraction Steps

#### 1. Extract Types

**Source:** `frontend/lib/utils/export.ts` lines 1-265
**Target:** `frontend/lib/utils/export/types.ts`

#### 2. Extract Constants

**Source:** Lines 14-35
**Target:** `frontend/lib/utils/export/constants.ts`

#### 3. Extract Utilities

**Source:** Lines 46-1487 (various utility functions)
**Target:** `frontend/lib/utils/export/utils.ts`

#### 4. Extract Exporters

| Exporter | Source Lines | Target File |
|----------|--------------|-------------|
| Excel | 336-549 | excel-exporter.ts |
| PDF | 551-998 | pdf-exporter.ts |
| CSV | 1000-1216 | csv-exporter.ts |

#### 5. Create Main Router

**Target:** `frontend/lib/utils/export/index.ts`

**Source:** Lines 1218-1505 (main router function)

## Phase 4: Freemium Store Refactoring

### Directory Structure Created ✅

```
frontend/lib/stores/freemium/
├── index.ts            # Store composition
├── types.ts            # Shared types
├── lead-slice.ts       # Lead management
├── session-slice.ts    # Session lifecycle
├── question-slice.ts   # Question flow
├── results-slice.ts    # Results generation
├── progress-slice.ts   # Progress tracking
├── consent-slice.ts    # Consent management
└── analytics-slice.ts  # Analytics/events
```

### Extraction Pattern (Zustand Slices)

Each slice follows this pattern:

```typescript
import { StateCreator } from 'zustand';

export interface XSliceState {
  // State properties
}

export interface XSliceActions {
  // Action methods
}

export const createXSlice: StateCreator<
  XSliceState & XSliceActions,
  [],
  [],
  XSliceState & XSliceActions
> = (set, get) => ({
  // Initial state

  // Actions
});

export type XSlice = XSliceState & XSliceActions;
```

### Slice Extraction Map

| Slice | Source Lines | State Lines | Action Lines |
|-------|--------------|-------------|--------------|
| Lead | 153-189 | 63-67 | 153-189 |
| Session | 200-318 | 69-73 | 200-318 |
| Question | 321-391 | 76-89 | 321-391 |
| Results | TBD | TBD | TBD |
| Progress | TBD | TBD | TBD |
| Consent | TBD | TBD | TBD |
| Analytics | TBD | TBD | TBD |

## Testing Strategy

### Backend Tests

```bash
# Test individual routers
pytest tests/api/routers/chat/test_conversations.py -v

# Test aggregator maintains compatibility
pytest tests/api/routers/test_chat_integration.py -v

# Test metrics trackers
pytest tests/monitoring/test_langgraph_metrics.py -v
```

### Frontend Tests

```bash
cd frontend

# Test export modules
pnpm test lib/utils/export --coverage

# Test freemium store
pnpm test lib/stores/freemium --coverage
```

### Integration Testing

After each module extraction:

1. ✅ Run linters: `ruff check .` or `pnpm lint`
2. ✅ Run type checks: `mypy .` or `pnpm typecheck`
3. ✅ Run unit tests for the module
4. ✅ Run integration tests
5. ✅ Verify imports work from aggregator

## Validation Checklist

### Per Module
- [ ] Function extracted with all logic intact
- [ ] All imports present and correct
- [ ] Docstrings and comments preserved
- [ ] Module <500 lines
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Unit tests pass

### Per File Refactoring
- [ ] All modules created
- [ ] Aggregator includes all modules
- [ ] Original file renamed to *_legacy
- [ ] Deprecation notice added
- [ ] All tests pass
- [ ] No import errors in codebase
- [ ] Performance benchmarks pass

### Overall Project
- [ ] All 4 files refactored
- [ ] 88% LOC reduction achieved
- [ ] Test coverage maintained/improved
- [ ] Documentation complete
- [ ] Team trained on new structure
- [ ] Production deployment successful
- [ ] 2-week monitoring period complete
- [ ] Legacy files deleted

## Rollback Procedure

If issues arise:

1. **Immediate Rollback:**
   ```bash
   # Backend
   mv api/routers/chat_legacy.py api/routers/chat.py
   rm -rf api/routers/chat/

   # Metrics
   git checkout app/core/monitoring/langgraph_metrics.py
   rm -rf app/core/monitoring/trackers/
   ```

2. **Partial Rollback:**
   - Keep new modules
   - Temporarily use legacy file in main imports
   - Fix issues in new modules
   - Switch back when ready

3. **Debug Issues:**
   - Check aggregator includes all routers
   - Verify import paths are correct
   - Ensure no circular dependencies
   - Check for missing dependencies

## Performance Monitoring

### Metrics to Track

1. **Response Times:**
   - P50, P95, P99 latency
   - Compare pre/post refactoring

2. **Bundle Size (Frontend):**
   ```bash
   cd frontend
   pnpm build
   npx bundlesize
   ```

3. **Test Execution Time:**
   ```bash
   pytest --durations=10
   ```

4. **Memory Usage:**
   - Monitor application memory
   - Check for leaks in new modules

## Common Issues & Solutions

### Issue: Circular Import

**Symptom:** `ImportError: cannot import name 'X' from partially initialized module`

**Solution:**
- Move shared types to separate `types.py`
- Use TYPE_CHECKING imports
- Restructure dependencies

### Issue: Missing Dependencies

**Symptom:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
- Check all imports copied from original
- Verify relative import paths
- Ensure __init__.py exports correctly

### Issue: Tests Failing

**Symptom:** Tests pass on legacy file but fail on new modules

**Solution:**
- Update test imports
- Check mock paths
- Verify fixtures work with new structure

## Timeline & Resources

### Estimated Timeline

| Phase | Estimated Time | Complexity |
|-------|---------------|------------|
| Chat Router | 4-6 hours | High |
| Metrics Trackers | 3-4 hours | Medium |
| Export Utils | 4-5 hours | High |
| Freemium Store | 3-4 hours | Medium |
| Testing & Validation | 4-6 hours | High |
| **Total** | **18-25 hours** | - |

### Resources Needed

- Senior developer for extraction
- QA engineer for testing
- DevOps for deployment monitoring
- Technical writer for documentation updates

## Success Criteria

✅ **88% LOC reduction** achieved (6,270 → ~750 lines)
✅ **All modules <500 lines**
✅ **Test coverage maintained** (no reduction)
✅ **Zero breaking changes** (backward compatible)
✅ **Performance neutral** (no regressions)
✅ **Team trained** on new structure

## Next Steps

1. **Complete Chat Router** (Phase 1 - Current)
   - Extract conversations.py
   - Extract messages.py
   - Extract evidence.py
   - Extract analytics.py
   - Extract iq_agent.py
   - Extract placeholder_endpoints.py
   - Update aggregator
   - Rename original file
   - Run tests

2. **Move to Metrics** (Phase 2)
3. **Refactor Export** (Phase 3)
4. **Refactor Store** (Phase 4)
5. **Final validation**
6. **Production deployment**
7. **Delete legacy files** (after 2 weeks)

## Questions or Issues?

Contact the development team lead or create a ticket in the project management system.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-01
**Status:** Active Implementation Guide
**Owner:** Development Team
