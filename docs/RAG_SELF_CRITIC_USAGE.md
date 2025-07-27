# RAG Self-Critic and Fact-Checking System

## Overview

The RAG Self-Critic system provides comprehensive fact-checking, quality assessment, and self-criticism capabilities for the Agentic RAG system. It ensures response accuracy, reliability, and quality through automated analysis.

## Features

- **Comprehensive Fact-Checking**: Verifies factual claims against source documents
- **Self-Criticism Analysis**: Evaluates response quality across multiple dimensions
- **Quick Fact-Check**: Real-time verification for production use
- **Quality Assessment**: Overall scoring and approval/rejection decisions
- **Benchmark Testing**: Performance evaluation across multiple queries
- **Command-Line Interface**: Easy-to-use CLI for all operations

## System Components

### 1. RAGFactChecker (`services/rag_fact_checker.py`)
Core fact-checking and quality assessment engine with:
- Multi-source fact verification
- Cross-reference validation
- Source reliability assessment
- Response quality scoring
- Automated self-criticism
- Bias detection

### 2. RAGSelfCriticCommands (`services/rag_self_critic.py`)
Command-line interface providing:
- Interactive fact-checking commands
- Batch processing capabilities
- Comprehensive reporting
- JSON output support

## Installation and Setup

### Prerequisites
```bash
# Required API keys in .env file
OPENAI_API_KEY=your-openai-api-key  # Required for LLM-based analysis
MISTRAL_API_KEY=your-mistral-api-key  # Used for embeddings

# Supabase configuration (already configured)
SUPABASE_URL=https://gaqkmdexddnmwzenrjrv.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
POSTGRES_PASSWORD=your-password
```

### Dependencies
All dependencies are already included in the existing ruleIQ environment:
- openai
- mistralai  
- supabase
- pydantic
- sqlalchemy

## Command Usage

### Basic Commands

#### 1. Quick Fact-Check (Real-time)
```bash
python services/rag_self_critic.py quick-check --query "How do I create a StateGraph in LangGraph?"
```
**Output:**
- ✅/⚠️ Approval status
- Response preview
- RAG confidence score
- Fact-check result (PASS/REVIEW NEEDED)

#### 2. Comprehensive Fact-Check
```bash
python services/rag_self_critic.py fact-check --query "What is Pydantic AI?" --max-results 5
```
**Output:**
- Detailed fact-checking analysis
- Individual claim verification
- Source quality assessment
- Flagged issues and recommendations

#### 3. Self-Critique Analysis
```bash
python services/rag_self_critic.py critique --query "How does LangGraph handle state persistence?"
```
**Output:**
- Accuracy assessment (0-1 score)
- Completeness evaluation
- Relevance analysis  
- Clarity rating
- Specific improvement suggestions

#### 4. Full Quality Assessment
```bash
python services/rag_self_critic.py assess --query "Can I use async functions with Pydantic AI?"
```
**Output:**
- Combined fact-check + critique results
- Overall quality score
- Approval/rejection decision
- Comprehensive recommendations

#### 5. Benchmark Testing
```bash
python services/rag_self_critic.py benchmark --num-queries 5
```
**Output:**
- Success rate across multiple queries
- Average processing time
- Average quality scores
- Approval rate statistics

### Advanced Usage

#### Save Results to File
```bash
python services/rag_self_critic.py assess --query "Your question" --output results.json
```

#### Batch Processing with Custom Queries
```bash
# Create a script to process multiple queries
for query in "Query 1" "Query 2" "Query 3"; do
    python services/rag_self_critic.py quick-check --query "$query"
done
```

## Output Interpretation

### Quality Scores
- **0.9-1.0**: Excellent quality, high confidence
- **0.8-0.9**: Good quality, generally reliable
- **0.7-0.8**: Acceptable quality, minor issues
- **0.6-0.7**: Fair quality, needs review
- **Below 0.6**: Poor quality, requires significant improvement

### Confidence Levels
- **HIGH**: Strong evidence supporting the claim
- **MEDIUM**: Reasonable evidence, generally reliable
- **LOW**: Limited evidence, use with caution
- **UNCERTAIN**: Insufficient evidence for verification

