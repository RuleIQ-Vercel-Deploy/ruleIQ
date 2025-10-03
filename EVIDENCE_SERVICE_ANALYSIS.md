# EvidenceService - Symbolic Analysis

**Date:** 2025-09-30
**Source:** `services/ai/assistant_legacy.py` lines 590-900
**Target:** `services/ai/domains/evidence_service.py`

---

## Public Methods to Port

### Method 1: `get_evidence_recommendations()` (Lines 590-617)

**Signature:**
```python
async def get_evidence_recommendations(
    self,
    user: User,
    business_profile_id: UUID,
    target_framework: str
) -> List[Dict[str, Any]]
```

**What it does:**
- Gets business context from context_manager
- Builds prompt using prompt_templates
- Generates AI response
- Returns simple recommendation list

**Dependencies:**
- ✅ `self.context_manager.get_conversation_context()` - Have it
- ✅ `self.prompt_templates.get_evidence_recommendation_prompt()` - Have it
- ❓ `self._generate_gemini_response()` - Need to use `response_generator.generate_simple()`
- ✅ Exception handling - Can replicate

**Complexity:** ⭐ SIMPLE (28 lines)

---

### Method 2: `get_context_aware_recommendations()` (Lines 619-664)

**Signature:**
```python
async def get_context_aware_recommendations(
    self,
    user: User,
    business_profile_id: UUID,
    framework: str,
    context_type: str = 'comprehensive'
) -> Dict[str, Any]
```

**What it does:**
- Gets business context and existing evidence
- Analyzes compliance maturity
- Analyzes evidence gaps
- Generates contextual recommendations
- Prioritizes recommendations
- Generates next steps
- Calculates effort

**Dependencies:**
- ✅ `self.context_manager.get_conversation_context()` - Have it
- ⚠️ `self._analyze_compliance_maturity()` - Already in WorkflowService! Need to share
- ❓ `self.analyze_evidence_gap()` - Need to port (in ComplianceAnalysisService)
- ❓ `self._generate_contextual_recommendations()` - Need to port
- ❓ `self._prioritize_recommendations()` - Need to port
- ❓ `self._generate_next_steps()` - Need to port
- ❓ `self._calculate_total_effort()` - Need to port

**Complexity:** ⭐⭐⭐ COMPLEX (45 lines + 5 helper methods)

---

## Helper Methods Needed

### From Legacy Evidence Section (Lines 713-943)

1. **`_generate_contextual_recommendations()`** (Line 713)
   - Builds prompt
   - Generates AI response
   - Parses response
   - Adds automation insights
   - ~30 lines

2. **`_build_contextual_recommendation_prompt()`** (Line 740)
   - Prompt building
   - ~50 lines

3. **`_summarize_evidence_types()`** (Line 792)
   - Simple helper
   - ~10 lines

4. **`_parse_ai_recommendations()`** (Line 805)
   - JSON parsing
   - ~15 lines

5. **`_parse_text_recommendations()`** (Line 821)
   - Fallback text parsing
   - ~20 lines

6. **`_add_automation_insights()`** (Line 842)
   - Enhancement logic
   - ~20 lines

7. **`_get_automation_guidance()`** (Line 862)
   - Guidance generation
   - ~25 lines

8. **`_prioritize_recommendations()`** (Line 889)
   - Prioritization algorithm
   - ~35 lines

9. **`_generate_next_steps()`** (Line 925)
   - Next steps generation
   - ~15 lines

10. **`_calculate_total_effort()`** (Line 943)
    - Effort calculation
    - ~10 lines

---

## Methods from Other Services (Dependencies)

### From ComplianceAnalysisService

- `analyze_evidence_gap()` - Needed by get_context_aware_recommendations
  - **Status:** Currently in ComplianceAnalysisService
  - **Issue:** Need to port ComplianceAnalysisService first OR call it from there

### From WorkflowService (Already Ported!)

- `_analyze_compliance_maturity()` - Already ported to WorkflowService
  - **Status:** ✅ Complete in WorkflowService (lines 483-522)
  - **Solution Options:**
    1. Copy to EvidenceService (duplicate code)
    2. Create shared base class
    3. Move to ComplianceAnalysisService and call from both

---

## Porting Strategy

### Option A: Start Simple (RECOMMENDED)

**Phase 1:** Port `get_evidence_recommendations()` only
- Simple method (28 lines)
- Minimal dependencies
- Can test quickly
- Low risk

**Phase 2:** Add helper methods one at a time
- Port parsing helpers first
- Then prompt builders
- Then enhancement logic

**Phase 3:** Port `get_context_aware_recommendations()`
- After all helpers are ready
- After ComplianceAnalysisService has `analyze_evidence_gap()`

### Option B: Port Everything at Once

**Risk:** ⚠️ HIGH
- Too many moving parts
- Hard to test incrementally
- One error breaks everything

**Not Recommended**

---

## Current EvidenceService Status

**File:** `services/ai/domains/evidence_service.py`
**Current Lines:** 81
**Current Implementation:**
```python
async def get_recommendations(self, user, business_profile_id, framework, control_id=None):
    # Placeholder - just calls fallback
    return self.fallback_generator.get_recommendations(framework, {})
```

**What needs to change:**
- Replace placeholder with real AI generation
- Add all helper methods
- Add proper error handling
- Add maturity analysis (share with WorkflowService)

---

## Estimated Effort

### Conservative (Method by Method)

1. Port `get_evidence_recommendations()`: **30 minutes**
   - Simple method
   - Test as we go

2. Port parsing helpers (3 methods): **45 minutes**
   - `_parse_ai_recommendations()`
   - `_parse_text_recommendations()`
   - `_summarize_evidence_types()`

3. Port prompt builder: **30 minutes**
   - `_build_contextual_recommendation_prompt()`

4. Port generation logic: **45 minutes**
   - `_generate_contextual_recommendations()`

5. Port enhancement logic (2 methods): **45 minutes**
   - `_add_automation_insights()`
   - `_get_automation_guidance()`

6. Port prioritization: **30 minutes**
   - `_prioritize_recommendations()`

7. Port utility methods (2): **20 minutes**
   - `_generate_next_steps()`
   - `_calculate_total_effort()`

8. Port complex method: **45 minutes**
   - `get_context_aware_recommendations()`

9. Handle maturity analysis sharing: **30 minutes**
   - Decide on approach
   - Implement

**Total: ~5 hours** (broken into 9 small tasks)

---

## Recommendation

**Start with Phase 1: Simple Method**

1. ✅ Analysis complete (this document)
2. ⏳ Get user approval
3. ⏳ Create backup
4. ⏳ Port `get_evidence_recommendations()` only
5. ⏳ Test it works
6. ⏳ Review and decide on next step

**Benefits:**
- Quick win (30 minutes)
- Low risk
- Tests the approach
- Validates dependencies work

**Next Step After Approval:**
Create backup and port first method.
