# Model Usage Context List - ruleIQ
_Generated: 2025-09-08_

## Summary
Based on comprehensive search of the codebase, here are all model references found with their usage context.

## Primary Models Configuration

### 1. IQ Agent (Main Orchestrator)
- **Current**: Gemini 2.5 Pro (as per user requirement)
- **Location**: `services/iq_agent.py`
- **Temperature**: 0.1 (high precision)
- **Fallback**: "5.1 mini" (as specified by user)
- **Purpose**: Chief Compliance Officer agent, main intelligence orchestration

### 2. Assessment Agent
- **Model**: Gemini 2.5 Flash
- **Locations**: 
  - `services/assessment_agent.py` (lines 301, 373, 781, 965, 1023, 1054)
  - `services/freemium_assessment_service.py` (lines 658, 979, 998, 1027, 1061, 1133, 1305)
- **Purpose**: Quick assessment generation and analysis
- **Context**: Used with circuit breaker pattern for availability checking

### 3. Agentic RAG System
- **Model**: gpt-4o-mini (OpenAI)
- **Location**: `services/agentic_rag.py` (line 100)
- **Purpose**: RAG document retrieval and answer generation
- **Used for**: 
  - Contextual embeddings generation
  - Answer synthesis from retrieved documents
  - Query expansion and refinement

### 4. Policy Generator
- **Primary**: Gemini models (configurable)
- **Fallback**: OpenAI (gpt-4-turbo-preview)
- **Location**: `services/ai/policy_generator.py`
- **Purpose**: Policy document generation
- **Stream endpoint**: Uses gpt-4-turbo-preview for streaming responses

### 5. PydanticAI Framework Agent
- **Model**: gemini-1.5-pro
- **Location**: `services/agents/pydantic_ai_framework.py` (line 64)
- **Purpose**: Compliance agent response generation
- **Note**: Uses older Gemini 1.5 Pro (should potentially be updated to 2.5)

## Cost Management Configurations

### Location: `services/ai/cost_management.py`

#### OpenAI Models (lines 103-112)
- **gpt-4-turbo**: $10.00 per million input tokens
- **gpt-4o**: $5.00 per million input tokens
- **gpt-3.5-turbo**: $0.50 per million input tokens
- **Usage**: Cost tracking and optimization decisions

#### Gemini Models (lines 63-100)
- **gemini-2.5-pro**: Premium model for complex tasks
- **gemini-2.5-flash**: Fast, cost-effective model
- **gemini-2.5-flash-lite**: Ultra-light model for simple tasks
- **Usage**: Primary AI provider with cost optimization

#### Model Recommendations (lines 113-115)
- **Simple tasks**: gemini-2.5-flash-lite, gpt-3.5-turbo
- **Complex tasks**: gemini-2.5-pro, gpt-4-turbo

## Evidence Processing
- **Model**: gemini-2.5-flash
- **Location**: `services/automation/evidence_processor.py` (line 303)
- **Purpose**: AI classification of evidence
- **Metadata**: Tracks AI version for audit trail

## AI Assistant Service
- **Primary**: Gemini models
- **Location**: `services/ai/assistant.py`
- **Functions**:
  - `_generate_gemini_response()` (line 383): Main response generation
  - Response caching with model metadata (line 459)
  - Evidence recommendations (line 581)
  - Policy generation (lines 1378, 1899)
  - Performance metrics tracking (lines 3968-3977)

## Performance Optimizer
- **Models tracked**: gpt-4, gpt-3.5-turbo, gemini-pro, gemini-flash
- **Location**: `services/ai_performance_optimizer.py` (lines 135-136)
- **Quality scores**:
  - gpt-4: 0.95
  - gemini-pro: 0.9
  - gpt-3.5-turbo: 0.85
  - gemini-flash: 0.8

## Embedding Models

### GraphRAG Retriever
- **Import**: `from langchain_openai import OpenAIEmbeddings`
- **Location**: `services/graphrag_retriever.py`
- **Purpose**: Vector embeddings for GraphRAG

### Agentic RAG
- **Options**: 
  - mistral-embed (if USE_MISTRAL_EMBEDDINGS=true)
  - text-embedding-3-small (OpenAI default)
- **Location**: `services/agentic_rag.py` (lines 98-99)

## Database Schema
- **Location**: `database/ai_cost_models.py` (line 110)
- **Field**: `model_family` - Tracks model families (gemini, gpt-4, etc.)

## Frontend References
All frontend references are in `pnpm-lock.yaml` and not actual code usage:
- Package versions (react-grid-layout@1.3.5)
- Build tools (turbo, various @swc packages)
- No actual GPT model usage in frontend code

## Key Findings

### Models Actually in Use:
1. **Gemini 2.5 Pro**: IQ Agent (main orchestrator)
2. **Gemini 2.5 Flash**: Assessment agents, evidence processing
3. **gemini-1.5-pro**: PydanticAI framework (needs update?)
4. **gpt-4o-mini**: Agentic RAG system only
5. **"5.1 mini"**: Specified as fallback by user (exact string)

### Models Referenced but Not Primary:
- **gpt-4-turbo**: Cost tracking, fallback for policy generation
- **gpt-3.5-turbo**: Cost tracking, recommendations for simple tasks
- **OpenAI embeddings**: GraphRAG vector storage

### No Usage Found:
- **GPT-4o**: Only in pnpm-lock.yaml (not in actual code)
- **GPT-3.5**: Only in cost configurations, not actively used

## Recommendations

1. **Update PydanticAI Agent**: Change from gemini-1.5-pro to gemini-2.5-pro for consistency
2. **Clarify "5.1 mini"**: This appears to be a custom model name - needs configuration
3. **Consider migrating RAG**: Move from gpt-4o-mini to Gemini for consistency
4. **Remove unused references**: Clean up cost configs for models not in use

## Circuit Breaker Pattern
Multiple services use `circuit_breaker.is_model_available()` to check model availability:
- Primary check: "gemini-2.5-flash"
- Fallback behavior when models unavailable
- Graceful degradation to rule-based systems