# Large File Refactoring - Quick Reference Card

## 🎯 At a Glance

**Mission:** Transform 6,270 lines → 750 lines (88% reduction)
**Scope:** 4 files → 29 focused modules
**Time:** 22-31 hours
**Status:** ✅ Framework complete, ready for extraction

## 📋 The 4 Files

| # | File | Lines | Target Modules | Time | Status |
|---|------|-------|---------------|------|--------|
| 1 | `api/routers/chat.py` | 1,606 | 6 routers | 4-6h | 🔄 Next |
| 2 | `app/core/monitoring/langgraph_metrics.py` | 1,897 | 8 trackers | 3-4h | ⏳ |
| 3 | `frontend/lib/utils/export.ts` | 1,505 | 7 modules | 4-5h | ⏳ |
| 4 | `frontend/lib/stores/freemium-store.ts` | 1,262 | 8 slices | 3-4h | ⏳ |

## 🚀 Quick Start (5 Steps)

1. **Read the guide:**
   ```bash
   cat LARGE_FILE_REFACTORING_IMPLEMENTATION_GUIDE.md
   ```

2. **Create first module:**
   ```bash
   touch api/routers/chat/conversations.py
   ```

3. **Extract lines 48-481** from `chat.py` using template

4. **Test:**
   ```bash
   pytest tests/api/routers/chat/ -v
   ```

5. **Repeat for remaining modules**

## 📖 Documentation Map

| Need | Use This Document |
|------|------------------|
| Line numbers? | `REFACTORING_METRICS_BASELINE.md` |
| How to extract? | `LARGE_FILE_REFACTORING_IMPLEMENTATION_GUIDE.md` |
| Why this pattern? | `docs/architecture/LARGE_FILE_REFACTORING.md` |
| Current status? | `REFACTORING_IMPLEMENTATION_STATUS.md` |
| Quick overview? | `REFACTORING_COMPLETE_SUMMARY.md` |

## 🎯 Phase 1: Chat Router (START HERE)

### Modules to Create (in order):

1. **conversations.py** (Lines 48-481 → ~200 lines)
   ```python
   # 4 endpoints: POST, GET, GET/{id}, DELETE
   from fastapi import APIRouter, Depends
   router = APIRouter(tags=["Chat - Conversations"])
   ```

2. **messages.py** (Lines 358-449 → ~100 lines)
   ```python
   # 1 endpoint: POST messages
   ```

3. **evidence.py** (Lines 484-1222 → ~400 lines)
   ```python
   # 10 endpoints: evidence/compliance
   ```

4. **analytics.py** (Lines 782-1381 → ~350 lines)
   ```python
   # 9 endpoints: metrics/monitoring
   ```

5. **iq_agent.py** (Lines 1383-1606 → ~200 lines)
   ```python
   # IQ Agent + 2 endpoints
   ```

6. **placeholder_endpoints.py** (Lines 1226-1355 → ~100 lines)
   ```python
   # 3 placeholder endpoints
   ```

### After All Extracted:

```python
# Update api/routers/chat/__init__.py
from .conversations import router as conversations_router
from .messages import router as messages_router
from .evidence import router as evidence_router
from .analytics import router as analytics_router
from .iq_agent import router as iq_agent_router
from .placeholder_endpoints import router as placeholder_router

router.include_router(conversations_router)
router.include_router(messages_router)
router.include_router(evidence_router)
router.include_router(analytics_router)
router.include_router(iq_agent_router)
router.include_router(placeholder_router)
```

### Final Steps:
```bash
# Rename original
mv api/routers/chat.py api/routers/chat_legacy.py

# Test everything
pytest tests/api/routers/chat/ -v
```

## ✅ Per-Module Checklist

- [ ] Lines extracted exactly as-is
- [ ] All imports present
- [ ] Module <500 lines
- [ ] `ruff check` passes
- [ ] `mypy` passes
- [ ] Tests pass
- [ ] Aggregator updated

