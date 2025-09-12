# Epic: Complete LangGraph and Golden Dataset Integration

## Epic ID: EPIC-2025-001
**Priority**: P1 - Critical
**Sprint**: Sprint 2025-Q1
**Epic Owner**: Engineering Team
**Estimated Story Points**: 21

## Executive Summary
The LangGraph implementation and Golden Dataset system are partially implemented but have critical integration issues preventing full functionality. This epic addresses all identified gaps to enable the AI-powered compliance orchestration system to operate at full capacity.

## Business Value
- **Enable AI-Driven Compliance**: Fully functional LangGraph workflows will automate 95% of compliance tasks
- **Quality Assurance**: Golden datasets ensure consistent, high-quality AI responses
- **Risk Reduction**: Proper integration reduces compliance gaps and improves accuracy
- **Time to Market**: Fixing these issues unblocks multiple dependent features

## Current State Analysis

### Working Components ✅
1. Core LangGraph StateGraph implementation in IQ Agent
2. Golden Dataset loader infrastructure
3. Basic workflow pipeline (Perceive → Plan → Act → Learn → Remember → Respond)
4. API integration at `/api/v1/iq` endpoints

### Critical Issues ⚠️
1. **QueryCategory Enum Incomplete**: Missing REGULATORY_COVERAGE and other query types
2. **Schema Mismatches**: ComplianceScenario schema doesn't align with data structure
3. **Async/Await Issues**: Coroutines not properly awaited causing runtime errors
4. **LLM Integration Broken**: ChatOpenAI missing required async methods
5. **Golden Dataset Directory**: Missing proper versioned dataset structure

## User Stories

### Story 1: Fix QueryCategory Enum and Compliance Queries
**Points**: 3
**Acceptance Criteria**:
- [ ] Add REGULATORY_COVERAGE to QueryCategory enum
- [ ] Add COMPLIANCE_GAPS query category
- [ ] Add CROSS_JURISDICTIONAL query category
- [ ] Implement execute_compliance_query for all categories
- [ ] Unit tests pass for all query types

### Story 2: Align Golden Dataset Schemas
**Points**: 5
**Acceptance Criteria**:
- [ ] Update ComplianceScenario schema to match actual data structure
- [ ] Update EvidenceCase schema for proper validation
- [ ] Update RegulatoryQAPair schema with required fields
- [ ] Create migration script for existing datasets
- [ ] Validation tests pass for all schema types

### Story 3: Fix Async/Await Implementation
**Points**: 3
**Acceptance Criteria**:
- [ ] Fix coroutine comparison in create_iq_agent
- [ ] Properly await all Neo4j operations
- [ ] Fix async context managers
- [ ] Add proper error handling for async operations
- [ ] Integration tests run without warnings

### Story 4: Repair LLM Integration
**Points**: 2
**Acceptance Criteria**:
- [ ] Replace ainvoke with proper async method (agenerate/acall)
- [ ] Add retry logic for LLM calls
- [ ] Implement proper token counting
- [ ] Add fallback for LLM failures
- [ ] LLM integration tests pass

### Story 5: Create Golden Dataset Infrastructure
**Points**: 5
**Acceptance Criteria**:
- [ ] Create services/ai/evaluation/data/golden_datasets directory
- [ ] Implement v1.0.0 dataset with proper structure
- [ ] Add versioning metadata files
- [ ] Create dataset migration tools
- [ ] Add CLI for dataset management
- [ ] Documentation for dataset creation

### Story 6: End-to-End Integration Testing
**Points**: 3
**Acceptance Criteria**:
- [ ] Create comprehensive integration test suite
- [ ] Test complete workflow from query to response
- [ ] Test golden dataset loading and validation
- [ ] Test Neo4j integration with LangGraph
- [ ] Performance benchmarks meet requirements
- [ ] All tests pass in CI/CD pipeline

## Technical Requirements

### Dependencies
- langgraph >= 0.0.26
- langchain-openai >= 0.0.5
- pydantic >= 2.0
- neo4j >= 5.0
- pytest-asyncio >= 0.21

### Architecture Changes
1. Refactor QueryCategory to use proper enum structure
2. Implement proper async context management
3. Add circuit breaker pattern for external services
4. Implement caching layer for golden datasets

### Performance Requirements
- Query response time < 2 seconds
- Golden dataset loading < 500ms
- Memory usage < 512MB per agent instance
- Support 100 concurrent requests

## Definition of Done
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] Deployed to staging environment
- [ ] Monitoring and alerts configured
- [ ] Product Owner acceptance

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Schema breaking changes | High | Medium | Implement versioning and migration tools |
| LLM API changes | High | Low | Abstract LLM interface, add fallbacks |
| Neo4j performance | Medium | Medium | Add caching, optimize queries |
| Golden dataset corruption | High | Low | Implement validation, backups |

