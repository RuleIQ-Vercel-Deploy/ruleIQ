"""
Assessment-specific services following SOLID principles.

This module provides focused services for assessment operations,
extracted from the monolithic AssessmentAgent to improve maintainability
and testability.
"""

from typing import Dict, List, Optional, Any, Protocol
from abc import abstractmethod
from enum import Enum

from services.ai.assistant import ComplianceAssistant
from services.ai.circuit_breaker import AICircuitBreaker
from config.logging_config import get_logger

logger = get_logger(__name__)


class AssessmentPhase(Enum):
    """Phases of the assessment process."""

    INTRODUCTION = "introduction"
    BUSINESS_CONTEXT = "business_context"
    COMPLIANCE_DISCOVERY = "compliance_discovery"
    DEEP_DIVE = "deep_dive"
    RISK_ASSESSMENT = "risk_assessment"
    RECOMMENDATIONS = "recommendations"
    COMPLETION = "completion"


class AssessmentState:
    """State container for assessment progress."""

    def __init__(self, session_id: str, lead_id: str) -> None:
        self.session_id = session_id
        self.lead_id = lead_id
        self.thread_id = f"thread_{session_id}"
        self.current_phase = AssessmentPhase.INTRODUCTION
        self.questions_asked: List[str] = []
        self.questions_answered = 0
        self.total_questions_planned = 5
        self.business_profile: Dict[str, Any] = {}
        self.compliance_needs: List[str] = []
        self.identified_risks: List[Dict[str, Any]] = []
        self.next_question_context: Dict[str, Any] = {}
        self.follow_up_needed = False
        self.expertise_level = "intermediate"
        self.compliance_score = 0.0
        self.risk_level = "unknown"
        self.recommendations: List[Dict[str, Any]] = []
        self.gaps_identified: List[Dict[str, Any]] = []
        self.should_continue = True
        self.error_count = 0
        self.fallback_mode = False


