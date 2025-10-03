# AI Refactor - Granular Implementation Plan

**Date:** September 30, 2025
**Status:** Phase 1 - Workflow Complete, Evidence In Progress
**Approach:** Small, testable increments with validation at each step

---

## Guiding Principles

1. **One Thing at a Time** - Never change multiple files simultaneously
2. **Test Before Moving Forward** - Verify imports and instantiation after each change
3. **Backup First** - Keep old versions safe
4. **Small Methods** - Port one method at a time, not entire classes
5. **Validate Continuously** - Run verification after each step

---

## Phase 1: WorkflowService ✅ COMPLETE

### Status: COMPLETE
- ✅ Lines of code: 534 (was 65 placeholder)
- ✅ Imports successfully
- ✅ Instantiates without errors
- ✅ Full AI integration with:
  - Maturity analysis
  - Prompt building
  - Response parsing
  - Automation enhancement
  - Effort calculation

---

## Phase 2: EvidenceService (CURRENT)

### Step 2.1: Analysis ⏳ IN PROGRESS
**Task:** Understand what needs to be ported
**Estimated Time:** 15 minutes

**Substeps:**
1. ✅ Read lines 590-620 of legacy code (just to understand)
2. ⏳ List all methods in legacy evidence recommendations
3. ⏳ Identify dependencies (what other methods are called)
4. ⏳ Document in simple bullet points

**DO NOT CODE YET** - Just document

---

### Step 2.2: Backup & Prepare
**Task:** Safety first
**Estimated Time:** 5 minutes

**Substeps:**
1. Copy current `evidence_service.py` to `evidence_service.py.backup`
2. Verify backup exists
3. Document current line count (baseline)

---

### Step 2.3: Port First Method Only
**Task:** Get ONE method working
**Estimated Time:** 30 minutes

**Method to Port:** `get_recommendations()` (the main public method)

**Substeps:**
1. Copy method signature from legacy
2. Copy docstring
3. Copy first 10 lines of implementation
4. Test - does it import?
5. Copy next 10 lines
6. Test - does it import?
7. Continue in 10-line increments
8. Add any helper methods needed (one at a time)

**Success Criteria:**
- ✅ File imports without errors
- ✅ Service instantiates
- ✅ Method exists and has correct signature
- ✅ No syntax errors

**DO NOT:** Port other methods yet - just this one

---

### Step 2.4: Validate Evidence Service
**Task:** Make sure nothing broke
**Estimated Time:** 10 minutes

**Tests:**
```bash
# 1. Import test
python -c "from services.ai.domains.evidence_service import EvidenceService"

# 2. Instantiation test
python -c "from services.ai.domains.evidence_service import EvidenceService;
from unittest.mock import Mock;
s = EvidenceService(Mock(), Mock(), Mock(), Mock())"

# 3. Method exists test
python -c "from services.ai.domains.evidence_service import EvidenceService;
print(hasattr(EvidenceService, 'get_recommendations'))"
```

**Success Criteria:**
- All three tests pass
- No import errors
- No instantiation errors

---

### Step 2.5: Review & Decide
**Task:** Assess progress
**Estimated Time:** 10 minutes

**Questions to Answer:**
1. Did the port go smoothly?
2. Are there any issues?
3. Should we continue with more methods?
4. Or should we fix issues first?

**STOP HERE** - Get user approval before continuing

---

## Phase 3: ComplianceAnalysisService (FUTURE)

### Step 3.1: Analysis (NOT STARTED)
Same granular approach as Phase 2

### Step 3.2-3.5: (NOT STARTED)
Will break down when we reach this phase

---

## Phase 4: AssessmentService Enhancement (FUTURE)

Currently has 181 lines with basic implementation.
Need to enhance with full prompt logic.

**Will break down when we reach this phase.**

---

## Phase 5: Integration Testing (FUTURE)

### Step 5.1: Update Benchmark Script
Add one functional test at a time

### Step 5.2: Run Parity Tests
Verify new implementations match legacy behavior

### Step 5.3: Performance Check
Ensure no major slowdowns

---

## Phase 6: Documentation Update (FUTURE)

### Step 6.1: Update Migration Guide
Document what was ported

### Step 6.2: Update Implementation Summary
Mark completion status

---

## Current Status Summary

### Completed
- ✅ WorkflowService: Full implementation (534 lines)
- ✅ Verification: Imports and instantiation working

### In Progress
- ⏳ EvidenceService: Analysis phase
  - Next: Document legacy methods
  - Then: Port ONE method
  - Then: Test and validate

### Not Started
- ⏸️ ComplianceAnalysisService
- ⏸️ AssessmentService enhancements
- ⏸️ Integration testing
- ⏸️ Documentation updates

---

## Risk Mitigation

### What Could Go Wrong?

1. **Import Errors**
   - Mitigation: Test imports after every change
   - Rollback: Keep backup files

2. **Missing Dependencies**
   - Mitigation: Port helper methods incrementally
   - Rollback: Revert to backup

3. **Breaking Existing Code**
   - Mitigation: Run façade tests after each service
   - Rollback: Git can restore

4. **Scope Creep**
   - Mitigation: Stick to plan, one step at a time
   - Recovery: Stop, reassess, simplify

---

## Progress Tracking

Use this checklist to track granular progress:

**WorkflowService:**
- [x] Analysis complete
- [x] Backup created (legacy preserved)
- [x] Implementation complete
- [x] Import test passing
- [x] Instantiation test passing
- [x] Method signatures verified

**EvidenceService:**
- [ ] Analysis complete
- [ ] Methods documented
- [ ] Dependencies identified
- [ ] Backup created
- [ ] First method ported
- [ ] Import test passing
- [ ] Instantiation test passing
- [ ] User review/approval

**ComplianceAnalysisService:**
- [ ] (Not started)

**AssessmentService:**
- [ ] (Not started)

---

## Next Immediate Actions

1. ✅ Complete WorkflowService validation
2. ⏳ Read legacy evidence code (lines 590-620)
3. ⏳ Document evidence methods needed
4. ⏳ Create evidence service backup
5. Get user approval before porting code

---

## Estimated Time Remaining

- EvidenceService: ~2 hours (if we go method by method)
- ComplianceAnalysisService: ~1.5 hours
- AssessmentService enhancements: ~1 hour
- Testing & validation: ~1 hour
- Documentation: ~30 minutes

**Total remaining: ~6 hours** (broken into small increments)

---

## Success Criteria (Overall)

### Structural Parity ✅
- All modules import correctly
- All classes instantiate
- All public methods exist

### Functional Parity ⏳ IN PROGRESS
- WorkflowService: ✅ Complete with AI logic
- EvidenceService: ⏳ In progress
- ComplianceAnalysisService: ⏸️ Not started
- AssessmentService: ⏸️ Needs enhancement

### Test Coverage ✅
- Unit tests exist (62 tests created)
- Benchmarking script exists (32 parity tests)
- Integration tests exist

### Documentation ✅
- Migration guide exists
- Implementation summary exists
- This granular plan exists

---

**Last Updated:** 2025-09-30 20:45 UTC
**Current Phase:** 2 (EvidenceService)
**Current Step:** 2.1 (Analysis)
