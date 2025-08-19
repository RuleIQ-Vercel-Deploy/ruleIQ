"""
Service Configuration for Agent Dependencies

This module configures all agent services with proper dependency injection,
following the dependency inversion principle and establishing clear service boundaries.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from services.agents.dependency_injection import (
    DependencyInjectionContainer,
    ServiceLifetime,
    get_container,
)
from services.agents.repositories import (
    BusinessProfileRepository,
    EvidenceRepository,
    ComplianceRepository,
    AssessmentSessionRepository,
)
from services.agents.services import (
    BusinessContextService,
    ComplianceSearchService,
    RecommendationService,
    ExecutionService,
)
from services.agents.assessment_services import (
    AssessmentContextAnalyzer,
    AIQuestionGenerator,
    FallbackQuestionGenerator,
    CompositeQuestionGenerator,
    StandardComplianceScorer,
    AssessmentRecommendationService,
    AssessmentProgressManager,
)
from services.agents.routing_services import (
    PreferredAgentStrategy,
    CapabilityBasedStrategy,
    ConversationalContextStrategy,
    LoadBalancingStrategy,
    FallbackStrategy,
    CompositeRoutingService,
    AgentHealthMonitor,
    SmartAgentRouter,
)
from services.ai.assistant import ComplianceAssistant
from services.ai.circuit_breaker import AICircuitBreaker


def configure_agent_services(container: DependencyInjectionContainer) -> None:
    """
    Configure all agent services with proper dependency injection.

    This function sets up the complete agent service hierarchy:
    1. Core infrastructure services (DB session, AI services)
    2. Repository layer for data access
    3. Domain services for business logic
    4. Assessment-specific services
    5. Routing and orchestration services
    6. Agent implementations
    """

    # ==========================================
    # Core Infrastructure Services
    # ==========================================

    # AI Services (External dependencies - will be injected when creating agents)
    container.register_singleton(AICircuitBreaker)

    # Note: ComplianceAssistant requires database session,
    # so it will be created with factory pattern when needed

    # ==========================================
    # Repository Layer
    # ==========================================

    # Repositories need database session, so they are transient
    # and will be created per request/session
    container.register_transient(BusinessProfileRepository)
    container.register_transient(EvidenceRepository)
    container.register_transient(ComplianceRepository)
    container.register_transient(AssessmentSessionRepository)

    # ==========================================
    # Domain Services Layer
    # ==========================================

    # Business context service
    container.register_transient(BusinessContextService)

    # Compliance search service
    container.register_transient(ComplianceSearchService)

    # Recommendation service
    container.register_transient(RecommendationService)

    # Execution service
    container.register_transient(ExecutionService)

    # ==========================================
    # Assessment Services Layer
    # ==========================================

    # Context analyzer
    container.register_transient(AssessmentContextAnalyzer)

    # Question generation strategies
    container.register_transient(AIQuestionGenerator)
    container.register_singleton(FallbackQuestionGenerator)  # Stateless, can be singleton
    container.register_transient(CompositeQuestionGenerator)

    # Compliance scoring
    container.register_singleton(StandardComplianceScorer)  # Stateless algorithms

    # Recommendation service for assessments
    container.register_transient(AssessmentRecommendationService)

    # Progress management
    container.register_transient(AssessmentProgressManager)

    # ==========================================
    # Routing Services Layer
    # ==========================================

    # Routing strategies (stateless, can be singletons)
    container.register_singleton(PreferredAgentStrategy)
    container.register_singleton(CapabilityBasedStrategy)
    container.register_singleton(ConversationalContextStrategy)
    container.register_singleton(LoadBalancingStrategy)
    container.register_singleton(FallbackStrategy)

    # Routing orchestration
    container.register_singleton(CompositeRoutingService)
    container.register_singleton(AgentHealthMonitor)
    container.register_singleton(SmartAgentRouter)


def create_agent_container_with_session(
    db_session: AsyncSession, neo4j_service: Optional[Any] = None
) -> DependencyInjectionContainer:
    """
    Create a configured container with database session and optional services.

    This is the main entry point for creating agent services with proper
    dependency injection in the context of a specific database session.

    Args:
        db_session: Database session for repositories and services
        neo4j_service: Optional Neo4j service for GraphRAG functionality

    Returns:
        Configured dependency injection container
    """
    # Create a new container for this session
    container = DependencyInjectionContainer()

    # Register the database session as a singleton for this container
    container.register_instance(AsyncSession, db_session)

    # Register Neo4j service if provided
    if neo4j_service:
        container.register_instance(type(neo4j_service), neo4j_service)

    # Register ComplianceAssistant as a factory since it needs the db_session
    container.register_factory(
        ComplianceAssistant, lambda: ComplianceAssistant(db_session), ServiceLifetime.SINGLETON
    )

    # Configure all other services
    configure_agent_services(container)

    return container


def get_configured_service(
    service_type: type, db_session: AsyncSession, neo4j_service: Optional[Any] = None
) -> Any:
    """
    Get a configured service instance with all dependencies injected.

    This is a convenience method for getting individual services
    without managing the container directly.

    Args:
        service_type: The type of service to create
        db_session: Database session for dependencies
        neo4j_service: Optional Neo4j service

    Returns:
        Configured service instance

    Example:
        async with get_async_db() as db:
            assessment_analyzer = get_configured_service(
                AssessmentContextAnalyzer,
                db
            )
    """
    container = create_agent_container_with_session(db_session, neo4j_service)
    return container.resolve(service_type)


def setup_agent_routing_strategies(router: SmartAgentRouter) -> None:
    """
    Set up default routing strategies for the smart agent router.

    This configures the routing priority and strategies for agent selection.
    Strategies are tried in order until one successfully selects an agent.

    Args:
        router: SmartAgentRouter instance to configure
    """
    # Clear any existing strategies
    router.routing_service._strategies.clear()

    # Add strategies in priority order
    container = get_container()

    # High priority: User-preferred agent
    router.add_routing_strategy(container.resolve(PreferredAgentStrategy))

    # Medium priority: Capability-based matching
    router.add_routing_strategy(container.resolve(CapabilityBasedStrategy))

    # Medium priority: Conversational context awareness
    router.add_routing_strategy(container.resolve(ConversationalContextStrategy))

    # Low priority: Load balancing
    router.add_routing_strategy(container.resolve(LoadBalancingStrategy))

    # Lowest priority: Fallback to any available agent
    router.add_routing_strategy(container.resolve(FallbackStrategy))


# Factory functions for common agent service configurations


def create_assessment_agent_services(
    db_session: AsyncSession,
) -> tuple[
    AssessmentContextAnalyzer,
    CompositeQuestionGenerator,
    StandardComplianceScorer,
    AssessmentRecommendationService,
    AssessmentProgressManager,
]:
    """
    Create all services needed for an AssessmentAgent.

    Returns tuple of (context_analyzer, question_generator, scorer, recommendation_service, progress_manager)
    """
    container = create_agent_container_with_session(db_session)

    return (
        container.resolve(AssessmentContextAnalyzer),
        container.resolve(CompositeQuestionGenerator),
        container.resolve(StandardComplianceScorer),
        container.resolve(AssessmentRecommendationService),
        container.resolve(AssessmentProgressManager),
    )


def create_iq_agent_services(
    db_session: AsyncSession, neo4j_service: Optional[Any] = None
) -> tuple[
    BusinessContextService, ComplianceSearchService, RecommendationService, ExecutionService
]:
    """
    Create all services needed for an IQComplianceAgent.

    Returns tuple of (business_context_service, compliance_search_service, recommendation_service, execution_service)
    """
    container = create_agent_container_with_session(db_session, neo4j_service)

    return (
        container.resolve(BusinessContextService),
        container.resolve(ComplianceSearchService),
        container.resolve(RecommendationService),
        container.resolve(ExecutionService),
    )


def create_smart_router(db_session: AsyncSession) -> SmartAgentRouter:
    """
    Create a fully configured SmartAgentRouter with all routing strategies.

    Returns:
        Configured SmartAgentRouter ready for agent routing
    """
    container = create_agent_container_with_session(db_session)
    router = container.resolve(SmartAgentRouter)
    setup_agent_routing_strategies(router)
    return router


# Example usage patterns for documentation
"""
Example Usage Patterns:

1. Manual service creation with DI:
    async with get_async_db() as db:
        container = create_agent_container_with_session(db)
        assessment_agent = AssessmentAgent(
            db,
            context_analyzer=container.resolve(AssessmentContextAnalyzer),
            question_generator=container.resolve(CompositeQuestionGenerator),
            compliance_scorer=container.resolve(StandardComplianceScorer),
            recommendation_service=container.resolve(AssessmentRecommendationService),
            progress_manager=container.resolve(AssessmentProgressManager)
        )

2. Factory function usage:
    async with get_async_db() as db:
        services = create_assessment_agent_services(db)
        assessment_agent = AssessmentAgent(db, *services)

3. Individual service resolution:
    async with get_async_db() as db:
        context_analyzer = get_configured_service(AssessmentContextAnalyzer, db)
        result = await context_analyzer.analyze_conversation_context(...)

4. Router configuration:
    async with get_async_db() as db:
        router = create_smart_router(db)
        agents = {"iq": iq_agent, "assessment": assessment_agent}
        response = await router.route_query("analyze compliance", agents, context)
"""
