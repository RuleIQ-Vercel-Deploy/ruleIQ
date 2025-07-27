"""
FastAPI router for Agentic RAG endpoints
Provides seamless integration with LangGraph and Pydantic AI documentation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

from services.agentic_rag import AgenticRAGSystem, AgenticRAGResponse
from api.dependencies.auth import get_current_user
from api.middleware.rate_limiter import rate_limit
from api.schemas.responses import StandardResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agentic-rag", tags=["Agentic RAG"])

# Request schemas
class DocumentationQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Question about LangGraph or Pydantic AI")
    source_filter: Optional[str] = Field(None, description="Filter by source: 'langgraph', 'pydantic_ai', etc.")
    query_type: str = Field("documentation", description="Type of query: 'documentation', 'code_examples', 'hybrid'")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results to return")

class ProcessDocumentationRequest(BaseModel):
    force_reprocess: bool = Field(False, description="Force reprocessing even if already indexed")

class FrameworkGuidanceRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="Topic to get guidance on")
    framework: str = Field(..., description="Framework: 'langgraph' or 'pydantic_ai'")

# Initialize the RAG system (singleton pattern)
_rag_system = None

def get_rag_system() -> AgenticRAGSystem:
    """Get or create the RAG system instance"""
    global _rag_system
    if _rag_system is None:
        _rag_system = AgenticRAGSystem()
    return _rag_system

@router.post("/query", response_model=StandardResponse[AgenticRAGResponse])
@rate_limit(requests=20, window=60)  # 20 requests per minute
async def query_documentation(
    request: DocumentationQueryRequest,
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """
    Query the agentic RAG system for LangGraph/Pydantic AI documentation
    
    This endpoint provides intelligent access to documentation with:
    - Semantic search with vector embeddings
    - Code example extraction and search
    - Hybrid search combining keywords and vectors
    - Context-aware responses
    """
    try:
        logger.info(f"User {current_user.id} querying RAG: {request.query[:50]}...")
        
        # Validate query type
        valid_types = ["documentation", "code_examples", "hybrid"]
        if request.query_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid query_type. Must be one of: {valid_types}"
            )
        
        # Validate source filter
        if request.source_filter:
            available_sources = await rag_system.get_available_sources()
            if request.source_filter not in available_sources:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid source_filter. Available sources: {available_sources}"
                )
        
        # Perform the query
        result = await rag_system.query_documentation(
            query=request.query,
            source_filter=request.source_filter,
            query_type=request.query_type,
            max_results=request.max_results
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=f"Successfully retrieved {len(result.sources)} relevant sources"
        )
        
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@router.get("/sources", response_model=StandardResponse[List[str]])
async def get_available_sources(
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """Get list of available documentation sources"""
    try:
        sources = await rag_system.get_available_sources()
        return StandardResponse(
            success=True,
            data=sources,
            message=f"Found {len(sources)} available sources"
        )
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@router.get("/statistics", response_model=StandardResponse[Dict[str, Any]])
async def get_framework_statistics(
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """Get statistics about indexed documentation and code examples"""
    try:
        stats = await rag_system.get_framework_statistics()
        return StandardResponse(
            success=True,
            data=stats,
            message="Framework statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/process-documentation")
@rate_limit(requests=2, window=3600)  # 2 requests per hour (processing is expensive)
async def process_documentation(
    request: ProcessDocumentationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """
    Process and index LangGraph and Pydantic AI documentation files
    
    This is a background task that:
    - Reads documentation files from docs/DEPENDENCY_DOCUMENTATION/
    - Chunks content intelligently by sections and code blocks
    - Generates embeddings with optional contextual enhancement
    - Extracts and indexes code examples separately
    - Stores everything in vector database for search
    """
    try:
        # Check if documentation is already processed (unless force reprocess)
        if not request.force_reprocess:
            stats = await rag_system.get_framework_statistics()
            if stats.get('total_chunks', 0) > 0:
                return JSONResponse(
                    content={
                        "success": True,
                        "message": "Documentation already processed. Use force_reprocess=true to reindex.",
                        "data": {"current_stats": stats}
                    }
                )
        
        # Add processing task to background
        background_tasks.add_task(
            _process_documentation_background,
            rag_system,
            current_user.id,
            request.force_reprocess
        )
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Documentation processing started in background. Check /statistics endpoint for progress.",
                "data": {"processing_started": datetime.utcnow().isoformat()}
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting documentation processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

async def _process_documentation_background(
    rag_system: AgenticRAGSystem, 
    user_id: str, 
    force_reprocess: bool
):
    """Background task for processing documentation"""
    try:
        logger.info(f"Starting documentation processing for user {user_id}")
        await rag_system.process_documentation_files()
        logger.info("Documentation processing completed successfully")
    except Exception as e:
        logger.error(f"Background documentation processing failed: {str(e)}")

@router.post("/guidance/{framework}", response_model=StandardResponse[str])
@rate_limit(requests=30, window=60)  # 30 requests per minute
async def get_framework_guidance(
    framework: str,
    request: FrameworkGuidanceRequest,
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """
    Get specific implementation guidance for LangGraph or Pydantic AI
    
    Provides targeted guidance on specific topics like:
    - LangGraph: state management, workflow orchestration, checkpointing
    - Pydantic AI: agent design, trust levels, context accumulation
    """
    try:
        # Validate framework
        valid_frameworks = ["langgraph", "pydantic_ai"]
        if framework not in valid_frameworks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework. Must be one of: {valid_frameworks}"
            )
        
        # Create a specific query for guidance
        guidance_query = f"How do I implement {request.topic} in {framework}? Please provide code examples and best practices."
        
        # Query the RAG system
        result = await rag_system.query_documentation(
            query=guidance_query,
            source_filter=framework,
            query_type="hybrid",  # Use hybrid search for best results
            max_results=3
        )
        
        return StandardResponse(
            success=True,
            data=result.answer,
            message=f"Retrieved {framework} guidance for {request.topic}"
        )
        
    except Exception as e:
        logger.error(f"Error getting framework guidance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get guidance: {str(e)}")

@router.post("/validate-approach", response_model=StandardResponse[str])
@rate_limit(requests=10, window=60)  # 10 requests per minute
async def validate_implementation_approach(
    approach_description: str = Field(..., min_length=10, max_length=2000),
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """
    Validate a technical approach against LangGraph/Pydantic AI best practices
    
    Analyzes your proposed implementation approach and provides:
    - Feedback on alignment with framework best practices
    - Suggestions for improvements
    - Alternative approaches to consider
    - Potential pitfalls to avoid
    """
    try:
        # Create validation query
        validation_query = f"""
        Is this a good approach for LangGraph/Pydantic AI implementation? 
        
        Proposed approach: {approach_description}
        
        Please provide detailed feedback, suggestions for improvement, and any potential issues.
        """
        
        # Query the RAG system with hybrid search for comprehensive coverage
        result = await rag_system.query_documentation(
            query=validation_query,
            source_filter=None,  # Search across all frameworks
            query_type="hybrid",
            max_results=5
        )
        
        return StandardResponse(
            success=True,
            data=result.answer,
            message="Implementation approach validated against framework best practices"
        )
        
    except Exception as e:
        logger.error(f"Error validating approach: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate approach: {str(e)}")

@router.get("/health")
async def health_check(rag_system: AgenticRAGSystem = Depends(get_rag_system)):
    """Health check for the RAG system"""
    try:
        # Check database connectivity
        sources = await rag_system.get_available_sources()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "available_sources": len(sources),
            "capabilities": {
                "contextual_embeddings": rag_system.use_contextual_embeddings,
                "hybrid_search": rag_system.use_hybrid_search,
                "agentic_rag": rag_system.use_agentic_rag,
                "knowledge_graph": rag_system.use_knowledge_graph
            }
        }
        
        return JSONResponse(content=health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Convenience endpoints for common use cases
@router.post("/quick-help", response_model=StandardResponse[str])
@rate_limit(requests=50, window=60)  # 50 requests per minute for quick help
async def quick_help(
    question: str = Field(..., min_length=5, max_length=500),
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """
    Quick help for common LangGraph/Pydantic AI questions
    
    Optimized for fast responses to common questions like:
    - "How do I create a state graph?"
    - "What's the difference between agents and workflows?"
    - "How do I add checkpointing?"
    """
    try:
        # Use documentation query with reduced max_results for speed
        result = await rag_system.query_documentation(
            query=question,
            source_filter=None,
            query_type="documentation",  # Fast documentation search
            max_results=3
        )
        
        return StandardResponse(
            success=True,
            data=result.answer,
            message="Quick help response generated"
        )
        
    except Exception as e:
        logger.error(f"Error in quick help: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick help failed: {str(e)}")

@router.post("/find-examples", response_model=StandardResponse[AgenticRAGResponse])
@rate_limit(requests=20, window=60)  # 20 requests per minute
async def find_code_examples(
    task_description: str = Field(..., min_length=5, max_length=300),
    framework: Optional[str] = Field(None, description="Filter by framework: 'langgraph' or 'pydantic_ai'"),
    current_user = Depends(get_current_user),
    rag_system: AgenticRAGSystem = Depends(get_rag_system)
):
    """
    Find specific code examples for a task
    
    Searches specifically through extracted code examples to find:
    - Implementation patterns for specific tasks
    - Working code snippets you can adapt
    - Examples of best practices in action
    """
    try:
        # Ensure agentic RAG is enabled for code examples
        if not rag_system.use_agentic_rag:
            raise HTTPException(
                status_code=503,
                detail="Code example search requires agentic RAG to be enabled"
            )
        
        # Create task-specific query
        example_query = f"Show me code examples for: {task_description}"
        
        # Search specifically for code examples
        result = await rag_system.query_documentation(
            query=example_query,
            source_filter=framework,
            query_type="code_examples",
            max_results=5
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=f"Found {len(result.sources)} relevant code examples"
        )
        
    except Exception as e:
        logger.error(f"Error finding examples: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to find examples: {str(e)}")

@router.post("/fact-check", 
    response_model=Dict[str, Any],
    summary="Fact-check a RAG response",
    description="Run fact-checking and self-criticism analysis on a RAG response")
async def fact_check_response(
    request: DocumentationQueryRequest,
    quick_check: bool = Query(True, description="Use quick fact-check for faster response"),
    rag_system: AgenticRAGSystem = Depends(get_rag_system),
    current_user: User = Depends(get_current_user)
):
    """
    Fact-check a RAG response using the self-critic system
    
    Args:
        request: The query and optional source filter
        quick_check: Whether to use quick fact-checking (default: True)
        
    Returns:
        Fact-check results with validation and quality scores
    """
    try:
        logger.info(f"Fact-checking request for query: {request.query}")
        
        # Get agentic integration service
        from services.agentic_integration import get_agentic_service
        agentic_service = await get_agentic_service()
        
        # Get RAG response first
        rag_response = await agentic_service.query_documentation(
            query=request.query,
            source_filter=request.source_filter,
            query_type=getattr(request, 'query_type', 'documentation')
        )
        
        # Run fact-checking
        fact_check_result = await agentic_service.fact_check_response(
            response_text=rag_response["answer"],
            sources=rag_response["sources"],
            original_query=request.query,
            quick_check=quick_check
        )
        
        return {
            "success": True,
            "rag_response": rag_response,
            "fact_check": fact_check_result,
            "analysis": {
                "query": request.query,
                "fact_check_type": fact_check_result.get("fact_check_type", "quick"),
                "approved": fact_check_result["approved"],
                "confidence": fact_check_result["confidence"],
                "recommendations": fact_check_result.get("recommendations", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in fact-check endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Fact-checking failed: {str(e)}"
        )

@router.post("/query-with-validation",
    response_model=Dict[str, Any], 
    summary="Query documentation with automatic validation",
    description="Query RAG system with built-in fact-checking and validation")
async def query_with_validation(
    request: DocumentationQueryRequest,
    enable_fact_check: bool = Query(True, description="Enable fact-checking validation"),
    quick_validation: bool = Query(True, description="Use quick validation for better performance"),
    rag_system: AgenticRAGSystem = Depends(get_rag_system),
    current_user: User = Depends(get_current_user)
):
    """
    Query documentation with automatic fact-checking validation
    
    This endpoint combines RAG querying with validation to provide
    high-quality, fact-checked responses suitable for production use.
    
    Args:
        request: The query parameters
        enable_fact_check: Whether to run fact-checking (default: True)
        quick_validation: Use quick validation for better performance (default: True)
        
    Returns:
        RAG response with validation results and trust scores
    """
    try:
        logger.info(f"Validated query request: {request.query}")
        
        # Get agentic integration service
        from services.agentic_integration import get_agentic_service
        agentic_service = await get_agentic_service()
        
        # Query with validation
        result = await agentic_service.query_documentation_with_validation(
            query=request.query,
            source_filter=request.source_filter,
            query_type=getattr(request, 'query_type', 'documentation'),
            enable_fact_check=enable_fact_check,
            quick_validation=quick_validation
        )
        
        return {
            "success": True,
            "query": request.query,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "trust_score": result["trust_score"],
            "approved_for_use": result["approved_for_use"],
            "sources": result["sources"],
            "processing_time": result["processing_time"],
            "validation": result["validation"],
            "metadata": {
                "query_type": result["query_type"],
                "fact_check_enabled": enable_fact_check,
                "validation_type": "quick" if quick_validation else "comprehensive"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in validated query endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validated query failed: {str(e)}"
        )
