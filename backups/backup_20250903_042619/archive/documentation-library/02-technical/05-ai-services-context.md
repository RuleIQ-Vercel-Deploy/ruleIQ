# AI Services Context

## Purpose & Responsibility

The AI Services layer provides intelligent compliance automation capabilities for the ruleIQ platform. It integrates Google Gemini AI models to deliver contextual guidance, automated assessment analysis, evidence collection assistance, and policy generation.

## Architecture Overview

### **Service Design Pattern**
- **Pattern**: Layered service architecture with circuit breaker resilience
- **Approach**: Multi-model strategy with intelligent fallback mechanisms
- **Integration**: Centralized ComplianceAssistant with specialized tool modules

### **Current Implementation Status**
- **Development Phase**: Week 1 Day 3 - AI SDK Optimization Project (40+ hours)
- **Progress**: Multi-model strategy implementation in progress
- **Target Outcomes**: 40-60% cost reduction, 80% latency improvement
- **Completion**: Advanced optimization features being implemented

## Dependencies

### **Incoming Dependencies**
- **API Layer**: `/api/routers/ai_assessments.py` - Main AI endpoint routing
- **Assessment Service**: Business logic requesting AI analysis and recommendations
- **Evidence Service**: Automated evidence collection and classification
- **Policy Service**: AI-powered policy document generation
- **Chat Service**: Real-time AI assistance and conversation management

### **Outgoing Dependencies**
- **Google Generative AI SDK**: Primary AI model integration
- **Redis Cache**: Response caching and performance optimization
- **PostgreSQL**: AI interaction logging and analytics storage
- **Circuit Breaker**: Fault tolerance and service degradation
- **Analytics Monitor**: Performance tracking and optimization metrics

## Key Interfaces

### **Public APIs**

#### **Assessment AI Endpoints** (`/api/ai/assessments/*`)
```python
POST /api/ai/assessments/{framework_id}/help
- Purpose: Get AI guidance for specific assessment questions
- Input: Question context, framework, business profile
- Output: Contextual guidance with confidence scores
- Rate Limit: 10 requests/minute with burst allowance

POST /api/ai/assessments/followup
- Purpose: Generate intelligent follow-up questions
- Input: Current assessment responses, business context
- Output: Prioritized follow-up questions with reasoning
- Rate Limit: 5 requests/minute

POST /api/ai/assessments/analysis
- Purpose: Comprehensive assessment result analysis
- Input: Complete assessment results, framework, business profile
- Output: Gaps, recommendations, risk assessment, evidence requirements
- Rate Limit: 3 requests/minute

POST /api/ai/assessments/analysis/stream
- Purpose: Real-time streaming analysis with progress updates
- Input: Assessment results, framework context
- Output: Server-Sent Events with incremental analysis
- Rate Limit: 3 requests/minute

POST /api/ai/assessments/recommendations
- Purpose: Generate personalized implementation recommendations
- Input: Identified gaps, business profile, timeline preferences
- Output: Actionable recommendations with implementation plans
- Rate Limit: 3 requests/minute

POST /api/ai/assessments/recommendations/stream
- Purpose: Streaming recommendation generation
- Input: Assessment gaps, business context
- Output: Real-time recommendation streaming
- Rate Limit: 3 requests/minute
```

#### **Health and Monitoring Endpoints**
```python
GET /api/ai/health
- Purpose: Comprehensive AI service health status
- Output: Circuit breaker states, uptime metrics, incident tracking

GET /api/ai/circuit-breaker/status
- Purpose: Detailed circuit breaker status for all models
- Output: Model-specific circuit states and metrics

POST /api/ai/circuit-breaker/reset
- Purpose: Manual circuit breaker reset for specific models
- Input: Model name to reset
- Output: Reset confirmation and status

GET /api/ai/models/{model_name}/health
- Purpose: Individual model health check
- Output: Model-specific availability and performance metrics

GET /api/ai/rate-limit-stats
- Purpose: Rate limiting statistics and current limits
- Output: Request counts, rate limit status, burst allowances
```

### **Internal Interfaces**

#### **Core AI Service Classes**
```python
class ComplianceAssistant:
    - get_assessment_help(): Question-specific guidance
    - generate_assessment_followup(): Intelligent follow-up questions
    - analyze_assessment_results(): Comprehensive gap analysis
    - analyze_assessment_results_stream(): Streaming analysis
    - get_assessment_recommendations(): Implementation recommendations
    - get_assessment_recommendations_stream(): Streaming recommendations

class CircuitBreaker:
    - call_with_circuit_breaker(): Protected AI service calls
    - is_model_available(): Model availability checking
    - get_health_status(): Overall circuit breaker health
    - reset_circuit(): Manual circuit reset functionality

class PerformanceOptimizer:
    - select_optimal_model(): Dynamic model selection
    - optimize_prompts(): Prompt optimization for efficiency
    - cache_responses(): Intelligent response caching
    - monitor_performance(): Real-time performance tracking
```

