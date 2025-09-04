# IQ Agent Implementation Guide

## Overview

This guide provides comprehensive instructions for deploying, configuring, and using the IQ Agent system - an autonomous compliance orchestrator powered by Neo4j GraphRAG and LangGraph intelligence loops.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

## System Architecture

The IQ Agent is built on a multi-layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI REST API                       │
│                   /api/v1/iq/*                             │
├─────────────────────────────────────────────────────────────┤
│                    IQ Agent Core                           │
│              (LangGraph Intelligence Loop)                  │
├─────────────────────────────────────────────────────────────┤
│                 Neo4j GraphRAG Layer                       │
│           (Compliance Knowledge Graph)                     │
├─────────────────────────────────────────────────────────────┤
│              Memory Management System                       │
│          (Conversation & Knowledge Storage)                 │
├─────────────────────────────────────────────────────────────┤
│                External AI Services                        │
│                  (OpenAI/Claude)                          │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **IQ Agent**: Autonomous compliance orchestrator with 5-node intelligence loop
2. **Neo4j GraphRAG**: Knowledge graph with 6 compliance domains and 12 regulations
3. **Memory Manager**: Conversation and knowledge consolidation system
4. **Retrieval Queries**: 14 categories of compliance analysis queries
5. **API Router**: RESTful endpoints with rate limiting and authentication

## Prerequisites

### Software Requirements

- Python 3.11+
- Neo4j 5.0+ (with APOC plugin)
- PostgreSQL 15+ (for application data)
- Redis (optional, for caching)

### Environment Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd ruleIQ

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Neo4j Setup

1. **Install Neo4j Desktop or Server**
   ```bash
   # Using Docker
   docker run \
     --name neo4j-compliance \
     -p7474:7474 -p7687:7687 \
     -d \
     -v $HOME/neo4j/data:/data \
     -v $HOME/neo4j/logs:/logs \
     -v $HOME/neo4j/import:/var/lib/neo4j/import \
     -v $HOME/neo4j/plugins:/plugins \
     --env NEO4J_AUTH=neo4j/your_password \
     --env NEO4J_PLUGINS='["apoc"]' \
     neo4j:5.20
   ```

2. **Configure APOC Plugin**
   - Ensure APOC is installed and enabled
   - Required for graph algorithms and data processing

## Installation & Setup

### 1. Environment Variables

Create `.env.local` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ruleiq
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

# AI Service Configuration
OPENAI_API_KEY=your_openai_api_key
# or
ANTHROPIC_API_KEY=your_anthropic_api_key

# Application Configuration
JWT_SECRET_KEY=your_jwt_secret_key
SECRET_KEY=your_app_secret_key
FERNET_KEY=your_fernet_encryption_key

# Optional: Redis Configuration
REDIS_URL=redis://localhost:6379

# Production Settings
ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

### 2. Database Setup

```bash
# Run Alembic migrations
alembic upgrade head

# Initialize compliance graph data
python database/init_db.py
```

### 3. Neo4j Graph Initialization

```bash
# Initialize compliance knowledge graph
python scripts/init_compliance_graph.py
```

This script creates:
- 6 compliance domains (AML, Data Protection, Operational Risk, etc.)
- 12 regulations (GDPR, 6AMLD, DORA, BSA, etc.)
- 150+ compliance requirements
- Cross-regulatory relationships
- Risk assessment patterns

### 4. Start the Application

```bash
# Development
python main.py

# Production with Gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Configuration

### IQ Agent Parameters

The IQ Agent can be configured via environment variables or direct instantiation:

```python
# Environment Variables
IQ_RISK_THRESHOLD=7.0          # Autonomy risk threshold (0-10)
IQ_AUTONOMY_BUDGET=10000.0     # Maximum autonomous action cost (USD)
IQ_MAX_ITERATIONS=50           # Maximum intelligence loop iterations
IQ_MEMORY_CONSOLIDATION_FREQ=10 # Memory consolidation frequency

# Graph Configuration
NEO4J_CONNECTION_TIMEOUT=30
NEO4J_MAX_RETRY_ATTEMPTS=3
NEO4J_BATCH_SIZE=1000

# Memory Management
MEMORY_MAX_CONVERSATION_HISTORY=100
MEMORY_CONSOLIDATION_THRESHOLD=0.8
MEMORY_CLEANUP_INTERVAL_HOURS=24
```

### Rate Limiting

API endpoints are rate-limited:

```python
# General endpoints: 100 requests/minute
# AI analysis endpoints: 20 requests/minute
# Authentication endpoints: 5 requests/minute
```

### Neo4j Graph Schema

The compliance graph uses this schema:

```cypher
// Core node types
(:ComplianceDomain {name, description, risk_level})
(:Regulation {code, name, jurisdiction, effective_date})
(:Requirement {id, title, description, risk_level, domain})
(:Control {id, title, type, implementation_guidance})
(:Risk {id, type, severity, likelihood, impact})

// Relationship types
-[:COVERS]->        // Domain covers regulation
-[:CONTAINS]->      // Regulation contains requirement
-[:IMPLEMENTS]->    // Control implements requirement
-[:MITIGATES]->     // Control mitigates risk
-[:RELATES_TO]->    // Cross-regulatory relationships
```

## Usage Guide

### 1. Basic Compliance Query

```python
import httpx

# Authenticate
response = httpx.post("/api/v1/auth/login", json={
    "email": "user@company.com",
    "password": "password"
})
token = response.json()["access_token"]

# Query compliance posture
response = httpx.post(
    "/api/v1/iq/query",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "query": "What are our GDPR compliance gaps?",
        "context": {
            "business_functions": ["data_processing", "customer_onboarding"],
            "regulations": ["GDPR", "DPA2018"],
            "risk_tolerance": "medium"
        },
        "include_graph_analysis": True,
        "include_recommendations": True
    }
)

result = response.json()
```

### 2. Memory Management

```python
# Store compliance insights
response = httpx.post(
    "/api/v1/iq/memory/store",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "memory_type": "compliance_insight",
        "content": {
            "insight": "GDPR consent mechanisms need improvement",
            "regulation": "GDPR",
            "domain": "Data Protection",
            "impact": "high"
        },
        "importance_score": 0.8,
        "tags": ["gdpr", "consent", "data_protection"]
    }
)

# Retrieve relevant memories
response = httpx.post(
    "/api/v1/iq/memory/retrieve",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "query": "GDPR consent management insights",
        "max_memories": 5,
        "relevance_threshold": 0.7
    }
)
```

### 3. Graph Initialization

```python
# Initialize or refresh compliance graph
response = httpx.post(
    "/api/v1/iq/graph/initialize",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "clear_existing": False,
        "load_sample_data": True
    }
)
```

### 4. Health Monitoring

```python
# Check IQ agent health
response = httpx.get(
    "/api/v1/iq/health?include_stats=true",
    headers={"Authorization": f"Bearer {token}"}
)

health_data = response.json()["data"]
print(f"Status: {health_data['status']}")
print(f"Neo4j Connected: {health_data['neo4j_connected']}")
print(f"Graph Statistics: {health_data['graph_statistics']}")
```

## API Reference

### Core Endpoints

#### POST /api/v1/iq/query
Analyze compliance posture and generate recommendations.

**Request Body:**
```json
{
  "query": "string (required)",
  "context": {
    "business_functions": ["string"],
    "regulations": ["string"],
    "risk_tolerance": "low|medium|high"
  },
  "include_graph_analysis": "boolean",
  "include_recommendations": "boolean"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "success",
    "timestamp": "2024-01-15T10:30:00Z",
    "summary": {
      "risk_posture": "MEDIUM",
      "compliance_score": 0.75,
      "top_gaps": ["string"],
      "immediate_actions": ["string"]
    },
    "artifacts": {
      "compliance_posture": "object",
      "action_plan": ["object"],
      "risk_assessment": "object"
    },
    "graph_context": {
      "nodes_traversed": "number",
      "patterns_detected": ["object"],
      "memories_accessed": ["string"],
      "learnings_applied": "number"
    },
    "evidence": {
      "controls_executed": "number",
      "evidence_stored": "number",
      "metrics_updated": "number"
    },
    "next_actions": ["object"],
    "llm_response": "string"
  }
}
```

#### POST /api/v1/iq/memory/store
Store compliance insights in IQ's memory.

#### POST /api/v1/iq/memory/retrieve
Retrieve relevant memories for contextual analysis.

#### POST /api/v1/iq/graph/initialize
Initialize or refresh the compliance knowledge graph.

#### GET /api/v1/iq/health
Check IQ agent and system health status.

#### GET /api/v1/iq/status
Lightweight status check for monitoring.

### Authentication

All endpoints require JWT authentication:

```bash
curl -H "Authorization: Bearer <token>" \
     -X POST /api/v1/iq/query
```

### Error Handling

Standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `429`: Too Many Requests (rate limiting)
- `500`: Internal Server Error
- `502`: Bad Gateway (AI service errors)
- `503`: Service Unavailable (IQ agent unavailable)

## Monitoring & Maintenance

### Health Checks

1. **Application Health**: `GET /api/v1/iq/health`
2. **Neo4j Connectivity**: Included in health checks
3. **Memory Usage**: Monitor via `/api/v1/iq/status`
4. **Rate Limiting**: Headers include remaining quota

### Performance Monitoring

```python
# Monitor query performance
import time

start = time.time()
response = httpx.post("/api/v1/iq/query", ...)
duration = time.time() - start

# Target: <2 seconds for standard queries
# Target: <5 seconds for complex analysis
```

### Log Monitoring

Key log patterns to monitor:

```bash
# Successful queries
"IQ agent query completed successfully"

# Performance warnings
"IQ agent query took longer than expected"

# Error patterns
"IQ Agent initialization failed"
"Neo4j connection failed"
"Memory consolidation failed"
```

### Database Maintenance

```bash
# Neo4j maintenance
# 1. Regular backups
neo4j-admin backup --backup-dir=/backups/compliance-graph

# 2. Graph statistics refresh
CALL db.stats.retrieve('COUNT')

# 3. Memory cleanup
CALL apoc.util.cleanupGraphDatabase()

# PostgreSQL maintenance
# 1. Memory table cleanup (weekly)
DELETE FROM compliance_memories 
WHERE created_at < NOW() - INTERVAL '30 days' 
AND importance_score < 0.3;
```

## Troubleshooting

### Common Issues

#### 1. Neo4j Connection Failures

**Symptoms**: 503 errors, "Neo4j connection failed" logs

**Solutions**:
```bash
# Check Neo4j status
docker ps | grep neo4j

# Verify credentials
cypher-shell -u neo4j -p your_password

# Check APOC plugin
CALL dbms.procedures() YIELD name WHERE name STARTS WITH 'apoc'
```

#### 2. Memory Consolidation Errors

**Symptoms**: Growing memory usage, slow query responses

**Solutions**:
```bash
# Manual memory cleanup
POST /api/v1/iq/memory/cleanup

# Check memory statistics
GET /api/v1/iq/health?include_stats=true

# Restart IQ agent if needed
docker restart ruleiq-api
```

#### 3. Rate Limiting Issues

**Symptoms**: 429 errors, slow responses

**Solutions**:
```python
# Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except HTTPException as e:
            if e.status_code == 429:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
```

#### 4. AI Service Timeouts

**Symptoms**: 502 errors, "AI analysis failed" logs

**Solutions**:
- Check API key validity
- Monitor AI service quotas
- Implement circuit breaker pattern
- Use shorter context windows

### Performance Optimization

1. **Query Optimization**:
   ```cypher
   // Create indexes for common queries
   CREATE INDEX compliance_domain_index FOR (d:ComplianceDomain) ON (d.name)
   CREATE INDEX regulation_code_index FOR (r:Regulation) ON (r.code)
   CREATE INDEX requirement_risk_index FOR (req:Requirement) ON (req.risk_level)
   ```

2. **Memory Management**:
   ```python
   # Configure memory limits
   MEMORY_MAX_CONVERSATION_HISTORY=50
   MEMORY_CONSOLIDATION_THRESHOLD=0.9
   MEMORY_CLEANUP_INTERVAL_HOURS=12
   ```

3. **Connection Pooling**:
   ```python
   # Neo4j driver configuration
   NEO4J_MAX_CONNECTION_POOL_SIZE=50
   NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60
   NEO4J_MAX_CONNECTION_LIFETIME=3600
   ```

## Advanced Configuration

### Custom Compliance Domains

Add new compliance domains to the graph:

```cypher
// Add custom domain
CREATE (d:ComplianceDomain {
  name: "Custom Domain",
  description: "Custom compliance requirements",
  risk_level: "medium",
  created_at: datetime()
})

// Link to regulations
MATCH (d:ComplianceDomain {name: "Custom Domain"})
MATCH (r:Regulation {code: "CUSTOM_REG"})
CREATE (d)-[:COVERS]->(r)
```

### Custom Retrieval Queries

Extend the IQ agent with custom analysis queries:

```python
# services/compliance_retrieval_queries.py

class CustomQueryCategory(QueryCategory):
    CUSTOM_ANALYSIS = "custom_analysis"

def execute_custom_compliance_query(
    neo4j_service: Neo4jGraphRAGService,
    query_params: Dict[str, Any]
) -> ComplianceQueryResult:
    """Custom compliance analysis query"""
    
    cypher_query = """
    MATCH (d:ComplianceDomain)-[:COVERS]->(r:Regulation)-[:CONTAINS]->(req:Requirement)
    WHERE d.name = $domain_name
    AND req.custom_field = $custom_value
    RETURN req, r, d
    """
    
    result = await neo4j_service.execute_query(
        cypher_query, 
        query_params
    )
    
    return ComplianceQueryResult(
        data=result,
        metadata={"query_type": "custom_analysis"}
    )
```

### Custom Memory Types

Add specialized memory types:

```python
# services/compliance_memory_manager.py

class CustomMemoryType(MemoryType):
    CUSTOM_INSIGHT = "custom_insight"

def store_custom_memory(
    self,
    content: Dict[str, Any],
    custom_metadata: Dict[str, Any]
) -> str:
    """Store custom memory type"""
    
    memory_node = MemoryNode(
        memory_type=CustomMemoryType.CUSTOM_INSIGHT,
        content=content,
        metadata=custom_metadata,
        importance_score=self._calculate_custom_importance(content)
    )
    
    return self.store_memory(memory_node)
```

### Integration with External Systems

```python
# Example: Slack integration
class SlackComplianceNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_compliance_alert(
        self, 
        risk_level: str, 
        message: str
    ):
        """Send compliance alerts to Slack"""
        
        if risk_level in ["HIGH", "CRITICAL"]:
            payload = {
                "text": f"🚨 Compliance Alert: {message}",
                "channel": "#compliance-alerts"
            }
            
            async with httpx.AsyncClient() as client:
                await client.post(self.webhook_url, json=payload)

# Usage in IQ agent
notifier = SlackComplianceNotifier(os.getenv("SLACK_WEBHOOK_URL"))
await notifier.send_compliance_alert(
    risk_level, 
    "Critical GDPR gap detected"
)
```

## Security Considerations

1. **API Authentication**: Always use JWT tokens
2. **Rate Limiting**: Respect API limits to prevent abuse
3. **Data Encryption**: Sensitive data is encrypted at rest
4. **Access Control**: RBAC controls graph access
5. **Audit Logging**: All queries are logged for compliance

## Support & Community

- **Documentation**: [Internal Wiki](wiki-url)
- **Issue Tracking**: [GitHub Issues](issues-url)
- **Team Chat**: #ruleiq-support on Slack

---

**Next Steps**: After deployment, run the health check endpoints and execute a test compliance query to verify the system is working correctly.