# Large File Refactoring Implementation Guide

## Overview
This document details the modular refactoring of 4 monolithic files into domain-specific modules to improve maintainability, testability, and adherence to Single Responsibility Principle.

## Files to Refactor

### 1. api/routers/chat.py
**Current Issues**: Monolithic router with multiple concerns
**Target Structure**:
```
api/routers/chat/
├── __init__.py           # Main router aggregation
├── conversations.py      # Conversation CRUD operations
├── messages.py           # Message send/receive endpoints
├── evidence.py           # Evidence collection endpoints
├── analytics.py          # Usage analytics endpoints
├── smart_evidence.py     # Smart evidence recommendation
└── iq_agent.py          # IQ Agent integration endpoints
```

**Domain Breakdown**:
- **conversations.py**: Create, list, get, delete conversations
- **messages.py**: Send messages, get message history
- **evidence.py**: Link evidence, get evidence recommendations
- **analytics.py**: Usage metrics, conversation statistics
- **smart_evidence.py**: AI-powered evidence suggestions
- **iq_agent.py**: IQ Agent quick checks and analysis

### 2. app/core/monitoring/langgraph_metrics.py
**Current Issues**: Single file handling all metrics tracking
**Target Structure**:
```
app/core/monitoring/langgraph_metrics/
├── __init__.py           # Main metrics aggregation
├── execution_tracker.py  # Execution time and performance metrics
├── token_tracker.py      # Token usage tracking
├── error_tracker.py      # Error and exception tracking
├── step_tracker.py       # Step progression tracking
└── aggregator.py         # Metrics aggregation and reporting
```

**Domain Breakdown**:
- **execution_tracker.py**: Track execution times, latency, throughput
- **token_tracker.py**: Monitor LLM token usage across agents
- **error_tracker.py**: Capture errors, exceptions, retry attempts
- **step_tracker.py**: Track step transitions, state changes
- **aggregator.py**: Combine metrics for dashboards and alerts

### 3. frontend/lib/utils/export.ts
**Current Issues**: 1505 lines handling all export formats
**Target Structure**:
```
frontend/lib/utils/export/
├── index.ts              # Public API and main export function
├── types.ts              # Shared types and interfaces
├── csv-exporter.ts       # CSV export logic
├── excel-exporter.ts     # Excel export logic
├── pdf-exporter.ts       # PDF export logic
├── formatters.ts         # Data formatting utilities
├── validators.ts         # Export validation logic
└── utils.ts              # Shared helper functions
```

**Domain Breakdown**:
- **csv-exporter.ts**: CSV generation using xlsx library
- **excel-exporter.ts**: Multi-sheet Excel workbook creation
- **pdf-exporter.ts**: PDF generation with jsPDF and autotable
- **formatters.ts**: Date, score, severity formatting
- **validators.ts**: Data validation before export
- **utils.ts**: Filename sanitization, color conversion, browser checks

### 4. frontend/lib/stores/freemium-store.ts
**Current Issues**: 1263 lines mixing state, actions, API calls
**Target Structure**:
```
frontend/lib/stores/freemium/
├── index.ts              # Main store export and composition
├── types.ts              # Store types and interfaces
├── initial-state.ts      # Initial state definition
├── lead-slice.ts         # Lead capture and management
├── session-slice.ts      # Session and authentication
├── assessment-slice.ts   # Assessment flow and questions
├── results-slice.ts      # Results generation and viewing
├── consent-slice.ts      # Consent and GDPR compliance
├── analytics-slice.ts    # Event tracking and analytics
└── api-service.ts        # API integration layer
```

**Domain Breakdown**:
- **lead-slice.ts**: `captureLead`, `setLeadInfo`, `updateLeadScore`
- **session-slice.ts**: `startAssessment`, `loadSession`, `clearSession`
- **assessment-slice.ts**: `submitAnswer`, `skipQuestion`, `goToPreviousQuestion`
- **results-slice.ts**: `generateResults`, `markResultsViewed`
- **consent-slice.ts**: `setMarketingConsent`, `updateConsent`
- **analytics-slice.ts**: `trackEvent`, `recordBehavioralEvent`

## Implementation Steps

### Phase 1: Backend Refactoring (chat.py, langgraph_metrics.py)

#### Step 1.1: Chat Router Refactoring
1. Create `/api/routers/chat/` directory
2. Extract conversation endpoints to `conversations.py`
3. Extract message endpoints to `messages.py`
4. Extract evidence endpoints to `evidence.py`
5. Extract analytics endpoints to `analytics.py`
6. Extract smart evidence to `smart_evidence.py`
7. Extract IQ Agent endpoints to `iq_agent.py`
8. Create aggregating `__init__.py`
9. Update `api/main.py` import from `api.routers.chat` to `api.routers.chat`
10. Test all chat endpoints

