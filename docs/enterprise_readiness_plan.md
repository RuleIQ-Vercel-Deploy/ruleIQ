# ruleIQ Enterprise Readiness Plan (Top 1%)

Objectives
- Elevate ruleIQ to best-in-class enterprise readiness across safety, privacy, reliability, retrieval quality, cost governance, and release discipline.
- Deliver measurable outcomes: zero-sev1 regressions during AI outages, audit-defensible safety logs, improved RAG answer fidelity, enforced cost ceilings, and provable evaluation gates.

Guiding principles
- Security- and privacy-by-design; default deny on uncertain content.
- Observability everywhere; treat AI as production infra (SLOs, budgets, and gates).
- Backwards-compatible rollouts with canaries and kill-switches.
- Automated verification; humans approve, not manually verify.

Workstreams and deliverables

WS1. Durable Safety & Audit Trail (High)
Deliverables
- Postgres schema and DAL for safety_decisions with tenant/org/user scoping, retention policy, and indexing.
- Write-path from AdvancedSafetyManager.evaluate_content_safety to database; append-only, immutable record with hash chain for tamper-evidence.
- Signed export to SIEM (JSONL over HTTPS Syslog/OTel logs) and on-demand PDF/CSV exports with filters.
- Admin APIs: list/filter/export decisions; configurable retention and redaction rules.

Acceptance criteria
- 100% of safety decisions persisted within 250 ms P95.
- Audit export under 60 seconds for 30-day window; hash-chain verification passes.
- RBAC enforced; no cross-tenant leakage (tests included).

KPIs
- Decision persistence error rate &lt; 0.1%; SIEM export lag &lt; 30s.

WS2. PII Detection & Redaction Pipeline (High)
Deliverables
- Pre-LLM input pipeline: pattern detectors (email, phone, national IDs), configurable custom regex, and ML-NER model (e.g., spacy en_core_web_trf or Presidio) for names/locations; redaction tags with reversible vault lookups if needed.
- Post-LLM output scrub with same detectors.
- Role-based bypass/justification flow for compliance officers; logs into safety audit.
- Unit, integration, and corpus tests with seeded sensitive samples.

Acceptance criteria
- &gt;98% precision, &gt;95% recall on internal PII validation set; zero PII egress in golden test suite.

KPIs
- PII egress incidents = 0; average redaction latency &lt; 40 ms.

WS3. RAG Quality: Embedding Upgrade & Reindex (Med-High)
Deliverables
- Move from 384-dim to 768–1024-dim embeddings (e.g., bge-large-en, e5-large-v2).
- Neo4j vector index migration (new index; run parallel) with tuned HNSW params and chunking strategy re-evaluation (overlap, window sizes).
- Re-ingestion pipeline with backfill jobs, progress monitoring, and roll-forward plan.
- AB tests on golden QA: hit rate, MRR, nDCG@k, factuality error rate; acceptance thresholds (+8–12% recall@5).

Acceptance criteria
- Meets or exceeds target uplift across goldens; no cost blow-up &gt; 25%.

KPIs
- Recall@5 +10% vs baseline; hallucination rate −30%.

WS4. Provider Abstraction, Policy Routing, and Fallbacks (Med-High)
Deliverables
- Central ProviderFacade with interfaces for chat, embeddings, and moderation; single choke point for routing, tracing, token accounting.
- Policy/routing engine: per-tenant, per-region, per-content-type (e.g., Gemini Pro for policy/regulatory, Flash for simple chat, OpenAI fallback in us‑only).
- Data-residency and export controls; enforce on provider selection and storage layers.
- Integration with circuit breaker for model-specific trip and automatic fallbacks; canary flags.

Acceptance criteria
- 100% traffic through ProviderFacade; kill-switch for any provider; conformance tests.

KPIs
- Fallback success rate &gt; 95% during single-provider outage; P95 latency within SLO.

WS5. Token Telemetry & Cost Governance (Med)
Deliverables
- Parse real token usage from provider SDK responses; normalize to a standard schema and persist in Redis/Postgres.
- Reconcile estimated vs actual costs; drift alert if &gt;5%.
- Policy-based budgets: per-tenant daily/monthly, per-feature caps, and hard-stop with graceful degradation (cached answers/fallback content).
- Exec dashboards: cost trends, per-feature ROI, “cost per successful task”.

Acceptance criteria
- 100% of AI calls have actual token counts; estimates only as explicit fallback.

KPIs
- Cost drift &lt; 5%; monthly cost savings &gt; 15% from routing/caching.

WS6. Eval-to-Prod Gates, A/B Automation, and Drift Monitors (High)
Deliverables
- CI gate: PRs impacting prompts/models/routing require passing evaluation suite (goldens + statistical tests via ab_testing_framework) and regression caps.
- Scheduled drift monitors: retrieval hit-rate, answer consistency, toxicity/safety rule triggers, cost per task; alerts in Slack/PagerDuty.
- Rollout strategy: progressive delivery (1% → 10% → 50% → 100%) with automatic rollback on SLO breach.

Acceptance criteria
- No prod rollout of AI changes without green eval and no active drift alerts.

KPIs
- Post-deploy incident rate &lt; 0.5% of releases; automatic rollback MTTR &lt; 10 min.

WS7. Observability, SLOs, and Runbooks (Med)
Deliverables
- OpenTelemetry spans for request → provider call → safety decision → persistence; correlation IDs.
- SLOs: availability, latency (P95), safety decision latency, retrieval success rate, budget conformance.
- Runbooks for provider outage, cost spike, safety audit export surge, index reingestion.

