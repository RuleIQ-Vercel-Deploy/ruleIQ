# Phase 3: RAG System Standardization

Replace the complex custom RAG system with standard LangChain components.

## Current Issues to Fix

1. 1200+ lines of custom RAG logic in `langgraph_agent/agents/rag_system.py`
2. Custom DocumentProcessor, DocumentChunk, RetrievalResult classes
3. Manual embedding generation and similarity calculations
4. Complex caching logic

## Required Changes

### File: Create `langgraph_agent/agents/rag_standard.py`

Implement simplified RAG using LangChain:

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import MultiQueryRetriever, EnsembleRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class StandardizedRAG:
    """Simplified RAG system using LangChain components."""
    
    def __init__(
        self, 
        company_id: UUID,
        collection_name: Optional[str] = None
    ):
        """Initialize with standard components."""
        self.company_id = company_id
        self.collection_name = collection_name or f"compliance_{company_id}"
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # Initialize vector store
        self._initialize_vector_store()
        
        # Setup retrievers
        self._setup_retrievers()
        
        # Text splitter for documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info(f"StandardizedRAG initialized for company {company_id}")
    
    def _initialize_vector_store(self):
        """Initialize or load vector store."""
        try:
            # Try to load existing
            self.vector_store = FAISS.load_local(
                f"./vectorstores/{self.collection_name}",
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Loaded existing vector store: {self.collection_name}")
        except:
            # Create new if doesn't exist
            self.vector_store = FAISS.from_texts(
                ["Initialization document"],
                self.embeddings
            )
            logger.info(f"Created new vector store: {self.collection_name}")
    
    def _setup_retrievers(self):
        """Setup retriever pipeline."""
        # Base retriever with high k for reranking
        base_retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": 0.5,
                "k": 20
            }
        )
        
        # Multi-query for query expansion
        from langchain.chat_models import ChatOpenAI
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=llm,
            parser_key="lines"
        )
        
        # Reranking for better relevance
        compressor = CohereRerank(
            model="rerank-english-v2.0",
            top_n=5
        )
        
        self.retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=multi_query_retriever
        )
    
    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add documents to vector store."""
        # Split documents
        texts = []
        metas = []
        
        for i, doc in enumerate(documents):
            chunks = self.text_splitter.split_text(doc)
            texts.extend(chunks)
            
            # Extend metadata for each chunk
            if metadatas and i < len(metadatas):
                chunk_meta = metadatas[i].copy()
                chunk_meta["chunk_index"] = list(range(len(chunks)))
                metas.extend([chunk_meta] * len(chunks))
            else:
                metas.extend([{"company_id": str(self.company_id)}] * len(chunks))
        
        # Add to vector store
        self.vector_store.add_texts(texts, metadatas=metas)
        
        # Save vector store
        self.vector_store.save_local(f"./vectorstores/{self.collection_name}")
        
        logger.info(f"Added {len(texts)} chunks from {len(documents)} documents")
    
    async def retrieve(
        self,
        query: str,
        k: Optional[int] = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents."""
        # Simple retrieval - all complexity handled by LangChain
        docs = await self.retriever.aget_relevant_documents(query)
        
        # Convert to dict format
        results = []
        for doc in docs[:k]:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": doc.metadata.get("relevance_score", 0.0)
            })
        
        logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Simple health check."""
        try:
            # Test retrieval
            test_docs = self.vector_store.similarity_search("test", k=1)
            return {
                "status": "healthy",
                "vector_store": "operational",
                "document_count": self.vector_store.index.ntotal if hasattr(self.vector_store, 'index') else "unknown"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
```

### File: Create adapter `langgraph_agent/agents/rag_adapter.py`

Create adapter to maintain compatibility:

```python
from .rag_system import RAGSystem, DocumentMetadata, DocumentType, DocumentSource
from .rag_standard import StandardizedRAG
import logging

logger = logging.getLogger(__name__)

class RAGAdapter:
    """Adapter to bridge old RAG interface with new standardized implementation."""
    
    def __init__(self, *args, **kwargs):
        # Extract what we need from old interface
        self.memory_manager = kwargs.get('memory_manager')
        company_id = kwargs.get('company_id', uuid4())
        
        # Initialize new standardized RAG
        self.standard_rag = StandardizedRAG(company_id)
        
        logger.info("RAGAdapter initialized - bridging to StandardizedRAG")
    
    async def add_document(
        self,
        file_path: str,
        company_id: UUID,
        title: str,
        document_type: DocumentType,
        source: DocumentSource,
        **kwargs
    ) -> DocumentMetadata:
        """Adapter method for add_document."""
        # Read document
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Prepare metadata
        metadata = {
            "title": title,
            "document_type": document_type.value,
            "source": source.value,
            "company_id": str(company_id),
            **kwargs
        }
        
        # Add to standardized RAG
        await self.standard_rag.add_documents([content], [metadata])
        
        # Return compatible metadata object
        return DocumentMetadata(
            document_id=f"doc_{uuid4()}",
            title=title,
            document_type=document_type,
            source=source,
            content_hash="",
            file_size_bytes=0,
            company_id=company_id,
            processing_status="processed"
        )
    
    async def retrieve_relevant_docs(
        self,
        query: str,
        company_id: UUID,
        k: int = 6,
        **kwargs
    ):
        """Adapter method for retrieval."""
        # Use standardized retrieval
        results = await self.standard_rag.retrieve(query, k)
        
        # Convert to old format
        from .rag_system import RetrievalResult, DocumentChunk, RetrievalStrategy
        
        chunks = []
        for i, result in enumerate(results):
            chunk = DocumentChunk(
                chunk_id=f"chunk_{i}",
                document_id="adapted",
                content=result["content"],
                chunk_index=i,
                start_char=0,
                end_char=len(result["content"]),
                relevance_score=result["score"]
            )
            chunks.append(chunk)
        
        return RetrievalResult(
            chunks=chunks,
            total_results=len(chunks),
            query=query,
            strategy=RetrievalStrategy.HYBRID,
            retrieval_time_ms=100,
            avg_relevance_score=sum(c.relevance_score for c in chunks) / len(chunks) if chunks else 0
        )
```

## Migration Steps

1. Create `StandardizedRAG` class with LangChain components
2. Create `RAGAdapter` for backward compatibility
3. Update imports in existing code to use adapter
4. Test retrieval quality
5. Remove old RAG system once validated

## Testing Requirements

1. Document addition works
2. Retrieval returns relevant results
3. Reranking improves quality
4. Multi-query expansion works
5. Performance is improved

## Success Criteria

- [ ] StandardizedRAG implemented (~200 lines)
- [ ] Adapter maintains compatibility
- [ ] All RAG tests passing
- [ ] Performance improved by >2x
- [ ] Code reduced by >80%