### Severity Levels
- **CRITICAL**: Major issues requiring immediate attention
- **HIGH**: Significant problems affecting quality
- **MEDIUM**: Moderate issues worth addressing
- **LOW**: Minor improvements possible
- **INFO**: Informational observations

## Integration Examples

### Python Integration
```python
from services.rag_self_critic import RAGSelfCriticCommands

async def validate_rag_response(query: str):
    critic = RAGSelfCriticCommands()
    await critic.initialize()
    
    # Quick validation for real-time use
    result = await critic.quick_check_command(query)
    
    if result.get("is_reliable"):
        return "approved"
    else:
        # Run comprehensive check for problematic responses
        detailed = await critic.assess_command(query)
        return detailed
```

### API Integration
```python
# Add to FastAPI endpoint
@app.post("/rag/query-with-validation")
async def query_with_validation(query: str):
    # Get RAG response
    rag_response = await rag_system.query_documentation(query)
    
    # Validate response
    critic = RAGSelfCriticCommands()
    await critic.initialize()
    validation = await critic.quick_check_command(query)
    
    return {
        "response": rag_response.answer,
        "validated": validation["is_reliable"],
        "confidence": rag_response.confidence
    }
```

## Performance Considerations

### Processing Times
- **Quick Check**: ~2-5 seconds
- **Fact Check**: ~10-30 seconds  
- **Full Assessment**: ~15-45 seconds
- **Benchmark (5 queries)**: ~1-3 minutes

### Resource Usage
- Uses existing RAG system infrastructure
- OpenAI API calls for LLM analysis
- Minimal additional database overhead
- Efficient caching through existing Redis setup

## Best Practices

### 1. Production Usage
- Use `quick-check` for real-time validation
- Run `assess` for high-stakes responses
- Implement approval thresholds based on use case
- Cache results for repeated queries

### 2. Development Workflow
```bash
# During development
python services/rag_self_critic.py assess --query "Test query"

# Before deployment
python services/rag_self_critic.py benchmark --num-queries 10

# Production monitoring
python services/rag_self_critic.py quick-check --query "User query"
```

### 3. Quality Thresholds
```python
# Recommended thresholds
PRODUCTION_APPROVAL_THRESHOLD = 0.75
HIGH_STAKES_APPROVAL_THRESHOLD = 0.85
QUICK_CHECK_THRESHOLD = True  # Boolean reliability check
```

## Troubleshooting

### Common Issues

#### 1. "OpenAI API key required"
```bash
# Set in .env file
OPENAI_API_KEY=your-actual-api-key
```

#### 2. "Failed to initialize system"
```bash
# Check Supabase connection
python test_supabase_rag.py
```

#### 3. "Fact-checking service unavailable"
- Falls back to conservative defaults
- System continues to function
- Manual review recommended

### Debug Mode
```bash
# Add verbose logging
export LOG_LEVEL=DEBUG
python services/rag_self_critic.py assess --query "Debug query"
```

## Configuration Options

### Environment Variables
```bash
# Fact-checking thresholds
FACT_CHECK_HIGH_CONFIDENCE_THRESHOLD=0.85
FACT_CHECK_MEDIUM_CONFIDENCE_THRESHOLD=0.65
FACT_CHECK_APPROVAL_THRESHOLD=0.75

# Model selection
FACT_CHECK_MODEL=gpt-4o-mini
CRITIC_MODEL=gpt-4o-mini

# Performance tuning
MAX_CLAIMS_TO_CHECK=10
QUICK_CHECK_TIMEOUT=5
COMPREHENSIVE_CHECK_TIMEOUT=60
```

### Custom Configuration
```python
# Modify in rag_fact_checker.py
class RAGFactChecker:
    def __init__(self, custom_thresholds=None):
        self.high_confidence_threshold = custom_thresholds.get('high', 0.85)
        self.medium_confidence_threshold = custom_thresholds.get('medium', 0.65)
        self.approval_threshold = custom_thresholds.get('approval', 0.75)
```

## Future Enhancements

- Multi-language fact-checking support
- Integration with external fact-checking APIs
- Machine learning-based quality prediction
- Real-time monitoring dashboard
- Automated response improvement suggestions
- Confidence calibration based on historical accuracy