Acceptance criteria
- All SLOs visible on dashboards; paging on burn-rate; runbooks validated by game days.

KPIs
- Alert precision &gt; 80%; false positives trending ↓ month-over-month.

90‑day phased roadmap
Days 0–30
- WS1: Implement safety decisions DB + write-path + SIEM export.
- WS2: PII detection v1 (regex + Presidio/Spacy) pre/post; integrate in assistant and assessment flows.
- WS5: Actual token parsing and persistence; drift alerts; budget enforcement MVP.
- WS7: OTel wiring for AI calls, base SLO dashboards; draft runbooks.
Outcome: Audit-defensible safety logging; cost visibility within 5%; zero-PII egress in tests.

Days 31–60
- WS3: New embeddings index (parallel), reingestion pipeline, A/B on goldens.
- WS4: ProviderFacade v1 with policy routing and residency enforcement; fallback paths via circuit breaker.
- WS6: CI eval gate with goldens + A/B harness, Slack alerts; progressive rollout automation.
Outcome: +10% retrieval quality; reliable fallbacks; blocked risky deployments by default.

Days 61–90
- WS2: PII NER tuning, domain-specific dictionaries; role-based bypass workflows and logging.
- WS4: Tenant-level routing policies exposed in admin UI/APIs; canary flags.
- WS6/7: Drift monitors complete; game days; finalize runbooks; audit readiness review.
Outcome: Enterprise-grade operational maturity; automated, safe iteration cadence.

Technical specifications (key changes)
Safety DB schema (Postgres)
- Tables: safety_decisions(id, org_id, user_id, content_type, decision, confidence, applied_filters, request_hash, prev_hash, created_at, metadata JSONB)
- Indexes: (org_id, created_at), GIN on metadata; optional partition by month for retention.
- Hash-chain: prev_hash → tamper-evidence; nightly verification job.

PII pipeline
- Pre-LLM: SanitizeRequest middleware → detect (regex + NER) → replace with [REDACTED:&lt;type&gt;] → mapping stored in secure vault (optional reversible).
- Post-LLM: SanitizeResponse → scrub outputs; annotate safety decision with redaction summary.
- Config via config/privacy.yml; per-tenant overrides.

ProviderFacade
- Interfaces: ChatClient.generate, Embeddings.embed, Moderation.check.
- Routing policy DSL (YAML): match on tenant, region, content_type, risk_level, cost_tier.
- Observability: trace attributes: provider, model, tokens_in/out, cost_usd, latency_ms, cache_hit.

Token telemetry
- Normalizers for Gemini/OpenAI responses; fall back to tokenizer estimate with source=estimated.
- Reconciliation job: aggregates vs invoice; alert on &gt;5% variance.

RAG reindex
- Chunking policy: 800–1200 tokens, 10–15% overlap; store both document-level and chunk-level embeddings.
- HNSW: M=32–48, efConstruction=200+, efSearch=64–128; verify per corpus size.

Eval gates
- Goldens: regulatory Q&amp;A, policy summaries, definitions; metrics: exact match, semantic similarity, citation completeness, safety pass.
- A/B harness: Welch t-test/MWU selection; power ≥ 0.8; early-stopping on futility/superiority.
- CI step fails on KPI regression beyond budgets; artifacts uploaded to dashboard.

Governance, security, and compliance mapping
- GDPR/UK GDPR: PII minimization, purpose limitation, auditability, subject rights (export/delete per tenant).
- ISO 27001 controls: A.8 (Asset), A.10 (Cryptography), A.12 (Ops Security), A.16 (Incident), A.18 (Compliance).
- SOC 2: Security, Confidentiality, Processing Integrity (audit trail and change mgmt).
- AI Safety: documentation for safety profiles, decision rationale, and override workflows.

Risks &amp; mitigations
- Index migration performance: run parallel index; throttle ingestion; switch via feature flag after shadow testing.
- PII over-blocking: staged thresholds; feedback loop from users; bypass for compliance officers (logged).
- Provider price/latency drift: automated model benchmarking weekly; routing policy auto-adjust suggestions.
- False-positive alerts: tune thresholds with burn-rate SLOs and historical baselines.

Ownership and resourcing
- Product &amp; Compliance: define policies, routing rules, and acceptance thresholds.
- Platform/Backend: WS1, WS4, WS5, WS7.
- AI/IR: WS2, WS3, WS6.
- SRE: SLOs, dashboards, runbooks, game days.
- Security: DPIA, data flow mapping, retention policies validation.

Success criteria (exit checks)
- Safety decisions 100% persisted; SIEM integrated; quarterly audit passed.
- PII egress = 0 in automated tests; manual spot-checks clean.
- Retrieval quality uplift ≥ +10% on goldens; hallucination rate ↓ 30%+.
- Provider outage: no-sev1; auto-fallback engaged; budgets respected.
- All AI-affecting PRs gated by automated eval; rollback MTTR &lt; 10 min.
- Exec dashboards show reliable costs, usage, and safety metrics with ≤5% drift.

Change log (this commit)
- Added docs/enterprise_readiness_plan.md (this file).
- Added config/privacy.yml and config/routing_policies.yml skeletons.
- Added Alembic migration to create safety_decisions table with indices and hash-chain fields (tamper-evidence foundation).