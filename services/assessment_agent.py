"""
Assessment Agent using LangGraph for conversational compliance assessments.

This module implements a stateful, conversational assessment agent that:
1. Maintains context throughout the assessment
2. Generates questions dynamically based on previous answers
3. Adapts difficulty and depth based on user expertise
4. Builds a compliance profile progressively

LangSmith tracing is integrated for observability:
- Set LANGCHAIN_TRACING_V2=true
- Set LANGCHAIN_API_KEY=your_api_key
- Set LANGCHAIN_PROJECT=ruleiq-assessment
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict, Annotated

from langgraph.graph import StateGraph, add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import traceable

from services.ai.assistant import ComplianceAssistant
from services.ai.circuit_breaker import AICircuitBreaker
from services.agents.assessment_services import (
    AssessmentContextAnalyzer,
    CompositeQuestionGenerator,
    AIQuestionGenerator,
    FallbackQuestionGenerator,
    StandardComplianceScorer,
    AssessmentRecommendationService,
    AssessmentProgressManager,
    AssessmentState,
    AssessmentPhase,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


# Import assessment state and phase from the new services module
# These are now defined in assessment_services.py following SOLID principles


class LangGraphAssessmentState(TypedDict):
    """
    LangGraph-specific state wrapper for the assessment agent.
    Extends the base AssessmentState with LangGraph requirements.
    """

    # Conversation history (LangGraph specific)
    messages: Annotated[List[Any], add_messages]

    # Core assessment state (serializable dict instead of AssessmentState object)
    assessment_state: Dict[str, Any]

    # LangGraph specific fields
    thread_id: str


def assessment_state_to_dict(state: AssessmentState) -> Dict[str, Any]:
    """Convert AssessmentState object to serializable dictionary."""
    return {
        "session_id": state.session_id,
        "lead_id": state.lead_id,
        "thread_id": state.thread_id,
        "current_phase": state.current_phase.value
        if hasattr(state.current_phase, "value")
        else state.current_phase,
        "questions_asked": state.questions_asked,
        "questions_answered": state.questions_answered,
        "total_questions_planned": state.total_questions_planned,
        "business_profile": state.business_profile,
        "compliance_needs": state.compliance_needs,
        "identified_risks": state.identified_risks,
        "next_question_context": state.next_question_context,
        "follow_up_needed": state.follow_up_needed,
        "expertise_level": state.expertise_level,
        "compliance_score": state.compliance_score,
        "risk_level": state.risk_level,
        "recommendations": state.recommendations,
        "gaps_identified": state.gaps_identified,
        "should_continue": state.should_continue,
        "error_count": state.error_count,
        "fallback_mode": state.fallback_mode,
    }


def dict_to_assessment_state(data: Dict[str, Any]) -> AssessmentState:
    """Convert dictionary back to AssessmentState object."""
    from services.agents.assessment_services import AssessmentPhase, AssessmentState

    state = AssessmentState(data["session_id"], data["lead_id"])
    state.thread_id = data.get("thread_id", f"thread_{data['session_id']}")
    state.current_phase = AssessmentPhase(data.get("current_phase", "introduction"))
    state.questions_asked = data.get("questions_asked", [])
    state.questions_answered = data.get("questions_answered", 0)
    state.total_questions_planned = data.get("total_questions_planned", 5)
    state.business_profile = data.get("business_profile", {})
    state.compliance_needs = data.get("compliance_needs", [])
    state.identified_risks = data.get("identified_risks", [])
    state.next_question_context = data.get("next_question_context", {})
    state.follow_up_needed = data.get("follow_up_needed", False)
    state.expertise_level = data.get("expertise_level", "intermediate")
    state.compliance_score = data.get("compliance_score", 0.0)
    state.risk_level = data.get("risk_level", "unknown")
    state.recommendations = data.get("recommendations", [])
    state.gaps_identified = data.get("gaps_identified", [])
    state.should_continue = data.get("should_continue", True)
    state.error_count = data.get("error_count", 0)
    state.fallback_mode = data.get("fallback_mode", False)
    return state


class AssessmentAgent:
    """
    LangGraph-based conversational assessment agent.

    Refactored to follow SOLID principles with dependency injection
    of specialized assessment services.
    """

    def __init__(
        self,
        db_session,
        context_analyzer: Optional[AssessmentContextAnalyzer] = None,
        question_generator: Optional[CompositeQuestionGenerator] = None,
        compliance_scorer: Optional[StandardComplianceScorer] = None,
        recommendation_service: Optional[AssessmentRecommendationService] = None,
        progress_manager: Optional[AssessmentProgressManager] = None,
    ) -> None:
        self.db = db_session
        self.assistant = ComplianceAssistant(db_session)
        self.circuit_breaker = AICircuitBreaker()

        # Use PostgreSQL checkpointer for persistent state across requests
        # Following LangGraph best practices for PostgreSQL configuration
        try:
            from langgraph_checkpoint_postgres import PostgresSaver
            import psycopg
            from psycopg.rows import dict_row
            import os

            database_url = os.getenv("DATABASE_URL")
            if database_url:
                # Replace asyncpg with psycopg for PostgresSaver compatibility
                if "asyncpg" in database_url:
                    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

                try:
                    # Create PostgreSQL connection with required configuration
                    # autocommit=True is critical for checkpointer operations
                    # row_factory=dict_row ensures proper data format
                    conn = psycopg.connect(database_url, autocommit=True, row_factory=dict_row)

                    # Initialize PostgresSaver with properly configured connection
                    self.checkpointer = PostgresSaver(conn)

                    # Critical: Call setup() to create checkpoint tables if they don't exist
                    # This is essential for state persistence to work properly
                    self.checkpointer.setup()

                    logger.info(
                        "PostgreSQL checkpointer initialized successfully with autocommit and dict_row",
                        extra={
                            "database_url_prefix": database_url[:30] + "...",
                            "autocommit": True,
                            "row_factory": "dict_row",
                            "setup_called": True,
                        },
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to initialize PostgreSQL checkpointer: {type(e).__name__}: {str(e)}",
                        exc_info=True,
                        extra={
                            "database_url_prefix": database_url[:30] + "..."
                            if database_url
                            else None,
                            "error_type": type(e).__name__,
                            "fallback": "MemorySaver",
                        },
                    )
                    # Fallback to MemorySaver only if PostgreSQL setup fails
                    from langgraph.checkpoint.memory import MemorySaver

                    self.checkpointer = MemorySaver()
            else:
                logger.warning(
                    "No DATABASE_URL found, using MemorySaver (state will not persist)",
                    extra={"checkpointer_type": "MemorySaver", "persistence": False},
                )
                from langgraph.checkpoint.memory import MemorySaver

                self.checkpointer = MemorySaver()

        except ImportError as e:
            logger.warning(
                f"PostgreSQL checkpointer not available: {e}. Using MemorySaver fallback",
                extra={
                    "checkpointer_type": "MemorySaver",
                    "persistence": False,
                    "reason": "import_error",
                },
            )
            from langgraph.checkpoint.memory import MemorySaver

            self.checkpointer = MemorySaver()

        # Configuration
        self.MIN_QUESTIONS = 5
        self.MAX_QUESTIONS = 12
        self.CONFIDENCE_THRESHOLD = 0.7

        # Inject specialized services or create defaults
        self.context_analyzer = context_analyzer or AssessmentContextAnalyzer(
            self.assistant, self.circuit_breaker
        )
        self.question_generator = question_generator or CompositeQuestionGenerator(
            ai_generator=AIQuestionGenerator(self.assistant, self.circuit_breaker),
            fallback_generator=FallbackQuestionGenerator(),
        )
        self.compliance_scorer = compliance_scorer or StandardComplianceScorer()
        self.recommendation_service = recommendation_service or AssessmentRecommendationService(
            self.assistant, self.circuit_breaker
        )
        self.progress_manager = progress_manager or AssessmentProgressManager()

        # Build the LangGraph workflow
        self._build_graph()

    def _configure_tracing(self) -> None:
        """Configure LangSmith tracing for observability."""
        # Check if tracing is enabled via environment variables
        tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

        if tracing_enabled:
            # Ensure required environment variables are set
            api_key = os.getenv("LANGCHAIN_API_KEY")
            project = os.getenv("LANGCHAIN_PROJECT", "ruleiq-assessment")

            if not api_key:
                logger.warning("LANGCHAIN_TRACING_V2 is enabled but LANGCHAIN_API_KEY is not set")
                return

            # Set project name if not already set
            os.environ["LANGCHAIN_PROJECT"] = project

            logger.info(f"LangSmith tracing enabled for project: {project}")
            logger.info("Traces will be available at: https://smith.langchain.com")
        else:
            logger.debug("LangSmith tracing is disabled. Set LANGCHAIN_TRACING_V2=true to enable.")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph with production hardening.

        Includes circuit breaker integration and performance optimizations
        for production stability and loop prevention.
        """
        graph = StateGraph(LangGraphAssessmentState)

        # Add nodes for each phase with circuit breaker protection
        graph.add_node("introduction", self._introduction_node)
        graph.add_node("analyze_context", self._analyze_context_node)
        graph.add_node("generate_question", self._circuit_breaker_protected_question_node)
        graph.add_node("process_answer", self._process_answer_node)
        graph.add_node("determine_next", self._determine_next_node)
        graph.add_node("generate_results", self._generate_results_node)
        graph.add_node("completion", self._completion_node)
        graph.add_node("error", self._error_node)  # Dedicated error handling node

        # Define edges with error handling
        graph.set_entry_point("introduction")

        graph.add_edge("introduction", "generate_question")
        graph.add_edge("generate_question", "process_answer")
        graph.add_edge("process_answer", "analyze_context")
        graph.add_edge("analyze_context", "determine_next")

        # Enhanced conditional routing with error handling
        graph.add_conditional_edges(
            "determine_next",
            self._route_next_step,
            {
                "continue": "generate_question",
                "complete": "generate_results",
                "error": "error",  # Route to dedicated error node
            },
        )

        graph.add_edge("generate_results", "completion")
        graph.add_edge("error", "completion")  # Error node leads to completion

        # Compile with checkpointer for state persistence
        self.workflow = graph.compile(checkpointer=self.checkpointer)

        # Also set the app attribute that other methods expect
        self.app = self.workflow

        logger.info(
            "LangGraph workflow compiled with production hardening",
            extra={
                "checkpointer_type": type(self.checkpointer).__name__,
                "nodes_count": len(graph.nodes),
                "circuit_breaker_enabled": True,
                "error_handling": "enhanced",
            },
        )

        return graph

    async def _introduction_node(self, state: LangGraphAssessmentState) -> LangGraphAssessmentState:
        """Initialize the assessment with a friendly introduction."""
        intro_message = AIMessage(
            content="""
Hello! I'm IQ, your AI compliance assistant. I'm here to help you understand your compliance needs
and identify areas where we can strengthen your compliance posture.

This assessment will be conversational - I'll ask you questions about your business and compliance
practices, and based on your answers, I'll tailor my follow-up questions to get a complete picture
of your needs.

Let's start with understanding your business context. What type of business do you operate, and
what's your primary industry?
        """
        )

        state["messages"].append(intro_message)

        # Update assessment state (convert dict to object, modify, convert back)
        assessment_state = dict_to_assessment_state(state["assessment_state"])
        assessment_state.current_phase = AssessmentPhase.BUSINESS_CONTEXT
        assessment_state.questions_asked.append("business_type_and_industry")
        state["assessment_state"] = assessment_state_to_dict(assessment_state)

        return state

    async def _analyze_context_node(
        self, state: LangGraphAssessmentState
    ) -> LangGraphAssessmentState:
        """Analyze accumulated context to understand the business better."""
        # Extract insights from conversation so far
        messages = state["messages"]
        assessment_state = dict_to_assessment_state(state["assessment_state"])

        # Use the injected context analyzer service
        analysis = await self.context_analyzer.analyze_conversation_context(
            messages=messages[-10:],  # Last 10 messages for context
            business_profile=assessment_state.business_profile,
            fallback_mode=assessment_state.fallback_mode,
        )

        # Update assessment state with analysis results
        assessment_state.business_profile.update(analysis.get("insights", {}))

        # Identify compliance needs
        new_needs = analysis.get("compliance_needs", [])
        for need in new_needs:
            if need not in assessment_state.compliance_needs:
                assessment_state.compliance_needs.append(need)

        # Update expertise level and follow-up status
        assessment_state.expertise_level = analysis.get("expertise_level", "intermediate")
        assessment_state.follow_up_needed = analysis.get("follow_up_needed", False)

        # Convert back to dictionary for serialization
        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    @traceable(
        name="generate_question",
        tags=["node", "question_generation"],
        metadata={"node_type": "question_generator"},
    )
    async def _generate_question_node(
        self, state: LangGraphAssessmentState
    ) -> LangGraphAssessmentState:
        """
        Generate the next question with comprehensive loop prevention.

        Addresses the critical issue: "the ai is creating the same question over and over again"
        """
        messages = state["messages"]
        assessment_state = dict_to_assessment_state(state["assessment_state"])

        # Enhanced tracing metadata for debugging repetitive questions
        questions_asked = assessment_state.questions_asked
        questions_answered = assessment_state.questions_answered
        current_phase = assessment_state.current_phase.value

        logger.info(
            f"Generating question - Phase: {current_phase}, Asked: {len(questions_asked)}, Answered: {questions_answered}",
            extra={
                "questions_asked": questions_asked,
                "questions_answered": questions_answered,
                "current_phase": current_phase,
                "messages_count": len(messages),
                "thread_id": state["thread_id"],
            },
        )

        # Multi-level anti-loop detection system

        # Level 1: Check for immediate repetition (identical consecutive AI messages)
        if len(messages) >= 2:
            last_ai_messages = [
                msg for msg in messages[-4:] if hasattr(msg, "role") and msg.role == "assistant"
            ]
            if len(last_ai_messages) >= 2:
                last_content = last_ai_messages[-1].content if last_ai_messages else ""
                prev_content = last_ai_messages[-2].content if len(last_ai_messages) > 1 else ""

                if last_content == prev_content and last_content:
                    logger.warning(
                        "Level 1: Identical question repetition detected - forcing completion",
                        extra={
                            "repeated_question": last_content[:100],
                            "thread_id": state["thread_id"],
                            "detection_level": "immediate_repetition",
                        },
                    )
                    assessment_state.current_phase = AssessmentPhase.COMPLETION
                    state["assessment_state"] = assessment_state_to_dict(assessment_state)
                    return state

        # Level 2: Check for similar questions (fuzzy matching)
        if len(messages) >= 6:
            recent_ai_content = [
                msg.content
                for msg in messages[-6:]
                if hasattr(msg, "role") and msg.role == "assistant" and msg.content
            ]

            if len(recent_ai_content) >= 3:
                # Simple similarity check - same first 50 characters
                latest = recent_ai_content[-1][:50].lower() if recent_ai_content else ""
                similar_count = sum(
                    1
                    for content in recent_ai_content[:-1]
                    if content[:50].lower() == latest and latest
                )

                if similar_count >= 2:  # Same question pattern repeated 3+ times
                    logger.warning(
                        f"Level 2: Similar question pattern detected ({similar_count + 1} occurrences) - forcing completion",
                        extra={
                            "question_pattern": latest,
                            "occurrence_count": similar_count + 1,
                            "thread_id": state["thread_id"],
                            "detection_level": "pattern_repetition",
                        },
                    )
                    assessment_state.current_phase = AssessmentPhase.COMPLETION
                    state["assessment_state"] = assessment_state_to_dict(assessment_state)
                    return state

        # Level 3: Check for excessive question generation without answers
        unanswered_questions = len(questions_asked) - questions_answered
        if unanswered_questions >= 3:  # Too many unanswered questions
            logger.warning(
                f"Level 3: Too many unanswered questions ({unanswered_questions}) - forcing completion",
                extra={
                    "unanswered_count": unanswered_questions,
                    "questions_asked": len(questions_asked),
                    "questions_answered": questions_answered,
                    "thread_id": state["thread_id"],
                    "detection_level": "unanswered_accumulation",
                },
            )
            assessment_state.current_phase = AssessmentPhase.COMPLETION
            state["assessment_state"] = assessment_state_to_dict(assessment_state)
            return state

        # Level 4: Check maximum question limit with safety margin
        if len(questions_asked) >= self.MAX_QUESTIONS - 1:  # Safety margin of 1
            logger.info(
                f"Level 4: Approaching maximum questions ({len(questions_asked)}/{self.MAX_QUESTIONS}) - forcing completion",
                extra={
                    "questions_asked": len(questions_asked),
                    "max_questions": self.MAX_QUESTIONS,
                    "thread_id": state["thread_id"],
                    "detection_level": "max_questions_safety",
                },
            )
            assessment_state.current_phase = AssessmentPhase.COMPLETION
            state["assessment_state"] = assessment_state_to_dict(assessment_state)
            return state

        # Build enhanced context for question generation
        context = {
            "previous_messages": messages[-6:],  # Last 3 Q&A pairs
            "min_questions": self.MIN_QUESTIONS,
            "max_questions": self.MAX_QUESTIONS,
            "questions_asked_count": len(questions_asked),
            "questions_answered_count": questions_answered,
            "current_phase": current_phase,
            "recent_questions": questions_asked[-3:]
            if len(questions_asked) >= 3
            else questions_asked,  # Avoid repeating recent questions
            "unanswered_count": unanswered_questions,
        }

        # Use the injected question generator service with enhanced context
        try:
            question_data = await self.question_generator.generate_question(
                assessment_state, context
            )
        except Exception as e:
            logger.error(
                f"Question generation failed: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "thread_id": state["thread_id"],
                    "error_type": type(e).__name__,
                    "fallback_action": "force_completion",
                },
            )
            # Force completion if question generation fails
            assessment_state.current_phase = AssessmentPhase.COMPLETION
            state["assessment_state"] = assessment_state_to_dict(assessment_state)
            return state

        if question_data:
            question_text = question_data.get("text", question_data.get("question_text"))
            question_id = question_data.get(
                "id", question_data.get("question_id", f"dyn_{uuid.uuid4().hex[:8]}")
            )

            # Level 5: Validate generated question isn't identical to recent ones
            if question_text:
                recent_ai_content = [
                    msg.content
                    for msg in messages[-4:]
                    if hasattr(msg, "role") and msg.role == "assistant"
                ]

                if question_text in recent_ai_content:
                    logger.warning(
                        "Level 5: Generated question already exists in recent messages - forcing completion",
                        extra={
                            "duplicate_question": question_text[:100],
                            "thread_id": state["thread_id"],
                            "detection_level": "generated_duplicate",
                        },
                    )
                    assessment_state.current_phase = AssessmentPhase.COMPLETION
                    state["assessment_state"] = assessment_state_to_dict(assessment_state)
                    return state

            logger.info(
                f"Generated valid new question: {question_id}",
                extra={
                    "question_id": question_id,
                    "question_text": question_text[:100] if question_text else "",
                    "question_type": question_data.get("question_type", "generated"),
                    "thread_id": state["thread_id"],
                    "loop_checks_passed": "all_5_levels",
                },
            )

            # Add question to conversation with enhanced metadata
            ai_message = AIMessage(
                content=question_text,
                additional_kwargs={
                    "question_id": question_id,
                    "question_type": question_data.get("question_type", "generated"),
                    "phase": assessment_state.current_phase.value,
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "questions_asked_count": len(questions_asked) + 1,
                    "questions_answered_count": questions_answered,
                    "loop_prevention_version": "v3_enhanced",
                },
            )

            messages.append(ai_message)
            assessment_state.questions_asked.append(question_id)
        else:
            logger.warning(
                "No question generated by service - forcing completion",
                extra={
                    "thread_id": state["thread_id"],
                    "current_phase": current_phase,
                    "questions_asked": len(questions_asked),
                    "fallback_reason": "no_question_generated",
                },
            )
            # Force completion if no question can be generated
            assessment_state.current_phase = AssessmentPhase.COMPLETION

        # Convert back to dictionary for serialization
        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    async def _circuit_breaker_protected_question_node(
        self, state: LangGraphAssessmentState
    ) -> LangGraphAssessmentState:
        """
        Circuit breaker protected question generation for production stability.

        This wrapper provides additional protection against infinite loops and AI service failures.
        """
        thread_id = state["thread_id"]

        try:
            # Check circuit breaker status before proceeding
            if hasattr(self.circuit_breaker, "is_open") and self.circuit_breaker.is_open:
                logger.warning(
                    "Circuit breaker is OPEN - forcing completion to prevent service degradation",
                    extra={
                        "thread_id": thread_id,
                        "circuit_breaker_state": "open",
                        "action": "force_completion",
                    },
                )
                # Force completion when circuit breaker is open
                assessment_state = dict_to_assessment_state(state["assessment_state"])
                assessment_state.current_phase = AssessmentPhase.COMPLETION
                assessment_state.error_count += 1
                state["assessment_state"] = assessment_state_to_dict(assessment_state)
                return state

            # Track question generation frequency for circuit breaker
            if hasattr(self.circuit_breaker, "record_call"):
                self.circuit_breaker.record_call()

            # Call the original question generation logic
            return await self._generate_question_node(state)

        except Exception as e:
            # Record failure for circuit breaker
            if hasattr(self.circuit_breaker, "record_failure"):
                self.circuit_breaker.record_failure()

            logger.error(
                f"Circuit breaker protected question generation failed: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "thread_id": thread_id,
                    "error_type": type(e).__name__,
                    "circuit_breaker_action": "record_failure",
                    "fallback": "force_completion",
                },
            )

            # Force completion on any exception
            assessment_state = dict_to_assessment_state(state["assessment_state"])
            assessment_state.current_phase = AssessmentPhase.COMPLETION
            assessment_state.error_count += 1
            state["assessment_state"] = assessment_state_to_dict(assessment_state)
            return state

    async def _error_node(self, state: LangGraphAssessmentState) -> LangGraphAssessmentState:
        """
        Dedicated error handling node for production robustness.

        This node handles various error conditions and ensures graceful degradation.
        """
        assessment_state = dict_to_assessment_state(state["assessment_state"])
        thread_id = state["thread_id"]

        logger.error(
            "Assessment entered error state - performing graceful shutdown",
            extra={
                "thread_id": thread_id,
                "error_count": assessment_state.error_count,
                "current_phase": assessment_state.current_phase.value,
                "questions_asked": len(assessment_state.questions_asked),
                "questions_answered": assessment_state.questions_answered,
            },
        )

        # Generate error message for user
        error_message = AIMessage(
            content="I apologize, but I'm experiencing some technical difficulties. Let me provide you with a summary of what we've covered so far and some general recommendations.",
            additional_kwargs={
                "message_type": "error_recovery",
                "error_timestamp": datetime.utcnow().isoformat(),
                "thread_id": thread_id,
                "graceful_degradation": True,
            },
        )

        state["messages"].append(error_message)

        # Force completion phase
        assessment_state.current_phase = AssessmentPhase.COMPLETION
        assessment_state.should_continue = False

        # Add some basic recommendations even in error state
        if assessment_state.questions_answered > 0:
            assessment_state.recommendations = [
                "Consider implementing a compliance management system",
                "Regular compliance reviews are recommended",
                "Ensure staff training on regulatory requirements",
            ]

        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    @traceable(
        name="process_answer",
        tags=["node", "answer_processing"],
        metadata={"node_type": "answer_processor"},
    )
    async def _process_answer_node(
        self, state: LangGraphAssessmentState
    ) -> LangGraphAssessmentState:
        """Process the user's answer and extract insights."""
        assessment_state = dict_to_assessment_state(state["assessment_state"])
        messages = state["messages"]

        # Enhanced tracing for answer processing
        logger.info(
            f"Processing answer - Questions answered: {assessment_state.questions_answered}",
            extra={
                "questions_answered": assessment_state.questions_answered,
                "questions_asked": len(assessment_state.questions_asked),
                "current_phase": assessment_state.current_phase.value,
                "messages_count": len(messages),
                "thread_id": state["thread_id"],
            },
        )

        # This node would be triggered after receiving user input
        assessment_state.questions_answered += 1

        # Extract key information from answer
        if messages:
            last_answer = messages[-1]
            if isinstance(last_answer, HumanMessage):
                logger.info(
                    f"Processing user answer: {last_answer.content[:100]}...",
                    extra={
                        "answer_length": len(last_answer.content),
                        "confidence": last_answer.additional_kwargs.get("confidence"),
                        "thread_id": state["thread_id"],
                        "question_number": assessment_state.questions_answered,
                    },
                )
                # Update business profile based on answer
                # This would use NLP/AI to extract structured data
                pass

        # Convert back to dictionary for serialization
        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    async def _determine_next_node(
        self, state: LangGraphAssessmentState
    ) -> LangGraphAssessmentState:
        """Determine whether to continue with more questions or complete."""
        assessment_state = dict_to_assessment_state(state["assessment_state"])

        # Use the injected progress manager service
        assessment_state.should_continue = self.progress_manager.should_continue_assessment(
            assessment_state
        )

        # Convert back to dictionary for serialization
        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    def _route_next_step(self, state: LangGraphAssessmentState) -> str:
        """
        Enhanced routing logic to prevent infinite loops and ensure proper state transitions.

        This method implements critical flow control to prevent the question generation loop
        identified in the user feedback: "the ai is creating the same question over and over again"
        """
        assessment_state = dict_to_assessment_state(state["assessment_state"])
        messages = state["messages"]
        questions_asked = len(assessment_state.questions_asked)
        questions_answered = assessment_state.questions_answered

        logger.info(
            f"Routing next step - Questions asked: {questions_asked}, answered: {questions_answered}, phase: {assessment_state.current_phase.value}",
            extra={
                "questions_asked_count": questions_asked,
                "questions_answered": questions_answered,
                "current_phase": assessment_state.current_phase.value,
                "should_continue": assessment_state.should_continue,
                "error_count": assessment_state.error_count,
                "thread_id": state["thread_id"],
            },
        )

        # Error handling - too many errors encountered
        if assessment_state.error_count > 3:
            logger.warning(
                f"Too many errors ({assessment_state.error_count}) - routing to error node",
                extra={
                    "thread_id": state["thread_id"],
                    "error_count": assessment_state.error_count,
                },
            )
            return "error"

        # Force completion if in completion phase (prevents loops after completion triggered)
        if assessment_state.current_phase == AssessmentPhase.COMPLETION:
            logger.info(
                "In completion phase - routing to completion",
                extra={
                    "thread_id": state["thread_id"],
                    "phase": assessment_state.current_phase.value,
                },
            )
            return "complete"

        # Check for question repetition loop in recent messages
        if len(messages) >= 4:
            recent_ai_messages = [
                msg.content
                for msg in messages[-4:]
                if hasattr(msg, "role") and msg.role == "assistant"
            ]
            if len(recent_ai_messages) >= 2:
                # If last two AI messages are identical, force completion
                if recent_ai_messages[-1] == recent_ai_messages[-2] and recent_ai_messages[-1]:
                    logger.warning(
                        "Question repetition loop detected in routing - forcing completion",
                        extra={
                            "repeated_content": recent_ai_messages[-1][:100],
                            "thread_id": state["thread_id"],
                        },
                    )
                    return "complete"

        # Minimum questions logic - continue asking if we haven't reached minimum
        if questions_answered < self.MIN_QUESTIONS:
            # But check if we've asked too many questions without answers (indicating a stuck state)
            if questions_asked >= questions_answered + 3:  # 3 unanswered questions = stuck
                logger.warning(
                    f"Too many unanswered questions ({questions_asked - questions_answered}) - forcing completion",
                    extra={
                        "questions_asked": questions_asked,
                        "questions_answered": questions_answered,
                        "unanswered_count": questions_asked - questions_answered,
                        "thread_id": state["thread_id"],
                    },
                )
                return "complete"
            else:
                logger.info(
                    f"Below minimum questions ({questions_answered}/{self.MIN_QUESTIONS}) - continuing",
                    extra={
                        "questions_answered": questions_answered,
                        "min_questions": self.MIN_QUESTIONS,
                    },
                )
                return "continue"

        # Maximum questions logic - force completion if we've reached the limit
        if questions_asked >= self.MAX_QUESTIONS:
            logger.info(
                f"Maximum questions reached ({questions_asked}/{self.MAX_QUESTIONS}) - completing",
                extra={"questions_asked": questions_asked, "max_questions": self.MAX_QUESTIONS},
            )
            return "complete"

        # Check explicit should_continue flag
        if not assessment_state.should_continue:
            logger.info(
                "should_continue is False - completing assessment",
                extra={
                    "should_continue": assessment_state.should_continue,
                    "thread_id": state["thread_id"],
                },
            )
            return "complete"

        # Default: continue the assessment
        logger.info(
            "Normal flow - continuing assessment",
            extra={
                "questions_asked": questions_asked,
                "questions_answered": questions_answered,
                "thread_id": state["thread_id"],
            },
        )
        return "continue"

    async def _generate_results_node(
        self, state: LangGraphAssessmentState
    ) -> LangGraphAssessmentState:
        """Generate comprehensive assessment results."""
        assessment_state = dict_to_assessment_state(state["assessment_state"])

        # Calculate compliance score using injected scorer
        assessment_state.compliance_score = self.compliance_scorer.calculate_score(assessment_state)

        # Determine risk level
        assessment_state.risk_level = self.compliance_scorer.determine_risk_level(
            assessment_state.compliance_score
        )

        # Generate recommendations using injected service
        assessment_state.recommendations = (
            await self.recommendation_service.generate_recommendations(
                assessment_state, fallback_mode=assessment_state.fallback_mode
            )
        )

        # Convert back to dictionary for serialization
        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    async def _completion_node(self, state: LangGraphAssessmentState) -> LangGraphAssessmentState:
        """Complete the assessment with a summary."""
        assessment_state = dict_to_assessment_state(state["assessment_state"])

        summary_message = AIMessage(
            content=f"""
Thank you for completing the assessment! Here's what I've learned about your compliance needs:

**Compliance Score:** {assessment_state.compliance_score:.1f}%
**Risk Level:** {assessment_state.risk_level}

**Key Compliance Areas Identified:**
{self._format_list(assessment_state.compliance_needs)}

**Top Recommendations:**
{self._format_recommendations(assessment_state.recommendations[:3])}

Based on our conversation, I can see that your organization would benefit from a more structured
approach to compliance management. Our platform can help automate many of these processes and
ensure you stay compliant with minimal effort.

Would you like to schedule a demo to see how we can help address your specific needs?
        """
        )

        state["messages"].append(summary_message)
        assessment_state.current_phase = AssessmentPhase.COMPLETION

        # Convert back to dictionary for serialization
        state["assessment_state"] = assessment_state_to_dict(assessment_state)
        return state

    # Removed legacy methods - functionality now handled by injected services:
    # - _has_sufficient_information -> AssessmentProgressManager
    # - _calculate_compliance_score -> StandardComplianceScorer
    # - _determine_risk_level -> StandardComplianceScorer
    # - _get_fallback_question -> FallbackQuestionGenerator
    # - _get_fallback_recommendations -> AssessmentRecommendationService

    def _format_list(self, items: List[str]) -> str:
        """Format a list for display."""
        if not items:
            return "- No specific areas identified yet"
        return "\n".join(f"- {item}" for item in items)

    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for display."""
        if not recommendations:
            return "- No recommendations available"

        formatted = []
        for rec in recommendations:
            priority = rec.get("priority", "medium")
            title = rec.get("title", "Recommendation")
            desc = rec.get("description", "")
            formatted.append(f"- **[{priority.upper()}]** {title}: {desc}")

        return "\n".join(formatted)

    async def start_assessment(
        self, session_id: str, lead_id: str, initial_context: Dict[str, Any]
    ) -> LangGraphAssessmentState:
        """
        Start a new assessment session using LangGraph.

        Args:
            session_id: Unique session identifier
            lead_id: Lead identifier
            initial_context: Initial business context

        Returns:
            Initial assessment state
        """
        # Setup PostgreSQL checkpointer tables if using PostgreSQL checkpointer
        if hasattr(self, "connection_pool") and self.connection_pool is not None:
            try:
                # Setup checkpointer tables - this needs to be done outside transaction context
                await self.checkpointer.setup()
                logger.debug("PostgreSQL checkpointer tables verified/created")
            except Exception as e:
                logger.warning(f"Failed to setup PostgreSQL checkpointer tables: {e}")
                # Fallback to MemorySaver
                from langgraph.checkpoint.memory import MemorySaver

                self.checkpointer = MemorySaver()
                self.connection_pool = None
                # Rebuild app with new checkpointer
                self.app = self.graph.compile(checkpointer=self.checkpointer)
                logger.info("Fell back to MemorySaver due to PostgreSQL setup issues")

        # Create initial assessment state using the new focused service classes
        assessment_state = AssessmentState(session_id, lead_id)
        assessment_state.business_profile = initial_context
        assessment_state.total_questions_planned = self.MIN_QUESTIONS
        assessment_state.fallback_mode = not self.circuit_breaker.is_model_available(
            "gemini-2.5-flash"
        )

        # Create LangGraph state wrapper with serializable dict
        initial_state = LangGraphAssessmentState(
            messages=[],
            assessment_state=assessment_state_to_dict(assessment_state),
            thread_id=f"thread_{session_id}",
        )

        # Run the introduction node with tracing context and increased recursion limit
        config = {
            "configurable": {"thread_id": initial_state["thread_id"]},
            "recursion_limit": 100,  # Increase from default 25 to prevent recursion errors
        }

        try:
            with tracing_v2_enabled(
                project_name=os.getenv("LANGCHAIN_PROJECT", "ruleiq-assessment"),
                tags=["assessment_start", f"session:{session_id}"],
            ):
                result = await self.app.ainvoke(initial_state, config)

            logger.info(f"Assessment session started successfully: {session_id}")
            return result

        except Exception as e:
            logger.error(f"Error in LangGraph assessment start: {str(e)}", exc_info=True)
            # Try one more time with MemorySaver fallback
            if hasattr(self, "connection_pool") and self.connection_pool is not None:
                logger.warning("Attempting fallback to MemorySaver due to PostgreSQL issues")
                from langgraph.checkpoint.memory import MemorySaver

                self.checkpointer = MemorySaver()
                self.connection_pool = None
                self.app = self.graph.compile(checkpointer=self.checkpointer)

                try:
                    result = await self.app.ainvoke(initial_state, config)
                    logger.info(
                        f"Assessment session started with MemorySaver fallback: {session_id}"
                    )
                    return result
                except Exception as fallback_error:
                    logger.error(f"Failed even with MemorySaver fallback: {fallback_error}")
                    raise
            else:
                raise

    async def process_user_response(
        self, session_id: str, user_response: str, confidence: Optional[str] = None
    ) -> LangGraphAssessmentState:
        """
        Process a user response and continue the assessment.

        Args:
            session_id: Session identifier
            user_response: User's answer to the question
            confidence: User's confidence level

        Returns:
            Updated LangGraph assessment state
        """
        # Get current state from checkpointer
        config = {
            "configurable": {"thread_id": f"thread_{session_id}"},
            "recursion_limit": 100,  # Increase from default 25 to prevent recursion errors
        }

        try:
            # First, get the current state from the checkpointer
            current_state = await self.app.aget_state(config)

            if not current_state or not current_state.values:
                logger.error(f"No existing state found for session {session_id}")
                raise ValueError(f"No assessment state found for session {session_id}")

            # Get the existing state values
            existing_state = current_state.values

            # Add user message to existing messages
            user_message = HumanMessage(
                content=user_response, additional_kwargs={"confidence": confidence}
            )

            # Update the state with the new message
            updated_state = existing_state.copy()
            updated_state["messages"] = existing_state.get("messages", []) + [user_message]

            # Continue graph execution with tracing context
            with tracing_v2_enabled(
                project_name=os.getenv("LANGCHAIN_PROJECT", "ruleiq-assessment"),
                tags=["assessment_response", f"session:{session_id}"],
            ):
                result = await self.app.ainvoke(updated_state, config)

            return result

        except Exception as e:
            # Enhanced error logging with full exception details
            logger.error(
                f"Error processing user response for session {session_id}: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "session_id": session_id,
                    "user_response_length": len(user_response) if user_response else 0,
                    "confidence": confidence,
                    "error_type": type(e).__name__,
                },
            )
            raise
