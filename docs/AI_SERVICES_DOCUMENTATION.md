# AI Services Documentation

## Overview

This document details the AI services architecture and implementation in ruleIQ, including the assessment AI service, IQ Agent, RAG Self-Critic, and supporting infrastructure.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [AI Assessment Service](#ai-assessment-service)
3. [IQ Agent](#iq-agent)
4. [RAG Self-Critic](#rag-self-critic)
5. [Circuit Breaker Pattern](#circuit-breaker-pattern)
6. [Rate Limiting](#rate-limiting)
7. [Error Handling](#error-handling)
8. [Testing AI Services](#testing-ai-services)

## Architecture Overview

### AI Services Stack

```
┌─────────────────────────────────────────┐
│         Frontend Application            │
├─────────────────────────────────────────┤
│      AI Assessment Service (TS)         │
│    /frontend/lib/api/assessments-ai     │
├─────────────────────────────────────────┤
│         FastAPI Backend                 │
│      /api/routers/ai_assessments        │
├─────────────────────────────────────────┤
│         AI Service Layer                │
│  ├── IQ Agent (GraphRAG)               │
│  ├── RAG Self-Critic                   │
│  └── LLM Service (Multi-provider)      │
├─────────────────────────────────────────┤
│      Infrastructure Layer               │
│  ├── Circuit Breaker                   │
│  ├── Rate Limiter                      │
│  └── Cache (Redis)                     │
├─────────────────────────────────────────┤
│         Data Layer                      │
│  ├── PostgreSQL (State)                │
│  └── Neo4j (Knowledge Graph)           │
└─────────────────────────────────────────┘
```

## AI Assessment Service

### Frontend Implementation

Located in `/frontend/lib/api/assessments-ai.service.ts`

#### Key Features

1. **Intelligent Help System**
   - Context-aware guidance
   - Framework-specific recommendations
   - Confidence scoring

2. **Streaming Responses**
   - Real-time updates
   - Progress tracking
   - Server-sent events

3. **Error Resilience**
   - Automatic retry logic
   - Fallback responses
   - Rate limit handling

#### Service Interface

```typescript
// AI Help Request
interface AIHelpRequest {
  question_id: string;
  question_text: string;
  framework_id: string;
  section_id?: string;
  user_context?: {
    business_profile?: Partial<BusinessProfile>;
    current_answers?: Record<string, any>;
    assessment_progress?: Partial<AssessmentProgress>;
  };
}

// AI Help Response
interface AIHelpResponse {
  guidance: string;
  confidence_score: number;
  related_topics?: string[];
  follow_up_suggestions?: string[];
  source_references?: string[];
}
```

#### Key Methods

```typescript
class AIAssessmentService {
  // Get AI help for a question
  async getHelp(request: AIHelpRequest): Promise<AIHelpResponse>

  // Stream assessment analysis
  async analyzeWithStream(
    assessment: Assessment,
    onUpdate: (update: StreamUpdate) => void
  ): Promise<AnalysisResult>

  // Get follow-up questions
  async getFollowUp(
    request: AIFollowUpRequest
  ): Promise<AIFollowUpResponse>

  // Generate recommendations
  async getRecommendations(
    gaps: Gap[],
    context: BusinessContext
  ): Promise<Recommendation[]>
}
```

### Backend Implementation

Located in `/api/routers/ai_assessments.py`

#### Endpoints

1. **POST /api/v1/ai-assessments/help**
   - Provides intelligent assistance
   - Rate limited: 20 req/min
   - Circuit breaker protected

2. **POST /api/v1/ai-assessments/analyze/stream**
   - Streams analysis results
   - Server-sent events
   - Progress tracking

3. **POST /api/v1/ai-assessments/recommendations**
   - Generates compliance recommendations
   - Priority-based sorting
   - Actionable insights

#### Service Layer

```python
class AIAssessmentService:
    def __init__(self):
        self.llm_service = LLMService()
        self.circuit_breaker = CircuitBreaker()
        self.cache = RedisCache()

    async def generate_guidance(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> AIGuidanceResponse:
        """Generate AI guidance with fallback."""

        # Check cache
        cache_key = self._generate_cache_key(question, context)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Circuit breaker protection
        try:
            response = await self.circuit_breaker.call(
                self.llm_service.generate,
                prompt=self._build_prompt(question, context)
            )
        except CircuitBreakerOpen:
            return self._get_fallback_response(question)

        # Cache successful response
        await self.cache.set(cache_key, response, ttl=3600)
        return response
```

## IQ Agent

### Overview

The IQ Agent is the core intelligence system powered by GraphRAG and LangGraph workflows.

### Architecture

```python
class IQAgent:
    def __init__(self):
        self.neo4j_service = Neo4jService()
        self.langgraph_workflow = ComplianceWorkflow()
        self.memory_manager = MemoryManager()

    async def process_query(
        self,
        query: str,
        session_id: str
    ) -> AgentResponse:
        """Process user query through PPALE loop."""

        # PERCEIVE - Query knowledge graph
        context = await self.neo4j_service.query_context(query)

        # PLAN - Generate action plan
        plan = await self.langgraph_workflow.plan(query, context)

        # ACT - Execute plan
        result = await self.langgraph_workflow.execute(plan)

        # LEARN - Extract patterns
        patterns = await self.memory_manager.extract_patterns(
            query, result
        )

        # REMEMBER - Store in memory
        await self.memory_manager.store(
            session_id, query, result, patterns
        )

        return result
```

### GraphRAG Integration

```python
class GraphRAGEngine:
    def __init__(self):
        self.neo4j = Neo4jConnection()
        self.embeddings = EmbeddingService()

    async def query(
        self,
        question: str,
        max_hops: int = 2
    ) -> KnowledgeContext:
        """Query knowledge graph with RAG."""

        # Generate embeddings
        query_embedding = await self.embeddings.embed(question)

        # Vector similarity search
        similar_nodes = await self.neo4j.vector_search(
            query_embedding,
            limit=10
        )

        # Graph traversal
        context = await self.neo4j.traverse_graph(
            similar_nodes,
            max_hops=max_hops
        )

        return KnowledgeContext(
            nodes=context.nodes,
            relationships=context.relationships,
            confidence=self._calculate_confidence(context)
        )
```

## RAG Self-Critic

### Overview

The RAG Self-Critic validates AI responses to prevent hallucinations and ensure accuracy.

### Implementation

```python
class RAGSelfCritic:
    def __init__(self):
        self.fact_checker = FactChecker()
        self.confidence_threshold = 0.85

    async def validate_response(
        self,
        response: str,
        context: KnowledgeContext
    ) -> ValidationResult:
        """Validate AI response against knowledge base."""

        # Extract claims from response
        claims = await self._extract_claims(response)

        # Verify each claim
        validations = []
        for claim in claims:
            validation = await self.fact_checker.verify(
                claim,
                context
            )
            validations.append(validation)

        # Calculate overall confidence
        confidence = sum(v.confidence for v in validations) / len(validations)

        # Self-critique if below threshold
        if confidence < self.confidence_threshold:
            response = await self._regenerate_response(
                response,
                validations,
                context
            )

        return ValidationResult(
            response=response,
            confidence=confidence,
            validations=validations
        )
```

### Quick Check Mode

```python
async def quick_check(query: str) -> QuickCheckResult:
    """Fast validation for simple queries (2-5 seconds)."""

    # Simplified flow for speed
    context = await graph_rag.quick_query(query)
    response = await llm.generate(query, context, max_tokens=100)
    confidence = await self_critic.quick_validate(response, context)

    return QuickCheckResult(
        response=response,
        confidence=confidence,
        execution_time=time.elapsed()
    )
```

## Circuit Breaker Pattern

### Implementation

```python
class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 30,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset on successful call."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Increment failure count and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
```

## Rate Limiting

### Tiered Rate Limits

```python
RATE_LIMITS = {
    "ai_help": RateLimit(20, timedelta(minutes=1)),
    "ai_analysis": RateLimit(5, timedelta(minutes=1)),
    "ai_recommendations": RateLimit(10, timedelta(minutes=1)),
    "quick_check": RateLimit(30, timedelta(minutes=1)),
    "streaming": RateLimit(3, timedelta(minutes=1))  # Concurrent
}
```

### Implementation

```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_limit(
        self,
        key: str,
        limit: RateLimit,
        user_id: str
    ) -> bool:
        """Check if request is within rate limit."""

        bucket_key = f"rate_limit:{key}:{user_id}"
        current_count = await self.redis.incr(bucket_key)

        if current_count == 1:
            await self.redis.expire(
                bucket_key,
                int(limit.window.total_seconds())
            )

        if current_count > limit.max_requests:
            raise RateLimitExceeded(
                f"Rate limit exceeded: {limit.max_requests} per {limit.window}"
            )

        return True
```

## Error Handling

### Fallback Responses

```python
class FallbackResponseGenerator:
    def __init__(self):
        self.templates = self._load_templates()

    def generate_fallback(
        self,
        question: str,
        error_type: str
    ) -> AIHelpResponse:
        """Generate fallback response when AI services fail."""

        template = self.templates.get(
            error_type,
            self.templates["default"]
        )

        return AIHelpResponse(
            guidance=template.format(question=question),
            confidence_score=0.6,
            is_fallback=True,
            follow_up_suggestions=[
                "Try rephrasing your question",
                "Contact support for assistance",
                "Check our documentation"
            ]
        )
```

### Error Categories

1. **Service Errors**
   - Circuit breaker open
   - LLM provider timeout
   - Network failures

2. **Rate Limit Errors**
   - User quota exceeded
   - Burst limit reached
   - Concurrent request limit

3. **Validation Errors**
   - Low confidence response
   - Failed fact checking
   - Inconsistent output

## Testing AI Services

### Unit Tests

```python
@pytest.mark.unit
@pytest.mark.ai
class TestAIAssessmentService:
    @pytest.fixture
    def mock_llm(self):
        return Mock(spec=LLMService)

    async def test_guidance_generation(self, mock_llm):
        """Test AI guidance generation with mocked LLM."""

        mock_llm.generate.return_value = "Test guidance"
        service = AIAssessmentService(llm_service=mock_llm)

        result = await service.generate_guidance(
            "Test question",
            {"industry": "Technology"}
        )

        assert result.guidance == "Test guidance"
        assert result.confidence_score > 0
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.ai
async def test_ai_help_endpoint():
    """Test AI help endpoint with real services."""

    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/api/v1/ai-assessments/help",
            json={
                "question_id": "q1",
                "question_text": "What is GDPR?",
                "framework_id": "gdpr"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "guidance" in data
        assert data["confidence_score"] > 0.7
```

### Performance Tests

```python
@pytest.mark.performance
@pytest.mark.benchmark
def test_quick_check_performance(benchmark):
    """Benchmark quick check response time."""

    result = benchmark(
        run_quick_check,
        "Simple compliance question"
    )

    # Assert performance requirements
    assert benchmark.stats['mean'] < 5.0  # Average < 5 seconds
    assert benchmark.stats['max'] < 10.0  # Max < 10 seconds
```

## Monitoring & Observability

### Metrics

```python
# Prometheus metrics
ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['service', 'operation']
)

ai_confidence_score = Histogram(
    'ai_confidence_score',
    'AI response confidence scores',
    ['service']
)

circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)',
    ['service']
)
```

### Logging

```python
import structlog

logger = structlog.get_logger()

async def process_ai_request(request):
    logger.info(
        "ai_request_started",
        request_id=request.id,
        service="ai_assessment",
        question_length=len(request.question)
    )

    try:
        result = await generate_response(request)

        logger.info(
            "ai_request_completed",
            request_id=request.id,
            confidence=result.confidence_score,
            response_length=len(result.guidance),
            duration=time.elapsed()
        )

        return result
    except Exception as e:
        logger.error(
            "ai_request_failed",
            request_id=request.id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

## Best Practices

1. **Always use circuit breakers** for external AI service calls
2. **Implement proper fallbacks** for service failures
3. **Cache responses** where appropriate (with TTL)
4. **Monitor confidence scores** and alert on low confidence
5. **Use streaming** for long-running operations
6. **Implement rate limiting** per user and operation type
7. **Log all AI interactions** for audit and improvement
8. **Test with mocked services** in unit tests
9. **Validate responses** with RAG Self-Critic
10. **Track costs** and optimize token usage