#### **Specialized AI Tools**
```python
AssessmentTools:
    - extract_question_context(): Context extraction from questions
    - generate_compliance_guidance(): Regulatory guidance generation
    - analyze_user_responses(): Response pattern analysis

EvidenceTools:
    - classify_evidence_types(): Automated evidence classification
    - extract_control_mappings(): Control framework mapping
    - generate_evidence_requirements(): Missing evidence identification

RegulationTools:
    - map_regulatory_requirements(): Framework requirement mapping
    - identify_compliance_gaps(): Gap identification and prioritization
    - generate_remediation_plans(): Action plan generation
```

## Implementation Context

### **Technology Choices**

#### **Google Generative AI SDK**
- **Current Version**: `google-generativeai>=0.3.0`
- **Models in Use**: 
  - Primary: `gemini-2.5-pro` (high-capability tasks)
  - Secondary: `gemini-2.5-flash` (fast responses)
  - Optimization: `gemini-2.5-flash-8b` (cost-effective)
  - Experimental: `gemma-3-8b-it` (lightweight tasks)

#### **Multi-Model Strategy** (In Development)
```python
MODEL_FALLBACK_CHAIN = [
    ModelType.GEMINI_25_PRO,      # Best capability
    ModelType.GEMINI_25_FLASH,    # Balanced performance
    ModelType.GEMINI_25_FLASH_LIGHT,  # Cost-effective
    ModelType.GEMMA_3             # Lightweight fallback
]

MODEL_METADATA = {
    "gemini-2.5-pro": ModelMetadata(
        cost_score=8.0,           # Higher cost
        speed_score=6.0,          # Moderate speed
        capability_score=10.0,    # Highest capability
        max_tokens=2048000,
        timeout_seconds=30.0
    ),
    "gemini-2.5-flash": ModelMetadata(
        cost_score=4.0,           # Lower cost
        speed_score=9.0,          # High speed
        capability_score=8.5,     # High capability
        max_tokens=1048576,
        timeout_seconds=15.0
    )
}
```

#### **Circuit Breaker Implementation**
- **Pattern**: Circuit breaker per AI model with shared failure tracking
- **Failure Threshold**: 5 consecutive failures trigger open circuit
- **Recovery Timeout**: 60 seconds before attempting recovery
- **Health Monitoring**: Real-time circuit state tracking and alerting

### **Code Organization**

#### **AI Services Directory Structure**
```
/services/ai/
├── __init__.py                    # Service exports
├── assistant.py                   # Main ComplianceAssistant service
├── circuit_breaker.py             # Circuit breaker implementation
├── performance_optimizer.py       # AI optimization logic
├── response_processor.py          # Response parsing and validation
├── prompt_templates.py            # Standardized prompt templates
├── exceptions.py                  # AI-specific exception hierarchy
├── tools.py                      # Shared AI tool utilities
├── assessment_tools.py           # Assessment-specific AI tools
├── evidence_tools.py             # Evidence processing AI tools
├── regulation_tools.py           # Regulatory compliance tools
├── analytics_monitor.py          # Performance analytics
├── health_monitor.py             # Service health tracking
├── retry_handler.py              # Retry logic with exponential backoff
├── response_cache.py             # Intelligent response caching
├── validation_models.py          # Pydantic response validation
└── ai_types.py                   # Type definitions and enums
```

### **Current Optimization Project**

#### **Phase 2.4: Google Gen AI SDK Comprehensive Optimization**
**Timeline**: 40+ hours across Week 1 Day 3-5
**Goals**: 
- 40-60% cost reduction through intelligent model selection
- 80% latency improvement through streaming and optimization
- Enhanced reliability through advanced circuit breaker patterns

#### **Implementation Areas**

##### **Multi-Model Strategy**
```python
# Dynamic model selection based on task complexity
async def select_optimal_model(self, task_type: str, complexity_score: float) -> ModelType:
    if complexity_score > 0.8:
        return ModelType.GEMINI_25_PRO
    elif complexity_score > 0.5:
        return ModelType.GEMINI_25_FLASH
    else:
        return ModelType.GEMINI_25_FLASH_LIGHT
```

