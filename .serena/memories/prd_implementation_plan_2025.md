# RuleIQ PRD Implementation Plan - UK Release Candidate 2025

## Overview
Comprehensive plan for UK-first MVP release by Dec 1, 2025, targeting 50% reduction in audit prep time through AI-first compliance automation.

## Target Features Summary
- **Framework Library**: ISO27001, SOC2, GDPR, Cyber Essentials (P0)
- **AI Policy Assistant**: GPT-powered policy generation and refinement
- **Evidence Automation**: GitHub/AWS/GWorkspace integrations with AI classification
- **Task Workflow Engine**: AI-prioritized remediation tasks
- **GDPR/PECR Modules**: DPIA wizard, breach logging, consent manager
- **UK Gov Integrations**: Companies House/HMRC filing reminders
- **Security Hardening**: MFA, encryption, UK data residency (eu-west-2)

## Sprint Breakdown (6 x 2-week sprints)

### Sprint 1: Framework Foundation (Aug 30 - Sep 12)
**Deliverables**:
- UK compliance frameworks loaded (≥4 frameworks)
- Policy template library (20 UK-specific templates)
- Policy AI assistant endpoint (`/ai/policy_suggest`)
- Basic RBAC (Admin/Contributor/Auditor roles)

**Code Impact**:
- Extend `ComplianceFramework` model for UK region/version
- Integrate with existing `ComplianceAssistant` class
- Add role column to User model with permission decorators

### Sprint 2: Evidence Core & GitHub (Sep 13 - Sep 26)
**Deliverables**:
- Evidence auto-classifier (≥50% accuracy on suggestions)
- GitHub integration fetching commit history nightly
- Audit logging for evidence add/remove operations
- Evidence list showing AI-proposed control tags

**Code Impact**:
- Utilize existing `Evidence.ai_metadata` JSONB field
- Create GitHub integration following Google Workspace pattern
- Extend `EvidenceAuditLog` with generalized logging decorator

### Sprint 3: Workflow Engine (Sep 27 - Oct 10)
**Deliverables**:
- Task assignment UI with due dates and contributor assignment
- AI-generated Implementation Plan using `SmartEvidenceCollector`
- Dashboard showing task counts and basic AI insights
- Risk Register with AI severity scoring

**Code Impact**:
- Implement Task model linking to controls/evidence
- Integrate existing `SmartEvidenceCollector.create_collection_plan()`
- Add Risk model with GPT-4 advisor integration

### Sprint 4: UK Compliance Modules (Oct 11 - Oct 24)
**Deliverables**:
- DPIA wizard with AI assistance and PDF report generation
- Breach incident logging with severity classification
- Cookie consent banner with backend choice recording
- Companies House integration for filing date reminders

**Code Impact**:
- Create DPIA and Incident models with ReportLab PDF generation
- React consent context with ConsentLog backend model
- Companies House API integration with scheduled Celery tasks

### Sprint 5: Security & Reporting (Oct 25 - Nov 7)
**Deliverables**:
- Full RBAC enforcement (Auditor read-only verified)
- Compliance dashboard with framework scores and trends
- "Export Audit Report" with AI-generated executive summary
- MFA enforcement for admins, DB/S3 encryption enabled

**Code Impact**:
- Complete permission system with endpoint decorators
- Build report generator using existing charting components
- Configure AWS KMS encryption and eu-west-2 residency

### Sprint 6: Testing & Hardening (Nov 10 - Nov 28)
**Deliverables**:
- External CREST-certified pentest completed (critical/high findings resolved)
- Performance target met (200 req/s, <500ms p95 latency)
- Internal compliance audit using RuleIQ on RuleIQ
- All P0 features complete and passing tests

## Resource Requirements
- **Backend Engineers**: 3 FTE (existing team capacity)
- **Frontend Engineers**: 2 FTE  
- **ML Engineer**: 1 FTE (AI feature development and optimization)
- **DevOps**: 1 FTE (infrastructure hardening, monitoring)
- **Compliance SME**: 1 FTE part-time (content validation, legal review)
- **QA Engineer**: 2 FTE (security testing, workflow validation)

## Critical Risks & Mitigations
1. **AI Hallucinations** (Impact: 5, Likelihood: 2)
   - Mitigation: Human review loops, extensive testing with compliance team
2. **Integration Delays** (Impact: 4, Likelihood: 3)  
   - Mitigation: Start with minimal viable connectors, parallelize development
3. **Scope Creep** (Impact: 4, Likelihood: 4)
   - Mitigation: Strict MoSCoW prioritization, timebox UK-specific features

## Existing Codebase Leverage
- `ComplianceAssistant` class ready for AI orchestration
- `Evidence.ai_metadata` field for AI classifier outputs
- Integration framework supports multiple providers (`aws`, `google_workspace`)
- Google Workspace integration as implementation template
- `SmartEvidenceCollector` for task prioritization logic

## Success Metrics
- 100% P0 backlog completion
- Security: No critical/high pentest findings
- Performance: <500ms p95 response time under 200 req/s
- User Acceptance: ≥4/5 CSAT from 2 UK pilot customers
- AI Features: ≥50% evidence auto-classification accuracy

## Timeline
**Phase 0**: Aug 4-29 (Discovery & Design)
**Sprints 1-6**: Aug 30 - Nov 28 (Development)
**GA Release**: Dec 1, 2025 (UK Launch)
**Phase 2**: Dec 2 - Feb 20, 2026 (P1 features, Azure/Atlassian connectors)