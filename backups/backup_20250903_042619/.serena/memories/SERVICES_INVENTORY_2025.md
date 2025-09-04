# RuleIQ Services Inventory - September 2025

## Core AI Services (`/services/ai/`)

### Circuit Breaker & Resilience
- `circuit_breaker.py`: Main circuit breaker implementation
- `cost_aware_circuit_breaker.py`: Cost-optimized circuit breaker
- `fallback_system.py`: Graceful degradation handlers
- `retry_handler.py`: Intelligent retry logic
- `offline_mode.py`: Offline capability support

### Performance & Optimization
- `performance_optimizer.py`: AI performance tuning
- `response_cache.py`: Response caching layer
- `cached_content.py`: Content caching strategies
- `google_cached_content.py`: Google-specific caching
- `ab_testing_framework.py`: A/B testing for AI models

### Evidence & Compliance
- `evidence_generator.py`: AI-powered evidence generation
- `smart_evidence_collector.py`: Intelligent evidence collection
- `evidence_tools.py`: Evidence processing utilities
- `compliance_query_engine.py`: Compliance-specific queries
- `compliance_ingestion_pipeline.py`: Compliance data ingestion

### Monitoring & Analytics
- `health_monitor.py`: AI service health monitoring
- `quality_monitor.py`: Response quality tracking
- `analytics_monitor.py`: Usage analytics
- `cost_management.py`: Token cost tracking
- `temporal_tracker.py`: Time-based tracking

### Evaluation Framework (`/services/ai/evaluation/`)
- Golden dataset management
- Custom evaluators
- Quality metrics
- Coverage metrics
- Infrastructure setup for Neo4j

## Business Services (`/services/`)

### Core Business Logic
- `assessment_service.py`: Assessment management
- `business_service.py`: Business profile operations
- `framework_service.py`: Compliance framework handling
- `policy_service.py`: Policy generation and management
- `implementation_service.py`: Implementation planning

### Authentication & Security
- `auth_service.py`: Authentication operations
- `rbac_service.py`: Role-based access control
- `api_key_management.py`: API key lifecycle
- `session_management.py`: Session handling
- `data_access_service.py`: Data access control

### AI & Automation
- `iq_agent.py`: Core IQ agent service
- `assessment_agent.py`: Assessment automation
- `agentic_rag.py`: RAG implementation
- `agentic_assessment.py`: AI-driven assessments
- `agentic_integration.py`: Agent integrations

### Evidence & Data
- `evidence_service.py`: Evidence management
- `evidence/orchestrator_v2.py`: Evidence orchestration v2
- `cache_service.py`: General caching service
- `context_service.py`: Context management

### Compliance & Knowledge
- `compliance_loader.py`: Compliance data loading
- `compliance_memory_manager.py`: Compliance memory
- `compliance_retrieval_queries.py`: Compliance queries
- `graphrag_retriever.py`: GraphRAG implementation
- `neo4j_service.py`: Neo4j operations

### Integrations & External
- `lead_scoring_service.py`: Lead scoring logic
- `freemium_assessment_service.py`: Freemium features
- `webhook_verification.py`: Webhook security
- `rate_limiting.py`: Rate limit enforcement

## API Routers (`/api/routers/`)

### Authentication & Security
- `auth.py`: Authentication endpoints
- `google_auth.py`: Google OAuth
- `rbac_auth.py`: RBAC endpoints
- `security.py`: Security operations
- `api_keys.py`: API key management

### Core Business Endpoints
- `assessments.py`: Assessment CRUD
- `business_profiles.py`: Business profile management
- `compliance.py`: Compliance operations
- `frameworks.py`: Framework management
- `policies.py`: Policy endpoints

### AI-Powered Endpoints
- `ai_assessments.py`: AI assessment endpoints
- `ai_policy.py`: AI policy generation
- `ai_cost_monitoring.py`: Cost tracking
- `ai_optimization.py`: Optimization endpoints
- `iq_agent.py`: IQ agent interactions
- `chat.py`: Chat functionality

### Evidence & Reporting
- `evidence.py`: Evidence management
- `evidence_collection.py`: Collection workflows
- `foundation_evidence.py`: Foundation evidence
- `reports.py`: Report generation
- `audit_export.py`: Audit exports

### Special Features
- `freemium.py`: Freemium endpoints
- `feedback.py`: Feedback collection
- `uk_compliance.py`: UK-specific compliance
- `integrations.py`: Third-party integrations
- `payment.py`: Payment processing

## Database Models (`/database/`)

### Core Models
- `user.py`: User accounts
- `business_profile.py`: Business profiles
- `assessment_session.py`: Assessment tracking
- `compliance_framework.py`: Framework definitions
- `evidence_item.py`: Evidence storage

### AI & Assessment
- `ai_question_bank.py`: AI question repository
- `ai_cost_models.py`: Cost tracking models
- `assessment_question.py`: Assessment questions
- `assessment_lead.py`: Lead information
- `freemium_assessment_session.py`: Freemium sessions

### Chat & Interaction
- `chat_conversation.py`: Conversation storage
- `chat_message.py`: Message records
- `generated_policy.py`: Generated policies

### Implementation & Planning
- `implementation_plan.py`: Implementation tracking
- `readiness_assessment.py`: Readiness scoring
- `report_schedule.py`: Report scheduling

### Analytics & Scoring
- `lead_scoring_event.py`: Lead scoring events
- `conversion_event.py`: Conversion tracking

## LangGraph Components (`/langgraph_agent/`)

### Graph Management
- `graph/app.py`: Main graph application
- `graph/master_integration_graph.py`: Master integration
- `graph/unified_state.py`: State management
- `graph/error_handler.py`: Error handling

### Node Types
- `nodes/compliance_nodes.py`: Compliance processing
- `nodes/evidence_nodes.py`: Evidence handling
- `nodes/reporting_nodes.py`: Report generation
- `nodes/rag_node.py`: RAG operations
- `nodes/notification_nodes.py`: Notifications

### Agent System
- `agents/agent_core.py`: Core agent logic
- `agents/rag_system.py`: RAG implementation
- `agents/tool_manager.py`: Tool orchestration
- `agents/memory_manager.py`: Memory management