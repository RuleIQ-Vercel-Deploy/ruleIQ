# Modular Routing Quick Reference

**Last Updated:** October 2, 2025
**Status:** ✅ ACTIVE

## Quick Facts

### Backend Chat Router
- **Façade:** `api/routers/chat.py` (18 lines)
- **Modular Impl:** `api/routers/chat/__init__.py` + 6 sub-modules
- **Reduction:** 1,606 lines → avg 267 lines per module
- **Imports:** All work via façade, no changes needed

### Frontend Freemium Store
- **Façade:** `frontend/lib/stores/freemium-store.ts` (38 lines)
- **Modular Impl:** `frontend/lib/stores/freemium/index.ts` + 8 slices
- **Reduction:** 1,263 lines → avg 158 lines per slice
- **Imports:** All work via façade, no changes needed

## Import Patterns

### Backend (Both work identically)
```python
# Via façade (current usage)
from api.routers import chat
from api.routers.chat import router

# Direct (recommended for new code)
from api.routers.chat import router
```

### Frontend (Both work identically)
```typescript
// Via façade (current usage)
import { useFreemiumStore } from '@/lib/stores/freemium-store';

// Direct (recommended for new code)
import { useFreemiumStore } from '@/lib/stores/freemium';
```

## Validation Commands

### Backend
```bash
# Import test
python -c "from api.routers.chat import router; print('✅ Works')"

# Full app test
source .venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Store tests
cd frontend && pnpm test freemium-store.test.ts --run

# Build test
cd frontend && pnpm build
```

## File Locations

### Chat Router Modules
```
api/routers/chat/
├── __init__.py          # Router aggregation
├── conversations.py     # CRUD operations
├── messages.py          # Message handling
├── evidence.py          # Evidence workflows
├── analytics.py         # Metrics & monitoring
├── iq_agent.py          # GraphRAG integration
└── placeholder_endpoints.py
```

### Freemium Store Slices
```
frontend/lib/stores/freemium/
├── index.ts            # Store composition
├── types.ts            # Type definitions
├── lead-slice.ts       # Lead management
├── session-slice.ts    # Session handling
├── question-slice.ts   # Question flow
├── results-slice.ts    # Results generation
├── progress-slice.ts   # Progress tracking
├── consent-slice.ts    # GDPR consent
├── analytics-slice.ts  # Event tracking
└── utility-slice.ts    # Utilities
```

## Common Issues & Solutions

### Issue: "Module not found" errors
**Solution:** Ensure you're in the correct directory and virtual environment is activated

### Issue: Circular import errors
**Solution:** Check that sub-modules don't import from parent package

### Issue: Tests fail with import errors
**Solution:** Update test fixtures to import from façade or package

### Issue: IDE shows incorrect type hints
**Solution:** Restart TypeScript/Python language server

## Rollback Instructions

### If you need to rollback:

**Backend:**
```bash
git checkout HEAD -- api/routers/chat.py
rm -rf api/routers/chat/
```

**Frontend:**
```bash
git checkout HEAD -- frontend/lib/stores/freemium-store.ts
rm -rf frontend/lib/stores/freemium/
```

## Related Documentation

- Full details: `/MODULAR_ROUTING_ACTIVATION.md`
- Architecture: `/docs/architecture/`
- Original issue: Comment #1 in verification review

## Key Benefits

1. **Better Organization:** Single-responsibility modules
2. **Easier Maintenance:** Find and fix issues faster
3. **Improved Testing:** Test individual slices
4. **Parallel Development:** Multiple devs, no conflicts
5. **Zero Risk:** Façade ensures backward compatibility

## Next Steps

- [ ] Optional: Update imports to use direct paths
- [ ] Optional: Add slice-specific tests
- [ ] Optional: Monitor bundle size improvements
- [ ] Optional: Update team documentation
