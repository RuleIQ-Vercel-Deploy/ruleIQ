"""
Core constants for LangGraph compliance agent.
Defines SLOs, cost limits, router thresholds, and tenancy keys.
"""


# Performance SLOs
SLO_P95_LATENCY_MS = 2500  # P95 ≤ 2.5s end-to-end
SLO_FIRST_TOKEN_MS = 500   # Stream first token fast
SLO_AVAILABILITY = 0.999   # 99.9% uptime

# Cost Management
COST_LIMITS = {
    "min_per_1k_tokens": 0.20,
    "max_per_1k_tokens": 0.35,
    "daily_budget_usd": 100.0,
    "monthly_budget_usd": 2500.0,
}

# Router Decision Thresholds
ROUTER_THRESHOLDS = {
    "rules_confidence": 0.95,      # Deterministic rule matching
    "classifier_confidence": 0.80,  # Lightweight ML classifier
    "llm_fallback_threshold": 0.70, # When to use expensive LLM
    "unknown_threshold": 0.50,     # Log as unknown for training
}

# Tenancy and Security
TENANCY_KEYS = {
    "company_id_header": "X-Company-ID",
    "thread_id_header": "X-Thread-ID",
    "user_id_header": "X-User-ID",
    "tenant_isolation_required": True,
}

# Graph Node Types
GRAPH_NODES = {
    "router": "router",
    "compliance_analyzer": "compliance_analyzer",
    "obligation_finder": "obligation_finder",
    "evidence_collector": "evidence_collector",
    "legal_reviewer": "legal_reviewer",
    "autonomy_policy": "autonomy_policy",
    "model": "model",
}

# Interrupt Types
INTERRUPT_TYPES = {
    "legal_review": "legal_review",
    "evidence_validation": "evidence_validation",
    "framework_selection": "framework_selection",
}

# Route Classifications
ROUTE_TYPES = [
    "compliance_analysis",
    "obligation_search",
    "evidence_collection",
    "legal_review",
    "policy_generation",
    "risk_assessment",
]

# Retrieval Configuration
RETRIEVAL_CONFIG = {
    "default_k": 6,                # Number of results to return
    "max_fanout": 3,               # Parallel framework searches
    "vector_dimension": 1536,      # OpenAI embedding dimension
    "similarity_threshold": 0.7,   # Minimum similarity score
    "max_context_tokens": 8000,    # Maximum context length
}

# Security Configuration
SECURITY_CONFIG = {
    "hmac_algorithm": "sha256",
    "signature_replay_window_seconds": 60,
    "jwt_algorithm": "HS256",
    "jwt_expiry_hours": 24,
    "max_tool_calls_per_session": 100,
}

# Rate Limiting (aligned with existing ruleIQ limits)
RATE_LIMITS = {
    "general_per_minute": 100,
    "ai_endpoints_per_minute": 20,
    "auth_endpoints_per_minute": 5,
    "langgraph_per_minute": 30,    # New limit for LangGraph endpoints
}

# Model Configuration
MODEL_CONFIG = {
    "embedding_model": "mistral-embed",  # Mistral embeddings
    "primary_model": "gemini-1.5-pro",     # Aligned with ruleIQ
    "fallback_model": "gpt-4o-mini",      # Aligned with ruleIQ
    "streaming_models": ["gemini-1.5-pro", "gpt-4o"],
    "json_mode_models": ["gpt-4o", "gpt-4o-mini"],
    "max_tokens": 4000,
    "temperature": 0.1,
}

# RAG Configuration  
RAG_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_results": 10,
    "min_relevance_score": 0.5,
    "enable_reranking": True,
    "cache_ttl_hours": 24,
}

# Compliance Frameworks (UK focus aligned with ruleIQ)
COMPLIANCE_FRAMEWORKS = [
    "GDPR",
    "UK_GDPR",
    "DPA_2018",
    "PECR",
    "ISO_27001",
    "NIST_Cybersecurity",
    "PCI_DSS",
    "SOX",
    "FCA_Handbook",
]

# Business Sectors (aligned with ruleIQ business profiles)
BUSINESS_SECTORS = [
    "retail",
    "healthcare",
    "finance",
    "technology",
    "manufacturing",
    "education",
    "hospitality",
    "professional_services",
    "construction",
    "transport",
]

# Agent Autonomy Levels (aligned with Agentic Vision)
AUTONOMY_LEVELS = {
    "transparent_helper": 1,    # Shows all reasoning, asks confirmation
    "trusted_advisor": 2,       # Makes confident suggestions, learns preferences
    "autonomous_partner": 3,    # Takes initiative, manages workflows
}

# Turn and Tool Limits
EXECUTION_LIMITS = {
    "max_turns_per_session": 20,
    "max_tool_calls_per_turn": 5,
    "max_tokens_per_session": 50000,
    "session_timeout_minutes": 30,
}

# Monitoring and Metrics
METRIC_TAGS = [
    "node_type",
    "company_id",
    "route_type",
    "model_name",
    "autonomy_level",
    "framework_type",
]

# Error Categories
ERROR_CATEGORIES = {
    "validation_error": "validation_error",
    "authentication_error": "authentication_error",
    "authorization_error": "authorization_error",
    "rate_limit_error": "rate_limit_error",
    "model_error": "model_error",
    "retrieval_error": "retrieval_error",
    "timeout_error": "timeout_error",
    "unknown_error": "unknown_error",
}

# Database Configuration (PostgreSQL checkpointer)
DATABASE_CONFIG = {
    "checkpointer_table": "langgraph_checkpoints",
    "writes_table": "langgraph_writes",
    "isolation_level": "READ_COMMITTED",
    "pool_size": 5,
    "max_overflow": 10,
}