class QuestionGenerationStrategy(Protocol):
    """Protocol for question generation strategies."""

    @abstractmethod
    async def generate_question(
        self, state: AssessmentState, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate the next question based on assessment state."""
        ...


class ComplianceScorer(Protocol):
    """Protocol for compliance scoring strategies."""

    @abstractmethod
    def calculate_score(self, state: AssessmentState) -> float:
        """Calculate compliance score based on assessment state."""
        ...

    @abstractmethod
    def determine_risk_level(self, score: float) -> str:
        """Determine risk level from compliance score."""
        ...


class AssessmentContextAnalyzer:
    """Service for analyzing assessment context and extracting insights."""

    def __init__(self, assistant: ComplianceAssistant, circuit_breaker: AICircuitBreaker) -> None:
        self.assistant = assistant
        self.circuit_breaker = circuit_breaker

    async def analyze_conversation_context(
        self, messages: List[Any], business_profile: Dict[str, Any], fallback_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze conversation context to extract insights.

        Args:
            messages: Recent conversation messages
            business_profile: Current business profile data
            fallback_mode: Whether to use fallback analysis

        Returns:
            Analysis results with insights and recommendations
        """
        if not fallback_mode and self.circuit_breaker.is_model_available("gemini-2.5-flash"):
            try:
                return await self._ai_powered_analysis(messages, business_profile)
            except Exception as e:
                logger.warning(f"AI analysis failed, falling back: {e}")
                fallback_mode = True

        if fallback_mode:
            return self._heuristic_analysis(messages)

        return {}

    async def _ai_powered_analysis(
        self, messages: List[Any], business_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to analyze conversation context."""
        return await self.assistant.analyze_conversation_context(
            messages=messages[-10:],  # Last 10 messages for context
            business_profile=business_profile,
        )

    def _heuristic_analysis(self, messages: List[Any]) -> Dict[str, Any]:
        """Fallback heuristic-based analysis."""
        if not messages:
            return {"insights": {}, "compliance_needs": [], "expertise_level": "intermediate"}

        recent_answer = getattr(messages[-1], "content", "") if messages else ""

        # Determine expertise level based on answer length and detail
        if len(recent_answer) > 200:
            expertise_level = "expert"
        elif len(recent_answer) > 50:
            expertise_level = "intermediate"
        else:
            expertise_level = "beginner"

        # Simple keyword detection for compliance needs
        compliance_needs = []
        keywords = {
            "gdpr": ["personal data", "eu", "privacy", "gdpr"],
            "security": ["security", "breach", "cyber", "hack"],
            "iso": ["iso", "certification", "audit"],
            "data": ["data protection", "backup", "storage"],
        }

        answer_lower = recent_answer.lower()
        for need, terms in keywords.items():
            if any(term in answer_lower for term in terms):
                compliance_needs.append(need)

        return {
            "insights": {"answer_detail_level": len(recent_answer)},
            "compliance_needs": compliance_needs,
            "expertise_level": expertise_level,
            "follow_up_needed": len(recent_answer) < 30,  # Short answers may need follow-up
        }


class AIQuestionGenerator:
    """AI-powered question generation service."""

    def __init__(self, assistant: ComplianceAssistant, circuit_breaker: AICircuitBreaker) -> None:
        self.assistant = assistant
        self.circuit_breaker = circuit_breaker

    async def generate_question(
        self, state: AssessmentState, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate contextual question using AI."""
        if not self.circuit_breaker.is_model_available("gemini-2.5-flash"):
            return None

        try:
            question_context = {
                "phase": state.current_phase.value,
                "questions_asked": len(state.questions_asked),
                "business_profile": state.business_profile,
                "compliance_needs": state.compliance_needs,
                "expertise_level": state.expertise_level,
                "questions_answered": state.questions_answered,
                "min_questions": 5,
                "max_questions": 12,
            }

            question_data = await self.assistant.generate_contextual_question(
                context=question_context, previous_messages=context.get("previous_messages", [])
            )

            return question_data

        except Exception as e:
            logger.warning(f"AI question generation failed: {e}")
            return None


class FallbackQuestionGenerator:
    """Fallback question generation using predefined questions."""

    def __init__(self) -> None:
        self.fallback_questions = {
            AssessmentPhase.BUSINESS_CONTEXT: [
                {"id": "fb_biz_1", "text": "How many employees does your organization have?"},
                {
                    "id": "fb_biz_2",
                    "text": "Do you operate in multiple countries or just domestically?",
                },
                {"id": "fb_biz_3", "text": "What are your main products or services?"},
            ],
            AssessmentPhase.COMPLIANCE_DISCOVERY: [
                {
                    "id": "fb_comp_1",
                    "text": "Do you currently follow any compliance frameworks (like ISO, SOC 2, GDPR)?",
                },
                {"id": "fb_comp_2", "text": "Have you had any compliance audits in the past year?"},
                {
                    "id": "fb_comp_3",
                    "text": "Do you handle sensitive customer data like payment information or health records?",
                },
            ],
            AssessmentPhase.RISK_ASSESSMENT: [
                {
                    "id": "fb_risk_1",
                    "text": "Have you experienced any security incidents or data breaches?",
                },
                {
                    "id": "fb_risk_2",
                    "text": "How do you currently manage access to sensitive systems?",
                },
                {"id": "fb_risk_3", "text": "Do you have a documented incident response plan?"},
            ],
        }

    async def generate_question(
        self, state: AssessmentState, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate fallback question from predefined set."""
        phase_questions = self.fallback_questions.get(state.current_phase, [])

        # Find a question that hasn't been asked yet
        for question in phase_questions:
            if question["id"] not in state.questions_asked:
                return question

        # If all questions in current phase are asked, move to next phase
        return self._advance_to_next_phase(state)

    def _advance_to_next_phase(self, state: AssessmentState) -> Optional[Dict[str, Any]]:
        """Advance to the next assessment phase."""
        phase_order = [
            AssessmentPhase.BUSINESS_CONTEXT,
            AssessmentPhase.COMPLIANCE_DISCOVERY,
            AssessmentPhase.RISK_ASSESSMENT,
        ]

        try:
            current_index = phase_order.index(state.current_phase)
            if current_index < len(phase_order) - 1:
                state.current_phase = phase_order[current_index + 1]
                # Return the first question from the new phase directly
                phase_questions = self.fallback_questions.get(state.current_phase, [])
                for question in phase_questions:
                    if question["id"] not in state.questions_asked:
                        return question
        except (ValueError, IndexError):
            pass

        return None


class StandardComplianceScorer:
    """Standard compliance scoring implementation."""

    def calculate_score(self, state: AssessmentState) -> float:
        """Calculate compliance score based on assessment state."""
        base_score = 50.0

        # Adjust based on identified risks
        risk_penalty = len(state.identified_risks) * 5
        base_score -= risk_penalty

        # Adjust based on compliance needs addressed
        needs_bonus = len(state.compliance_needs) * 3
        base_score += needs_bonus

        # Adjust based on expertise level
        expertise_bonus = {"beginner": -10, "intermediate": 0, "expert": 10}.get(
            state.expertise_level, 0
        )

        base_score += expertise_bonus

        # Ensure score is within bounds
        return max(0, min(100, base_score))

    def determine_risk_level(self, score: float) -> str:
        """Determine risk level based on compliance score."""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        elif score >= 40:
            return "high"
        else:
            return "critical"


class AssessmentRecommendationService:
    """Service for generating assessment recommendations."""

    def __init__(self, assistant: ComplianceAssistant, circuit_breaker: AICircuitBreaker) -> None:
        self.assistant = assistant
        self.circuit_breaker = circuit_breaker

    async def generate_recommendations(
        self, state: AssessmentState, fallback_mode: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on assessment results.

        Args:
            state: Current assessment state
            fallback_mode: Whether to use fallback recommendations

        Returns:
            List of recommendation objects
        """
        if not fallback_mode and self.circuit_breaker.is_model_available("gemini-2.5-flash"):
            try:
                return await self._ai_powered_recommendations(state)
            except Exception as e:
                logger.error(f"AI recommendation generation failed: {e}")
                fallback_mode = True

        if fallback_mode:
            return self._fallback_recommendations(state)

        return []

    async def _ai_powered_recommendations(self, state: AssessmentState) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations."""
        return await self.assistant.generate_recommendations(
            business_profile=state.business_profile,
            compliance_needs=state.compliance_needs,
            identified_risks=state.identified_risks,
            compliance_score=state.compliance_score,
        )

    def _fallback_recommendations(self, state: AssessmentState) -> List[Dict[str, Any]]:
        """Generate fallback recommendations based on score."""
        score = state.compliance_score

        if score < 40:
            return [
                {
                    "priority": "high",
                    "title": "Implement Basic Compliance Framework",
                    "description": "Start with ISO 27001 basics to establish foundational security controls",
                },
                {
                    "priority": "high",
                    "title": "Conduct Risk Assessment",
                    "description": "Identify and document your key compliance risks and vulnerabilities",
                },
                {
                    "priority": "medium",
                    "title": "Develop Security Policies",
                    "description": "Create and document essential security and data protection policies",
                },
            ]
        elif score < 70:
            return [
                {
                    "priority": "medium",
                    "title": "Enhance Current Controls",
                    "description": "Strengthen existing compliance measures and fill identified gaps",
                },
                {
                    "priority": "medium",
                    "title": "Implement Monitoring",
                    "description": "Set up continuous compliance monitoring and alerting",
                },
                {
                    "priority": "low",
                    "title": "Prepare for Certification",
                    "description": "Work towards formal compliance certification",
                },
            ]
        else:
            return [
                {
                    "priority": "low",
                    "title": "Maintain Excellence",
                    "description": "Continue regular reviews and updates to maintain high compliance standards",
                },
                {
                    "priority": "low",
                    "title": "Automate Processes",
                    "description": "Look for opportunities to automate compliance workflows",
                },
            ]


class CompositeQuestionGenerator:
    """Composite question generator that tries multiple strategies."""

    def __init__(
        self, ai_generator: AIQuestionGenerator, fallback_generator: FallbackQuestionGenerator
    ) -> None:
        self.ai_generator = ai_generator
        self.fallback_generator = fallback_generator

    async def generate_question(
        self, state: AssessmentState, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate question using available strategies."""
        # Try AI-powered generation first
        if not state.fallback_mode:
            question = await self.ai_generator.generate_question(state, context)
            if question:
                return question
            else:
                state.fallback_mode = True

        # Fall back to predefined questions
        return await self.fallback_generator.generate_question(state, context)


class AssessmentProgressManager:
    """Service for managing assessment progress and flow control."""

    def __init__(self, min_questions: int = 5, max_questions: int = 12) -> None:
        self.min_questions = min_questions
        self.max_questions = max_questions

    def should_continue_assessment(self, state: AssessmentState) -> bool:
        """Determine if assessment should continue."""
        questions_answered = state.questions_answered

        # Check completion criteria
        if questions_answered >= self.min_questions:
            # Check if we have enough information
            if self._has_sufficient_information(state):
                return False
            elif questions_answered >= self.max_questions:
                return False
            else:
                # Continue if we need more information
                return True
        else:
            return True

    def _has_sufficient_information(self, state: AssessmentState) -> bool:
        """Check if we have enough information to generate meaningful results."""
        # Check key information points
        has_business_type = bool(state.business_profile.get("business_type"))
        has_company_size = bool(state.business_profile.get("company_size"))
        has_compliance_needs = len(state.compliance_needs) > 0
        has_enough_answers = state.questions_answered >= self.min_questions

        return all([has_business_type, has_company_size, has_compliance_needs, has_enough_answers])

    def get_completion_status(self, state: AssessmentState) -> str:
        """Get the current completion status."""
        if state.error_count > 3:
            return "error"
        elif self.should_continue_assessment(state):
            return "continue"
        else:
            return "complete"
