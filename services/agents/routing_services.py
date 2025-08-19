"""
Agent routing services following SOLID principles.

This module implements flexible agent routing that follows the Open/Closed principle,
allowing new routing strategies to be added without modifying existing code.
"""

from typing import Dict, List, Optional, Any, Protocol
from abc import abstractmethod
from enum import Enum

from services.agents.protocols import (
    ComplianceAgent,
    AgentCapability,
    ComplianceContext,
    ComplianceResponse,
    ResponseStatus,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class RoutingStrategy(Protocol):
    """Protocol for agent routing strategies."""

    @abstractmethod
    async def select_agent(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> Optional[str]:
        """
        Select the most appropriate agent for the query.

        Args:
            query: The user's query
            agents: Available agents by ID
            context: Query context

        Returns:
            Selected agent ID or None if no suitable agent found
        """
        ...


class RoutingPriority(Enum):
    """Priority levels for routing strategies."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


class PreferredAgentStrategy:
    """Strategy for routing to a preferred agent if available."""

    def __init__(self, priority: RoutingPriority = RoutingPriority.HIGH) -> None:
        self.priority = priority

    async def select_agent(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> Optional[str]:
        """Select preferred agent if specified in context."""
        if context and hasattr(context, "preferred_agent"):
            preferred_agent = getattr(context, "preferred_agent", None)
            if preferred_agent and preferred_agent in agents:
                logger.debug(f"Routing to preferred agent: {preferred_agent}")
                return preferred_agent

        return None


class CapabilityBasedStrategy:
    """Strategy for routing based on required capabilities."""

    def __init__(self, priority: RoutingPriority = RoutingPriority.MEDIUM) -> None:
        self.priority = priority
        self._capability_cache: Dict[str, List[AgentCapability]] = {}

    async def select_agent(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> Optional[str]:
        """Select agent based on required capabilities."""
        required_capabilities = self._extract_required_capabilities(query, context)

        if not required_capabilities:
            return None

        # Find agents with matching capabilities
        for agent_id, agent in agents.items():
            agent_capabilities = await self._get_agent_capabilities(agent_id, agent)

            if all(cap in agent_capabilities for cap in required_capabilities):
                logger.debug(f"Routing to capability-matched agent: {agent_id}")
                return agent_id

        return None

    def _extract_required_capabilities(
        self, query: str, context: Optional[ComplianceContext]
    ) -> List[AgentCapability]:
        """Extract required capabilities from query and context."""
        required_capabilities = []

        # Check context for explicit capabilities
        if context and hasattr(context, "required_capabilities"):
            required_capabilities.extend(getattr(context, "required_capabilities", []))

        # Analyze query for capability hints
        query_lower = query.lower()

        if any(word in query_lower for word in ["assess", "assessment", "evaluate"]):
            required_capabilities.append(AgentCapability.ASSESSMENT)

        if any(word in query_lower for word in ["risk", "threat", "vulnerability"]):
            required_capabilities.append(AgentCapability.RISK_ANALYSIS)

        if any(word in query_lower for word in ["evidence", "document", "proof"]):
            required_capabilities.append(AgentCapability.EVIDENCE_CHECK)

        if any(word in query_lower for word in ["regulation", "compliance", "standard"]):
            required_capabilities.append(AgentCapability.REGULATION_SEARCH)

        if any(word in query_lower for word in ["plan", "strategy", "roadmap"]):
            required_capabilities.append(AgentCapability.PLAN_GENERATION)

        if any(word in query_lower for word in ["report", "generate", "create"]):
            required_capabilities.append(AgentCapability.REPORT_GENERATION)

        return required_capabilities

    async def _get_agent_capabilities(
        self, agent_id: str, agent: ComplianceAgent
    ) -> List[AgentCapability]:
        """Get capabilities for an agent, using cache if available."""
        if agent_id not in self._capability_cache:
            try:
                metadata = await agent.get_capabilities()
                self._capability_cache[agent_id] = metadata.capabilities
            except Exception as e:
                logger.warning(f"Failed to get capabilities for agent {agent_id}: {e}")
                self._capability_cache[agent_id] = []

        return self._capability_cache[agent_id]


class ConversationalContextStrategy:
    """Strategy for routing based on conversational context."""

    def __init__(self, priority: RoutingPriority = RoutingPriority.MEDIUM) -> None:
        self.priority = priority

    async def select_agent(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> Optional[str]:
        """Select agent based on conversational context."""
        if not context or not context.session_id:
            return None

        # If this is part of an ongoing conversation, try to use a conversational agent
        conversational_agents = []

        for agent_id, agent in agents.items():
            try:
                metadata = await agent.get_capabilities()
                if AgentCapability.CONVERSATIONAL in metadata.capabilities:
                    conversational_agents.append(agent_id)
            except Exception:
                continue

        if conversational_agents:
            # For now, return the first conversational agent
            # In a more sophisticated implementation, this could consider
            # previous conversation history
            logger.debug(f"Routing to conversational agent: {conversational_agents[0]}")
            return conversational_agents[0]

        return None


class LoadBalancingStrategy:
    """Strategy for load balancing across multiple suitable agents."""

    def __init__(self, priority: RoutingPriority = RoutingPriority.LOW) -> None:
        self.priority = priority
        self._agent_usage_count: Dict[str, int] = {}

    async def select_agent(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> Optional[str]:
        """Select agent with lowest usage count."""
        if not agents:
            return None

        # Find agent with minimum usage
        min_usage = float("inf")
        selected_agent = None

        for agent_id in agents.keys():
            usage_count = self._agent_usage_count.get(agent_id, 0)
            if usage_count < min_usage:
                min_usage = usage_count
                selected_agent = agent_id

        if selected_agent:
            # Increment usage count
            self._agent_usage_count[selected_agent] = min_usage + 1
            logger.debug(f"Load-balanced routing to agent: {selected_agent}")

        return selected_agent


class FallbackStrategy:
    """Fallback strategy that selects the first available agent."""

    def __init__(self, priority: RoutingPriority = RoutingPriority.LOW) -> None:
        self.priority = priority

    async def select_agent(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> Optional[str]:
        """Select the first available agent as a fallback."""
        if agents:
            fallback_agent = next(iter(agents.keys()))
            logger.debug(f"Fallback routing to agent: {fallback_agent}")
            return fallback_agent

        return None


class CompositeRoutingService:
    """Composite routing service that applies multiple strategies in order."""

    def __init__(self) -> None:
        self._strategies: List[RoutingStrategy] = []

    def add_strategy(self, strategy: RoutingStrategy) -> None:
        """Add a routing strategy."""
        self._strategies.append(strategy)

    def remove_strategy(self, strategy: RoutingStrategy) -> None:
        """Remove a routing strategy."""
        if strategy in self._strategies:
            self._strategies.remove(strategy)

    async def route_query(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> ComplianceResponse:
        """
        Route query to the most appropriate agent using configured strategies.

        Args:
            query: The user's query
            agents: Available agents by ID
            context: Query context

        Returns:
            Response from the selected agent or error response
        """
        if not agents:
            return ComplianceResponse(
                status=ResponseStatus.ERROR,
                message="No agents available to process this query",
                errors=["No registered agents found"],
            )

        # Try each strategy in order
        for strategy in self._strategies:
            try:
                selected_agent_id = await strategy.select_agent(query, agents, context)

                if selected_agent_id and selected_agent_id in agents:
                    agent = agents[selected_agent_id]
                    logger.info(f"Routing query to agent: {selected_agent_id}")
                    return await agent.process_query(query, context)

            except Exception as e:
                logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
                continue

        # If all strategies failed, return error
        return ComplianceResponse(
            status=ResponseStatus.ERROR,
            message="Failed to route query to any agent",
            errors=["All routing strategies failed"],
        )


class AgentHealthMonitor:
    """Service for monitoring agent health and availability."""

    def __init__(self) -> None:
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes

    async def get_healthy_agents(
        self, agents: Dict[str, ComplianceAgent]
    ) -> Dict[str, ComplianceAgent]:
        """Get only healthy agents from the provided set."""
        healthy_agents = {}

        for agent_id, agent in agents.items():
            try:
                health_status = await self._get_agent_health(agent_id, agent)

                if health_status.get("status") in ["healthy", "degraded"]:
                    healthy_agents[agent_id] = agent
                else:
                    logger.warning(f"Agent {agent_id} is unhealthy: {health_status}")

            except Exception as e:
                logger.warning(f"Failed to check health for agent {agent_id}: {e}")
                # Include agent anyway if health check fails
                healthy_agents[agent_id] = agent

        return healthy_agents

    async def _get_agent_health(self, agent_id: str, agent: ComplianceAgent) -> Dict[str, Any]:
        """Get health status for an agent, using cache if available."""
        import time

        # Check cache
        if agent_id in self._health_cache:
            cache_entry = self._health_cache[agent_id]
            if time.time() - cache_entry["timestamp"] < self._cache_ttl:
                return cache_entry["health"]

        # Get fresh health status
        try:
            health_status = await agent.health_check()

            # Cache the result
            self._health_cache[agent_id] = {"health": health_status, "timestamp": time.time()}

            return health_status

        except Exception as e:
            logger.error(f"Health check failed for agent {agent_id}: {e}")
            return {"status": "error", "error": str(e)}


class SmartAgentRouter:
    """
    Smart agent router that combines routing strategies with health monitoring.

    This is the main entry point for agent routing in the system.
    """

    def __init__(self) -> None:
        self.routing_service = CompositeRoutingService()
        self.health_monitor = AgentHealthMonitor()

        # Configure default routing strategies
        self._setup_default_strategies()

    def _setup_default_strategies(self) -> None:
        """Set up default routing strategies in priority order."""
        # High priority: Preferred agent
        self.routing_service.add_strategy(PreferredAgentStrategy())

        # Medium priority: Capability-based routing
        self.routing_service.add_strategy(CapabilityBasedStrategy())

        # Medium priority: Conversational context
        self.routing_service.add_strategy(ConversationalContextStrategy())

        # Low priority: Load balancing
        self.routing_service.add_strategy(LoadBalancingStrategy())

        # Lowest priority: Fallback
        self.routing_service.add_strategy(FallbackStrategy())

    async def route_query(
        self,
        query: str,
        agents: Dict[str, ComplianceAgent],
        context: Optional[ComplianceContext] = None,
    ) -> ComplianceResponse:
        """
        Route query to the best available agent.

        Args:
            query: The user's query
            agents: Available agents by ID
            context: Query context

        Returns:
            Response from the selected agent
        """
        # Filter for healthy agents first
        healthy_agents = await self.health_monitor.get_healthy_agents(agents)

        if not healthy_agents:
            logger.error("No healthy agents available for routing")
            return ComplianceResponse(
                status=ResponseStatus.ERROR,
                message="No healthy agents available to process this query",
                errors=["All agents are currently unhealthy"],
            )

        # Route using the composite routing service
        return await self.routing_service.route_query(query, healthy_agents, context)

    def add_routing_strategy(self, strategy: RoutingStrategy) -> None:
        """Add a custom routing strategy."""
        self.routing_service.add_strategy(strategy)

    def remove_routing_strategy(self, strategy: RoutingStrategy) -> None:
        """Remove a routing strategy."""
        self.routing_service.remove_strategy(strategy)