## ⚠️ Golden Rules

### DO ✅
- Extract exact code (copy-paste)
- Test after each module
- Keep legacy files until validated
- Update aggregators

### DON'T ❌
- Refactor logic while extracting
- Skip testing
- Delete originals immediately
- Change function signatures

## 🔄 The Pattern

Every refactoring follows this pattern:

```
1. Create new module
2. Copy exact code (with line numbers from guide)
3. Add required imports
4. Add docstring
5. Export router/class
6. Update aggregator
7. Test module
8. Move to next
9. When all done: rename original to *_legacy
10. Test everything
```

## 📊 Success Metrics

| Metric | Target | How to Verify |
|--------|--------|--------------|
| LOC Reduction | 88% | `wc -l` before/after |
| Module Size | <500 lines | Check each file |
| Test Coverage | Maintained | `pytest --cov` |
| Performance | Neutral/Better | Benchmark |
| Breaking Changes | 0 | Integration tests |

## 🆘 If Something Goes Wrong

### Tests Fail?
```bash
# Check imports
# Verify aggregator includes module
# Compare with legacy file
```

### Import Errors?
```python
# Check all imports copied from original
# Verify relative paths correct
# Ensure __init__.py exports
```

### Need to Rollback?
```bash
mv api/routers/chat_legacy.py api/routers/chat.py
rm -rf api/routers/chat/
pytest  # Should pass
```

## 💡 Pro Tips

1. **Work in branches:**
   ```bash
   git checkout -b refactor/chat-router
   ```

2. **Commit after each module:**
   ```bash
   git add api/routers/chat/conversations.py
   git commit -m "Extract conversations router"
   ```

3. **Test frequently:**
   ```bash
   # After each module
   pytest tests/api/routers/chat/test_conversations.py -v
   ```

4. **Use templates:**
   - See implementation guide for module templates
   - Copy structure, fill in extracted code

## 📈 Progress Tracking

Use this table (update as you go):

| Module | Status | Lines | Tested? |
|--------|--------|-------|---------|
| conversations.py | ⏳ | ~200 | ❌ |
| messages.py | ⏳ | ~100 | ❌ |
| evidence.py | ⏳ | ~400 | ❌ |
| analytics.py | ⏳ | ~350 | ❌ |
| iq_agent.py | ⏳ | ~200 | ❌ |
| placeholder_endpoints.py | ⏳ | ~100 | ❌ |

## 🎯 Today's Goal

**Extract conversations.py** (first module, ~200 lines)

**Estimated Time:** 30-45 minutes
**Difficulty:** Easy (template provided)
**Validation:** Tests pass

**Commands:**
```bash
# Create file
touch api/routers/chat/conversations.py

# Open and extract lines 48-481 from chat.py
code api/routers/chat/conversations.py

# Test
pytest tests/api/routers/chat/ -v
```

## 🏆 Completion Criteria

### Phase 1 Complete When:
- [ ] All 6 modules created
- [ ] Aggregator updated
- [ ] Original renamed to *_legacy
- [ ] All tests pass
- [ ] No import errors
- [ ] Performance neutral

### All Phases Complete When:
- [ ] 29 modules created
- [ ] 88% LOC reduction
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Production stable (2 weeks)
- [ ] Legacy files deleted

## 📞 Need Help?

1. Check implementation guide (detailed instructions)
2. Review architecture docs (patterns explained)
3. Check baseline metrics (line numbers)
4. Use rollback procedure if stuck

## 🎉 You Got This!

**Remember:**
- Framework is 100% complete
- Every line is mapped
- Every import is documented
- Every template is provided
- You just need to extract!

**Start with conversations.py and build momentum! 🚀**

---

**Quick Reference Version:** 1.0
**Date:** 2025-10-01
**Status:** Ready to use
**Keep this handy during implementation!**