##### **Streaming Implementation**
```python
# Real-time response streaming for better UX
async def analyze_assessment_results_stream(
    self, assessment_responses: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    async for chunk in self._stream_ai_response(prompt, context):
        yield self._process_stream_chunk(chunk)
```

##### **Function Calling**
```python
# Structured AI interactions with function calling
tools = [
    {
        "name": "extract_compliance_requirements",
        "description": "Extract compliance requirements from assessment responses",
        "parameters": {
            "type": "object",
            "properties": {
                "framework": {"type": "string"},
                "responses": {"type": "object"}
            }
        }
    }
]
```

##### **Advanced Caching**
```python
# Intelligent caching with context awareness
@cached(ttl=3600, key_builder=lambda *args, **kwargs: 
        f"ai_response:{hash(str(args) + str(kwargs))}")
async def get_cached_ai_response(self, prompt: str, context: dict) -> str:
    return await self._generate_ai_response(prompt, context)
```

## Change Impact Analysis

### **Risk Factors**

#### **High-Risk Areas**
1. **External AI Service Dependency**: Google AI service outages affect core functionality
2. **Model Response Format Changes**: Breaking changes in AI model outputs
3. **Rate Limiting**: Google AI API rate limits affecting user experience
4. **Cost Management**: Unoptimized model usage leading to cost overruns

#### **Breaking Change Potential**
1. **AI Response Schema Changes**: Frontend components expecting specific response formats
2. **Circuit Breaker State Changes**: Service degradation affecting dependent services
3. **Authentication Changes**: Google AI API authentication modifications
4. **Timeout Configuration**: Changes affecting user experience expectations

### **Testing Requirements**

#### **AI-Specific Testing**
- **Model Response Validation**: Ensure responses match expected schemas
- **Circuit Breaker Testing**: Failure scenario simulation and recovery testing
- **Performance Testing**: Response time and throughput measurement
- **Cost Monitoring**: Usage tracking and cost optimization validation
- **Fallback Testing**: Model fallback chain validation

#### **Integration Testing**
- **API Contract Testing**: Ensure AI endpoints match frontend expectations
- **Database Integration**: AI interaction logging and analytics storage
- **Cache Integration**: Response caching effectiveness and invalidation
- **Error Handling**: Comprehensive error scenario coverage

## Current Status

### **Production Readiness**
- **Core Functionality**: ✅ Production ready with comprehensive error handling
- **Performance**: ✅ Optimized with caching and circuit breaker patterns
- **Monitoring**: ✅ Health checks and analytics in place
- **Testing**: ✅ 26 AI-specific tests covering all major scenarios

### **Optimization Progress** (Week 1 Day 3)
- **Multi-Model Strategy**: 🔄 Implementation in progress
- **Streaming Responses**: 🔄 Server-sent events implementation ongoing
- **Function Calling**: 🔄 Structured interaction patterns being added
- **Advanced Caching**: 🔄 Context-aware caching optimization in development
- **Performance Monitoring**: 🔄 Enhanced analytics and optimization metrics

### **Known Issues**

#### **Current Limitations**
1. **Single Model Usage**: Currently using one model for all tasks
2. **Blocking Responses**: 15-30 second response times without streaming
3. **Basic Caching**: Simple TTL-based caching without context awareness
4. **Limited Structured Output**: Basic parsing instead of schema validation

#### **Technical Debt**
1. **Hardcoded Configuration**: Model selection criteria should be configurable
2. **Error Message Exposure**: Internal AI service details leaked in error responses
3. **Mock Fallback Methods**: Placeholder implementations need completion
4. **Circuit Breaker Configuration**: Should be environment-specific

### **Planned Improvements**

#### **Week 1 Completion**
- Complete multi-model strategy implementation
- Finish streaming response implementation
- Add comprehensive function calling capabilities
- Implement advanced caching with context awareness

#### **Future Enhancements**
- **Model Fine-tuning**: Custom model training for compliance-specific tasks
- **Prompt Optimization**: A/B testing for prompt effectiveness
- **Advanced Analytics**: Machine learning-based usage optimization
- **Compliance Validation**: Regulatory requirement validation for AI responses

---

**Document Metadata**
- Created: 2025-01-07
- Version: 1.0.0
- Authors: AI Assistant
- Review Status: Initial Draft
- Next Review: 2025-01-10 (Active development area)
- Dependencies: AI_CONTEXT.md, ARCHITECTURE_CONTEXT.md
- Change Impact: High - active development component
- Related Files: services/ai/*, api/routers/ai_assessments.py