## Success Metrics
- Zero critical bugs in production
- 95% uptime for IQ Agent
- <2s average response time
- 100% golden dataset validation pass rate
- 90% test coverage maintained

## Timeline
- **Week 1**: Stories 1-3 (Fix core issues)
- **Week 2**: Stories 4-5 (Infrastructure setup)
- **Week 3**: Story 6 (Testing and validation)
- **Week 4**: UAT, deployment, monitoring

## Notes
- This epic blocks the AI-powered compliance features
- Coordinate with DevOps for Neo4j cluster setup
- Review with Security team for data handling compliance
- Consider feature flags for gradual rollout

---
*Epic created: 2025-01-12*
*Last updated: 2025-01-12*

## QA Results

### Review Date: 2025-01-12

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment

**Critical Issues Identified**:
- **Story 1**: QueryCategory enum is completely empty (lines 38-40 in `services/compliance_retrieval_queries.py`) but referenced throughout the codebase with values like REGULATORY_COVERAGE, COMPLIANCE_GAPS, CROSS_JURISDICTIONAL, etc.
- **Story 5**: Golden dataset directory exists but only contains a sample file, missing the versioned structure required
- The code is attempting to use enum values that don't exist, which will cause immediate runtime failures

### Refactoring Performed

None - This epic requires implementation work rather than refactoring. The missing enum values and infrastructure must be added before any refactoring can occur.

### Compliance Check

- Coding Standards: [✗] Empty enum violates basic code completeness requirements
- Project Structure: [✓] File organization follows standards
- Testing Strategy: [✗] No tests can pass with empty enum
- All ACs Met: [✗] Core functionality is broken

### Improvements Checklist

**Must Fix (P0 - Blocking Production)**:
- [ ] Add all missing QueryCategory enum values (REGULATORY_COVERAGE, COMPLIANCE_GAPS, CROSS_JURISDICTIONAL, RISK_CONVERGENCE, TEMPORAL_CHANGES, ENFORCEMENT_LEARNING)
- [ ] Implement execute_compliance_query for all categories  
- [ ] Create golden_datasets directory structure with v1.0.0
- [ ] Fix async/await implementation issues
- [ ] Repair LLM integration (ainvoke → agenerate/acall)

**Should Fix (P1 - High Priority)**:
- [ ] Align ComplianceScenario schema with data structure
- [ ] Add proper error handling for Neo4j operations
- [ ] Implement retry logic for LLM calls
- [ ] Create migration scripts for existing datasets

**Nice to Have (P2 - Future Enhancement)**:
- [ ] Add circuit breaker pattern for external services
- [ ] Implement caching layer for golden datasets
- [ ] Add comprehensive logging throughout
- [ ] Create CLI tools for dataset management

### Security Review

- **Data Handling**: Golden datasets may contain sensitive compliance data - ensure proper access controls
- **LLM Integration**: Missing retry logic and error handling could expose sensitive prompts in logs
- **Neo4j Access**: No evidence of parameterized queries verification needed

### Performance Considerations

- **Query Performance**: No caching layer for golden datasets will impact response times
- **Memory Usage**: Loading entire golden datasets without pagination could cause memory issues
- **Concurrent Requests**: No rate limiting or connection pooling visible

### Test Coverage Analysis

**Story-Level Test Requirements**:
1. **Story 1**: Unit tests for each QueryCategory enum value
2. **Story 2**: Schema validation tests for all data models
3. **Story 3**: Async operation tests with proper mocking
4. **Story 4**: LLM integration tests with fallback scenarios
5. **Story 5**: Dataset loading and versioning tests
6. **Story 6**: End-to-end workflow tests

**Current Coverage**: 0% - Code cannot execute with empty enum

### Risk Assessment

| Risk | Severity | Probability | Impact |
|------|----------|-------------|--------|
| Runtime failures from empty enum | Critical | Certain (100%) | System non-functional |
| Data corruption without schemas | High | High (80%) | Invalid compliance data |
| LLM failures without retry | Medium | Medium (50%) | User experience degraded |
| Memory issues with large datasets | Medium | Low (30%) | Performance degradation |

### Gate Status

Gate: **FAIL** → docs/qa/gates/EPIC-2025-001-langgraph-golden-dataset.yml
Risk profile: High-risk epic with certain runtime failures
NFR assessment: Security and performance concerns identified

### Recommended Status

[✗ Changes Required - Critical issues must be resolved before proceeding]

The epic cannot proceed to implementation without fixing the empty QueryCategory enum. This is a **hard blocker** that will cause immediate runtime failures. All six stories have dependencies on this core issue being resolved first.