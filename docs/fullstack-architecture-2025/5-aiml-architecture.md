# 5. AI/ML ARCHITECTURE

## 5.1 AI Service Layer

```python
class AIService:
    def __init__(self):
        self.llm = GeminiClient()
        self.embeddings = EmbeddingService()
        self.rag = RAGPipeline()
        self.circuit_breaker = CircuitBreaker()
    
    @with_circuit_breaker
    async def generate_policy(
        self,
        framework: str,
        context: dict
    ) -> PolicyContent:
        # RAG-enhanced generation
        relevant_docs = await self.rag.retrieve(framework)
        
        prompt = self.build_prompt(
            framework=framework,
            context=context,
            examples=relevant_docs
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=8000
        )
        
        return self.parse_policy(response)
```

## 5.2 RAG Pipeline

```yaml
RAG Architecture:
  Embeddings:
    Model: text-embedding-004
    Dimensions: 768
    Storage: pgvector
    
  Retrieval:
    Method: Hybrid (semantic + keyword)
    Reranking: Cross-encoder
    Chunks: 512 tokens with 128 overlap
    
  Generation:
    Model: Gemini 2.5 Pro
    Context: 32K tokens
    Temperature: 0.3 for factual
    
  Quality:
    Hallucination: Fact verification
    Relevance: Cosine similarity > 0.7
    Citations: Source tracking
```

---
