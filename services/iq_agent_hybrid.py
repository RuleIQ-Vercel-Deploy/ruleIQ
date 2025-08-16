"""
Hybrid IQ Agent combining structured workflow with ReAct capabilities.

This module enhances the IQ Agent with dynamic ReAct reasoning while
maintaining the structured compliance workflow for formal assessments.
"""

from typing import Dict, List, Optional, Any, Literal
from enum import Enum

from services.iq_agent import IQComplianceAgent
from services.assessment_agent_react import ReActAssessmentAgent, ComplianceTools
from config.logging_config import get_logger

logger = get_logger(__name__)


class QueryType(Enum):
    """Types of queries that determine processing mode."""
    STRUCTURED_ASSESSMENT = "structured"  # Full compliance assessment
    EXPLORATORY = "exploratory"  # Research and discovery
    QUICK_ANSWER = "quick"  # Simple Q&A
    EVIDENCE_CHECK = "evidence"  # Document verification
    RISK_ANALYSIS = "risk"  # Risk assessment


class HybridIQAgent(IQComplianceAgent):
    """
    Enhanced IQ Agent that combines:
    1. Structured PPALMR workflow for formal assessments
    2. ReAct architecture for dynamic problem-solving
    3. Intelligent routing based on query type
    """
    
    def __init__(self, neo4j_service, postgres_session=None, llm_model="gpt-4"):
        # Initialize parent IQ Agent
        super().__init__(neo4j_service, postgres_session, llm_model)
        
        # Initialize ReAct components
        self.react_agent = ReActAssessmentAgent(
            neo4j_service=neo4j_service,
            postgres_session=postgres_session,
            model_name=llm_model
        )
        
        # Query classifier
        self.query_classifier = self._create_query_classifier()
        
        logger.info("Hybrid IQ Agent initialized with structured + ReAct capabilities")
    
    def _create_query_classifier(self):
        """Create a classifier to determine query type."""
        return {
            "keywords": {
                QueryType.STRUCTURED_ASSESSMENT: [
                    "assessment", "audit", "full review", "compliance check",
                    "evaluate", "comprehensive", "analyze our compliance"
                ],
                QueryType.EXPLORATORY: [
                    "what if", "how about", "explore", "research", "tell me about",
                    "explain", "what are the options", "alternatives"
                ],
                QueryType.QUICK_ANSWER: [
                    "what is", "define", "meaning of", "quick question",
                    "simple", "just tell me"
                ],
                QueryType.EVIDENCE_CHECK: [
                    "do we have", "check documents", "evidence for",
                    "proof of", "documentation", "certificates"
                ],
                QueryType.RISK_ANALYSIS: [
                    "risk", "threat", "vulnerability", "exposure",
                    "what could go wrong", "potential issues"
                ]
            }
        }
    
    async def process_intelligent_query(
        self,
        user_query: str,
        business_profile_id: Optional[str] = None,
        mode: Optional[Literal["auto", "structured", "react"]] = "auto",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process query using the most appropriate method.
        
        Args:
            user_query: The user's question or request
            business_profile_id: Optional business profile ID
            mode: Processing mode (auto-detect, structured, or react)
            session_id: Optional session ID for tracking
            
        Returns:
            Response with reasoning, recommendations, and metadata
        """
        try:
            # Determine processing mode
            if mode == "auto":
                query_type = self._classify_query(user_query)
                logger.info(f"Query classified as: {query_type.value}")
            elif mode == "structured":
                query_type = QueryType.STRUCTURED_ASSESSMENT
            else:  # react
                query_type = QueryType.EXPLORATORY
            
            # Route to appropriate processor
            if query_type == QueryType.STRUCTURED_ASSESSMENT:
                # Use structured PPALMR workflow
                result = await self._process_structured(
                    user_query, business_profile_id, session_id
                )
            elif query_type in [QueryType.EXPLORATORY, QueryType.RISK_ANALYSIS]:
                # Use ReAct for dynamic reasoning
                result = await self._process_with_react(
                    user_query, business_profile_id, session_id, query_type
                )
            elif query_type == QueryType.EVIDENCE_CHECK:
                # Quick evidence verification
                result = await self._check_evidence_quick(
                    user_query, business_profile_id
                )
            else:  # QUICK_ANSWER
                # Simple LLM response with context
                result = await self._process_quick_answer(user_query)
            
            # Add metadata
            result["processing_mode"] = query_type.value
            result["hybrid_version"] = "1.0"
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid processing failed: {e}")
            # Fallback to parent IQ Agent
            return await super().process_query(user_query)
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify the query type based on content."""
        query_lower = query.lower()
        
        # Check keywords for each type
        scores = {}
        for query_type, keywords in self.query_classifier["keywords"].items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[query_type] = score
        
        # Return type with highest score, default to exploratory
        if max(scores.values()) == 0:
            return QueryType.EXPLORATORY
        
        return max(scores, key=scores.get)
    
    async def _process_structured(
        self,
        query: str,
        business_profile_id: Optional[str],
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Process using structured PPALMR workflow."""
        logger.info("Using structured PPALMR workflow")
        
        if business_profile_id:
            # Use context-aware processing
            result = await self.process_query_with_context(
                user_query=query,
                business_profile_id=business_profile_id
            )
        else:
            # Standard processing
            result = await self.process_query(query)
        
        result["reasoning_method"] = "PPALMR (Perceive-Plan-Act-Learn-Memory-Respond)"
        return result
    
    async def _process_with_react(
        self,
        query: str,
        business_profile_id: Optional[str],
        session_id: Optional[str],
        query_type: QueryType
    ) -> Dict[str, Any]:
        """Process using ReAct architecture."""
        logger.info("Using ReAct reasoning architecture")
        
        # Get business context if available
        business_context = None
        if business_profile_id and self.has_postgres_access:
            try:
                business_context = await self.retrieve_business_context(
                    business_profile_id
                )
            except Exception as e:
                logger.warning(f"Could not retrieve business context: {e}")
        
        # Use ReAct agent
        result = await self.react_agent.conduct_assessment(
            user_query=query,
            business_context=business_context,
            session_id=session_id or f"hybrid_{query_type.value}"
        )
        
        result["reasoning_method"] = "ReAct (Reasoning and Acting)"
        return result
    
    async def _check_evidence_quick(
        self,
        query: str,
        business_profile_id: Optional[str]
    ) -> Dict[str, Any]:
        """Quick evidence availability check."""
        if not business_profile_id or not self.has_postgres_access:
            return {
                "status": "error",
                "message": "Business profile ID required for evidence check",
                "reasoning_method": "direct_check"
            }
        
        # Extract what evidence they're asking about
        # Simple keyword extraction for now
        evidence_keywords = ["policy", "certificate", "audit", "report", "document"]
        requested_evidence = [kw for kw in evidence_keywords if kw in query.lower()]
        
        if not requested_evidence:
            requested_evidence = ["general documents"]
        
        # Use the React tool directly
        tools = ComplianceTools(self.neo4j, self.postgres_session)
        
        results = {}
        for requirement in requested_evidence:
            result = await tools.check_evidence_availability(
                business_id=business_profile_id,
                requirement=requirement
            )
            results[requirement] = result
        
        return {
            "status": "success",
            "evidence_check": results,
            "reasoning_method": "direct_evidence_check",
            "summary": self._summarize_evidence_results(results)
        }
    
    async def _process_quick_answer(self, query: str) -> Dict[str, Any]:
        """Process simple questions with minimal overhead."""
        logger.info("Processing quick answer")
        
        # Use LLM directly with system context
        prompt = f"""As IQ, the ruleIQ compliance assistant, provide a brief, accurate answer.

Question: {query}

Focus on UK compliance frameworks (GDPR, DPA 2018, ISO 27001, Cyber Essentials).
Keep the response concise and actionable."""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return {
                "status": "success",
                "answer": response.content,
                "reasoning_method": "direct_llm",
                "response_type": "quick_answer"
            }
        except Exception as e:
            logger.error(f"Quick answer failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "reasoning_method": "direct_llm"
            }
    
    def _summarize_evidence_results(self, results: Dict) -> str:
        """Summarize evidence check results."""
        available = []
        missing = []
        
        for doc_type, result in results.items():
            if result.get("has_evidence"):
                count = result.get("evidence_count", 0)
                available.append(f"{doc_type} ({count} document{'s' if count != 1 else ''})")
            else:
                missing.append(doc_type)
        
        summary = []
        if available:
            summary.append(f"✅ Available: {', '.join(available)}")
        if missing:
            summary.append(f"❌ Missing: {', '.join(missing)}")
        
        return " | ".join(summary) if summary else "No evidence information available"
    
    async def adaptive_conversation(
        self,
        conversation_history: List[Dict[str, str]],
        business_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle multi-turn conversations with adaptive mode switching.
        
        The agent can switch between structured and ReAct modes based on
        the conversation flow and user needs.
        """
        # Analyze conversation trajectory
        if len(conversation_history) < 3:
            # Early in conversation - use exploratory ReAct
            mode = "react"
        elif any("assess" in msg.get("content", "").lower() 
                for msg in conversation_history[-3:]):
            # Recent assessment request - use structured
            mode = "structured"
        else:
            # Let the system decide
            mode = "auto"
        
        # Get latest user message
        latest_query = conversation_history[-1].get("content", "")
        
        # Process with determined mode
        result = await self.process_intelligent_query(
            user_query=latest_query,
            business_profile_id=business_profile_id,
            mode=mode
        )
        
        # Add conversation context
        result["conversation_length"] = len(conversation_history)
        result["adaptive_mode"] = mode
        
        return result


# Example usage
async def demo_hybrid_agent():
    """Demonstrate hybrid agent capabilities."""
    from services.neo4j_service import Neo4jGraphRAGService
    from database.session import get_db
    
    neo4j = Neo4jGraphRAGService()
    async with get_db() as db:
        agent = HybridIQAgent(neo4j, db)
        
        # Example 1: Exploratory query (uses ReAct)
        result1 = await agent.process_intelligent_query(
            "What are the different approaches to GDPR compliance for startups?",
            mode="auto"
        )
        print(f"Exploratory result: {result1['reasoning_method']}")
        
        # Example 2: Structured assessment (uses PPALMR)
        result2 = await agent.process_intelligent_query(
            "Conduct a full compliance assessment for our fintech startup",
            mode="auto"
        )
        print(f"Assessment result: {result2['reasoning_method']}")
        
        # Example 3: Quick evidence check
        result3 = await agent.process_intelligent_query(
            "Do we have privacy policy documentation?",
            business_profile_id="test-id",
            mode="auto"
        )
        print(f"Evidence check: {result3['reasoning_method']}")
        
        return [result1, result2, result3]


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_hybrid_agent())