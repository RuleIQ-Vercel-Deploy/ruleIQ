"""
Service Interfaces for Agent Architecture

This module defines abstract interfaces for all agent services,
following the Interface Segregation Principle and enabling
proper dependency inversion and testability.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from enum import Enum

from services.agents.assessment_services import AssessmentState
from services.agents.protocols import ComplianceContext, ComplianceResponse


# ==========================================
# Repository Interfaces
# ==========================================


@runtime_checkable
class IRepository(Protocol):
    """Base repository interface for data access operations."""

    async def create(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity."""
        ...

    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID."""
        ...

    async def update(self, entity_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing entity."""
        ...

    async def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        ...


@runtime_checkable
class IBusinessProfileRepository(IRepository, Protocol):
    """Interface for business profile data access."""

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get business profile by user ID."""
        ...

    async def get_compliance_status(self, profile_id: str) -> Dict[str, Any]:
        """Get compliance status for a business profile."""
        ...


@runtime_checkable
class IEvidenceRepository(IRepository, Protocol):
    """Interface for evidence data access."""

    async def get_by_business_profile(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get all evidence for a business profile."""
        ...

    async def get_by_framework(self, framework_id: str) -> List[Dict[str, Any]]:
        """Get evidence for a specific framework."""
        ...


@runtime_checkable
class IComplianceRepository(IRepository, Protocol):
    """Interface for compliance data access."""

    async def search_regulations(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search compliance regulations."""
        ...

    async def get_framework_requirements(self, framework_id: str) -> List[Dict[str, Any]]:
        """Get requirements for a compliance framework."""
        ...


@runtime_checkable
class IAssessmentSessionRepository(IRepository, Protocol):
    """Interface for assessment session data access."""

    async def get_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment session by ID."""
        ...

    async def update_session_state(self, session_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update assessment session state."""
        ...


# ==========================================
# Domain Service Interfaces
# ==========================================


@runtime_checkable
class IBusinessContextService(Protocol):
    """Interface for business context operations."""

    async def retrieve_business_context(
        self, user_id: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve business context for a user."""
        ...

    async def retrieve_session_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve context for a specific session."""
        ...

    async def update_business_profile(
        self, user_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update business profile information."""
        ...


@runtime_checkable
class IComplianceSearchService(Protocol):
    """Interface for compliance search operations."""

    async def search_compliance_resources(
        self, query: str, context: Optional[ComplianceContext] = None, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search compliance resources."""
        ...

    async def get_regulatory_updates(self, frameworks: List[str]) -> List[Dict[str, Any]]:
        """Get recent regulatory updates."""
        ...


@runtime_checkable
class IRecommendationService(Protocol):
    """Interface for recommendation generation."""

    async def generate_compliance_recommendations(
        self, business_profile: Dict[str, Any], compliance_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate compliance recommendations."""
        ...

    async def prioritize_actions(
        self, recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize recommended actions."""
        ...


@runtime_checkable
class IExecutionService(Protocol):
    """Interface for plan execution operations."""

    async def create_implementation_plan(
        self, recommendations: List[Dict[str, Any]], business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an implementation plan."""
        ...

    async def track_progress(self, plan_id: str) -> Dict[str, Any]:
        """Track implementation progress."""
        ...


# ==========================================
# Assessment Service Interfaces
# ==========================================


@runtime_checkable
class IAssessmentContextAnalyzer(Protocol):
    """Interface for assessment context analysis."""

    async def analyze_conversation_context(
        self, messages: List[Any], business_profile: Dict[str, Any], fallback_mode: bool = False
    ) -> Dict[str, Any]:
        """Analyze conversation context to extract insights."""
        ...


@runtime_checkable
class IQuestionGenerator(Protocol):
    """Interface for question generation."""

    async def generate_question(
        self, state: AssessmentState, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate the next question based on assessment state."""
        ...


@runtime_checkable
class IComplianceScorer(Protocol):
    """Interface for compliance scoring."""

    def calculate_score(self, state: AssessmentState) -> float:
        """Calculate compliance score based on assessment state."""
        ...

    def determine_risk_level(self, score: float) -> str:
        """Determine risk level from compliance score."""
        ...


@runtime_checkable
class IAssessmentRecommendationService(Protocol):
    """Interface for assessment recommendation generation."""

    async def generate_recommendations(
        self, state: AssessmentState, fallback_mode: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on assessment results."""
        ...


@runtime_checkable
class IAssessmentProgressManager(Protocol):
    """Interface for assessment progress management."""

    def should_continue_assessment(self, state: AssessmentState) -> bool:
        """Determine if assessment should continue."""
        ...

    def get_completion_status(self, state: AssessmentState) -> str:
        """Get the current completion status."""
        ...


# ==========================================
# Routing Service Interfaces
# ==========================================


@runtime_checkable
class IRoutingStrategy(Protocol):
    """Interface for agent routing strategies."""

    async def select_agent(
        self, query: str, agents: Dict[str, Any], context: Optional[ComplianceContext] = None
    ) -> Optional[str]:
        """Select the most appropriate agent for the query."""
        ...


@runtime_checkable
class IAgentRouter(Protocol):
    """Interface for agent routing orchestration."""

    async def route_query(
        self, query: str, agents: Dict[str, Any], context: Optional[ComplianceContext] = None
    ) -> ComplianceResponse:
        """Route query to the most appropriate agent."""
        ...

    def add_routing_strategy(self, strategy: IRoutingStrategy) -> None:
        """Add a routing strategy."""
        ...


@runtime_checkable
class IAgentHealthMonitor(Protocol):
    """Interface for agent health monitoring."""

    async def get_healthy_agents(self, agents: Dict[str, Any]) -> Dict[str, Any]:
        """Get only healthy agents from the provided set."""
        ...

    async def check_agent_health(self, agent: Any) -> Dict[str, Any]:
        """Check health status of a specific agent."""
        ...


# ==========================================
# AI Service Interfaces
# ==========================================


@runtime_checkable
class IAICircuitBreaker(Protocol):
    """Interface for AI service circuit breaker."""

    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available."""
        ...

    def record_success(self, model_name: str) -> None:
        """Record a successful model call."""
        ...

    def record_failure(self, model_name: str, error: Exception) -> None:
        """Record a failed model call."""
        ...


@runtime_checkable
class IComplianceAssistant(Protocol):
    """Interface for AI compliance assistant."""

    async def analyze_conversation_context(
        self, messages: List[Any], business_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze conversation context using AI."""
        ...

    async def generate_contextual_question(
        self, context: Dict[str, Any], previous_messages: List[Any]
    ) -> Dict[str, Any]:
        """Generate contextual question using AI."""
        ...

    async def generate_recommendations(
        self,
        business_profile: Dict[str, Any],
        compliance_needs: List[str],
        identified_risks: List[Dict[str, Any]],
        compliance_score: float,
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations."""
        ...


# ==========================================
# Service Configuration Interface
# ==========================================


@runtime_checkable
class IServiceContainer(Protocol):
    """Interface for dependency injection container."""

    def register_singleton(
        self, service_type: type, implementation_type: Optional[type] = None
    ) -> "IServiceContainer":
        """Register a service as singleton."""
        ...

    def register_transient(
        self, service_type: type, implementation_type: Optional[type] = None
    ) -> "IServiceContainer":
        """Register a service as transient."""
        ...

    def register_factory(self, service_type: type, factory: callable) -> "IServiceContainer":
        """Register a service with a factory function."""
        ...

    def resolve(self, service_type: type) -> Any:
        """Resolve a service instance with its dependencies."""
        ...

    def is_registered(self, service_type: type) -> bool:
        """Check if a service type is registered."""
        ...


# ==========================================
# Agent Interface Extensions
# ==========================================


@runtime_checkable
class IConfigurableAgent(Protocol):
    """Interface for agents that can be configured with dependency injection."""

    def configure_dependencies(self, container: IServiceContainer) -> None:
        """Configure agent with dependencies from container."""
        ...

    def validate_configuration(self) -> bool:
        """Validate that all required dependencies are configured."""
        ...


@runtime_checkable
class IDisposableService(Protocol):
    """Interface for services that need cleanup."""

    def dispose(self) -> None:
        """Clean up service resources."""
        ...


# ==========================================
# Service Metadata and Discovery
# ==========================================


class ServiceType(Enum):
    """Enumeration of service types for discovery and configuration."""

    REPOSITORY = "repository"
    DOMAIN_SERVICE = "domain_service"
    ASSESSMENT_SERVICE = "assessment_service"
    ROUTING_SERVICE = "routing_service"
    AI_SERVICE = "ai_service"
    INFRASTRUCTURE = "infrastructure"


@runtime_checkable
class IServiceMetadata(Protocol):
    """Interface for service metadata and discovery."""

    @property
    def service_type(self) -> ServiceType:
        """Get the type of service."""
        ...

    @property
    def dependencies(self) -> List[type]:
        """Get list of service dependencies."""
        ...

    @property
    def provides_interfaces(self) -> List[type]:
        """Get list of interfaces this service implements."""
        ...


# ==========================================
# Service Health and Monitoring
# ==========================================


class HealthStatus(Enum):
    """Service health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@runtime_checkable
class IHealthCheckable(Protocol):
    """Interface for services that support health checking."""

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...

    def get_health_status(self) -> HealthStatus:
        """Get current health status."""
        ...