#### Step 1.2: LangGraph Metrics Refactoring
1. Create `/app/core/monitoring/langgraph_metrics/` directory
2. Extract execution tracking to `execution_tracker.py`
3. Extract token tracking to `token_tracker.py`
4. Extract error tracking to `error_tracker.py`
5. Extract step tracking to `step_tracker.py`
6. Create metrics aggregator in `aggregator.py`
7. Create unified `__init__.py`
8. Update all metric collection callsites
9. Test metrics collection and reporting

### Phase 2: Frontend Refactoring (export.ts, freemium-store.ts)

#### Step 2.1: Export Utils Refactoring
1. Create `/frontend/lib/utils/export/` directory
2. Extract types to `types.ts`
3. Extract CSV logic to `csv-exporter.ts`
4. Extract Excel logic to `excel-exporter.ts`
5. Extract PDF logic to `pdf-exporter.ts`
6. Extract formatters to `formatters.ts`
7. Extract validators to `validators.ts`
8. Extract utilities to `utils.ts`
9. Create public API in `index.ts`
10. Update import statements across frontend
11. Test all export formats

#### Step 2.2: Freemium Store Refactoring
1. Create `/frontend/lib/stores/freemium/` directory
2. Extract types to `types.ts`
3. Extract initial state to `initial-state.ts`
4. Create lead slice in `lead-slice.ts`
5. Create session slice in `session-slice.ts`
6. Create assessment slice in `assessment-slice.ts`
7. Create results slice in `results-slice.ts`
8. Create consent slice in `consent-slice.ts`
9. Create analytics slice in `analytics-slice.ts`
10. Extract API calls to `api-service.ts`
11. Compose store in `index.ts`
12. Update component imports
13. Test freemium flow end-to-end

### Phase 3: Integration and Testing

#### Step 3.1: Update Imports and Registrations
1. Update all import statements in dependent files
2. Update API router registrations in `api/main.py`
3. Update frontend component imports
4. Update test imports
5. Verify build passes: `make test-fast` (backend), `pnpm build` (frontend)

#### Step 3.2: Regression Testing
1. **Backend Tests**:
   - Test chat conversation creation
   - Test message send/receive
   - Test evidence linking
   - Test metrics collection
   - Test IQ Agent integration

2. **Frontend Tests**:
   - Test CSV export with sample data
   - Test Excel export with all sheets
   - Test PDF export with charts
   - Test freemium lead capture
   - Test freemium assessment flow
   - Test results generation

3. **Integration Tests**:
   - Test full chat conversation flow
   - Test full freemium assessment flow
   - Test export from results page
   - Test metrics dashboard updates

#### Step 3.3: Documentation Updates
1. Update API documentation with new router structure
2. Update frontend documentation with new module structure
3. Add module-level READMEs explaining each domain
4. Update CLAUDE.md with new architecture
5. Add migration guide for developers

## Benefits of This Refactoring

### Maintainability
- **Single Responsibility**: Each module handles one domain concern
- **Easier Navigation**: Clear file structure maps to functionality
- **Reduced Cognitive Load**: Smaller files are easier to understand

### Testability
- **Isolated Testing**: Test individual domains without mocking entire system
- **Better Coverage**: Easier to achieve 100% coverage per module
- **Faster Tests**: Can run domain-specific test suites

### Performance
- **Code Splitting**: Frontend modules can be lazy-loaded
- **Selective Imports**: Import only what's needed
- **Better Tree Shaking**: Unused code eliminated in production builds

### Collaboration
- **Parallel Development**: Multiple developers can work on different slices
- **Clear Ownership**: Each module has clear domain boundaries
- **Easier Reviews**: Smaller PRs focused on specific domains

## Migration Strategy

### Backward Compatibility
- Keep original files as deprecated wrappers initially
- Add deprecation warnings in logs
- Provide 2-sprint migration period
- Remove deprecated files after full migration

### Rollback Plan
- Tag codebase before refactoring starts
- Keep original files until all tests pass
- Use feature flags for gradual rollout
- Monitor error rates during migration

## Success Metrics

### Code Quality
- **File Size**: No file over 500 lines
- **Cyclomatic Complexity**: Max complexity of 10 per function
- **Test Coverage**: Maintain 95%+ coverage

### Performance
- **Build Time**: Frontend build under 30 seconds
- **Test Time**: Backend tests under 2 minutes
- **Import Resolution**: Under 100ms for module resolution

### Developer Experience
- **Onboarding Time**: New developers understand structure in 1 day
- **PR Review Time**: Average PR review under 30 minutes
- **Bug Fix Time**: Average bug fix under 2 hours

## Timeline

- **Week 1**: Chat router and LangGraph metrics refactoring (Backend)
- **Week 2**: Export utils and freemium store refactoring (Frontend)
- **Week 3**: Integration, testing, and documentation
- **Week 4**: Migration and cleanup

---

**Document Version**: 1.0
**Last Updated**: 2025-10-01
**Owner**: Engineering Team
