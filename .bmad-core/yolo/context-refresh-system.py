#!/usr/bin/env python3
"""
Context Refresh System for BMad YOLO - Ensures optimal context per agent

This system manages context to enable continuous work without overflow.
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class ContextPriority(Enum):
    """Priority levels for context retention."""
    CRITICAL = 1  # Must retain
    HIGH = 2      # Important to retain
    MEDIUM = 3    # Retain if space
    LOW = 4       # Can be summarized
    ARCHIVE = 5   # Can be removed


@dataclass
class ContextItem:
    """Represents a piece of context."""
    item_id: str
    content: str
    priority: ContextPriority
    agent: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    token_count: int = 0
    category: str = ""
    can_summarize: bool = True
    summary: Optional[str] = None


@dataclass
class AgentContext:
    """Context configuration for an agent."""
    agent_name: str
    max_tokens: int = 8000  # Conservative limit
    critical_items: List[str] = field(default_factory=list)
    retain_categories: List[str] = field(default_factory=list)
    summarization_threshold: float = 0.7  # When to start summarizing
    refresh_strategy: str = "sliding_window"


class ContextRefreshSystem:
    """Manages context refresh to ensure continuous work."""

    # Optimal context sizes per agent (in tokens)
    AGENT_CONTEXT_LIMITS = {
        "pm": 6000,        # PM needs broad context
        "architect": 8000,  # Architect needs technical depth
        "po": 5000,        # PO needs epic/story context
        "sm": 4000,        # SM needs current sprint context
        "dev": 10000,      # Dev needs code context
        "qa": 6000,        # QA needs test context
        "security": 5000,  # Security needs vulnerability context
        "devops": 5000     # DevOps needs deployment context
    }

    # Critical context that must be retained
    CRITICAL_CONTEXT = {
        "pm": ["project_goals", "success_criteria", "constraints"],
        "architect": ["tech_stack", "patterns", "architecture_decisions"],
        "po": ["epics", "acceptance_criteria", "priorities"],
        "sm": ["current_story", "sprint_goals", "blockers"],
        "dev": ["current_task", "code_standards", "api_contracts"],
        "qa": ["test_criteria", "quality_gates", "known_issues"],
        "security": ["vulnerabilities", "compliance_requirements"],
        "devops": ["deployment_config", "infrastructure", "credentials"]
    }

    def __init__(self, context_dir: str = ".bmad-core/yolo/context"):
        """Initialize context refresh system."""
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.contexts: Dict[str, List[ContextItem]] = {}
        self.summaries: Dict[str, str] = {}
        self.token_counter = self._simple_token_counter

    def _simple_token_counter(self, text: str) -> int:
        """Simple token estimation (4 chars = 1 token)."""
        return len(text) // 4

    def add_context(
        self,
        agent: str,
        content: str,
        priority: ContextPriority = ContextPriority.MEDIUM,
        category: str = "",
        can_summarize: bool = True
    ) -> ContextItem:
        """Add context item for an agent."""
        item = ContextItem(
            item_id=f"{agent}_{datetime.now(timezone.utc).timestamp()}",
            content=content,
            priority=priority,
            agent=agent,
            token_count=self.token_counter(content),
            category=category,
            can_summarize=can_summarize
        )

        if agent not in self.contexts:
            self.contexts[agent] = []

        self.contexts[agent].append(item)

        # Trigger refresh if needed
        self._check_and_refresh(agent)

        return item

    def _check_and_refresh(self, agent: str):
        """Check if context refresh is needed."""
        limit = self.AGENT_CONTEXT_LIMITS.get(agent, 8000)
        current_tokens = self._calculate_total_tokens(agent)

        if current_tokens > limit:
            logger.info(f"Context refresh triggered for {agent}: {current_tokens} > {limit}")
            self.refresh_context(agent)

    def refresh_context(self, agent: str) -> Dict[str, Any]:
        """Refresh context for an agent using intelligent pruning."""
        if agent not in self.contexts:
            return {"status": "no_context", "tokens": 0}

        items = self.contexts[agent]
        limit = self.AGENT_CONTEXT_LIMITS.get(agent, 8000)

        # Step 1: Separate critical and non-critical items
        critical_items = []
        other_items = []

        critical_categories = self.CRITICAL_CONTEXT.get(agent, [])

        for item in items:
            if item.priority == ContextPriority.CRITICAL or item.category in critical_categories:
                critical_items.append(item)
            else:
                other_items.append(item)

        # Step 2: Calculate critical context size
        critical_tokens = sum(item.token_count for item in critical_items)
        remaining_budget = limit - critical_tokens

        if remaining_budget <= 0:
            # Even critical context exceeds limit, summarize oldest critical
            critical_items = self._summarize_oldest(critical_items, limit)
            self.contexts[agent] = critical_items
            return {
                "status": "critical_only",
                "tokens": self._calculate_total_tokens(agent),
                "items_retained": len(critical_items)
            }

        # Step 3: Apply refresh strategy for non-critical items
        retained_items = self._apply_refresh_strategy(
            other_items,
            remaining_budget,
            agent
        )

        # Step 4: Combine and update
        self.contexts[agent] = critical_items + retained_items

        # Step 5: Create summary of removed items
        removed_count = len(items) - len(self.contexts[agent])
        if removed_count > 0:
            self._create_summary(agent, items, self.contexts[agent])

        return {
            "status": "refreshed",
            "tokens": self._calculate_total_tokens(agent),
            "items_retained": len(self.contexts[agent]),
            "items_removed": removed_count,
            "summary_created": removed_count > 0
        }

    def _apply_refresh_strategy(
        self,
        items: List[ContextItem],
        token_budget: int,
        agent: str
    ) -> List[ContextItem]:
        """Apply refresh strategy to fit within token budget."""
        # Sort by priority and recency
        sorted_items = sorted(
            items,
            key=lambda x: (x.priority.value, -x.created_at.timestamp())
        )

        retained = []
        current_tokens = 0

        for item in sorted_items:
            if current_tokens + item.token_count <= token_budget:
                retained.append(item)
                current_tokens += item.token_count
            elif item.can_summarize and item.priority != ContextPriority.ARCHIVE:
                # Try to summarize instead of removing
                summary = self._summarize_item(item)
                summary_tokens = self.token_counter(summary)

                if current_tokens + summary_tokens <= token_budget:
                    item.summary = summary
                    item.content = summary
                    item.token_count = summary_tokens
                    retained.append(item)
                    current_tokens += summary_tokens

        return retained

    def _summarize_item(self, item: ContextItem) -> str:
        """Create a summary of a context item."""
        # Simple summarization - in production, use LLM
        content = item.content
        if len(content) > 200:
            return f"[Summary of {item.category}]: {content[:150]}..."
        return content

    def _summarize_oldest(
        self,
        items: List[ContextItem],
        limit: int
    ) -> List[ContextItem]:
        """Summarize oldest items to fit within limit."""
        sorted_items = sorted(items, key=lambda x: x.created_at)

        # Summarize oldest 30% of items
        summarize_count = len(items) // 3

        for i in range(min(summarize_count, len(items))):
            if sorted_items[i].can_summarize:
                summary = self._summarize_item(sorted_items[i])
                sorted_items[i].content = summary
                sorted_items[i].token_count = self.token_counter(summary)
                sorted_items[i].summary = summary

        return sorted_items

    def _create_summary(
        self,
        agent: str,
        original_items: List[ContextItem],
        retained_items: List[ContextItem]
    ):
        """Create a summary of removed context."""
        removed = set(item.item_id for item in original_items) - \
                 set(item.item_id for item in retained_items)

        if not removed:
            return

        summary_parts = []
        for item in original_items:
            if item.item_id in removed:
                if item.category:
                    summary_parts.append(f"[{item.category}]: {item.content[:50]}...")
                else:
                    summary_parts.append(f"{item.content[:50]}...")

        summary = f"Previous context summary for {agent}:\n" + "\n".join(summary_parts[:10])
        self.summaries[agent] = summary

        # Save summary to file
        summary_file = self.context_dir / f"{agent}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)

    def _calculate_total_tokens(self, agent: str) -> int:
        """Calculate total tokens for an agent's context."""
        if agent not in self.contexts:
            return 0
        return sum(item.token_count for item in self.contexts[agent])

    def get_context(self, agent: str, format: str = "full") -> str:
        """Get formatted context for an agent."""
        if agent not in self.contexts:
            return ""

        items = self.contexts[agent]

        if format == "full":
            parts = []

            # Add summary if exists
            if agent in self.summaries:
                parts.append(f"=== CONTEXT SUMMARY ===\n{self.summaries[agent]}\n")

            # Add critical context first
            critical = [i for i in items if i.priority == ContextPriority.CRITICAL]
            if critical:
                parts.append("=== CRITICAL CONTEXT ===")
                for item in critical:
                    parts.append(item.content)

            # Add other context by priority
            for priority in [ContextPriority.HIGH, ContextPriority.MEDIUM, ContextPriority.LOW]:
                priority_items = [i for i in items if i.priority == priority]
                if priority_items:
                    parts.append(f"\n=== {priority.name} PRIORITY ===")
                    for item in priority_items:
                        parts.append(item.content)

            return "\n".join(parts)

        elif format == "summary":
            return self.summaries.get(agent, "No summary available")

        elif format == "critical":
            critical = [i.content for i in items if i.priority == ContextPriority.CRITICAL]
            return "\n".join(critical)

    def handoff_context(
        self,
        from_agent: str,
        to_agent: str,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """Create optimized context for agent handoff."""
        handoff_data = {
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": {}
        }

        # Get relevant context from source agent
        if from_agent in self.contexts:
            # Filter context relevant to target agent
            relevant_items = self._filter_relevant_context(
                self.contexts[from_agent],
                to_agent
            )

            # Add to target agent's context
            for item in relevant_items:
                self.add_context(
                    to_agent,
                    item.content,
                    item.priority,
                    f"from_{from_agent}_{item.category}",
                    item.can_summarize
                )

            handoff_data["context"]["items_transferred"] = len(relevant_items)

        # Include summary if requested
        if include_summary and from_agent in self.summaries:
            handoff_data["context"]["summary"] = self.summaries[from_agent]

        # Ensure target agent has optimal context
        refresh_result = self.refresh_context(to_agent)
        handoff_data["context"]["refresh_result"] = refresh_result

        return handoff_data

    def _filter_relevant_context(
        self,
        items: List[ContextItem],
        target_agent: str
    ) -> List[ContextItem]:
        """Filter context relevant to target agent."""
        # Define relevance mapping
        relevance_map = {
            "dev": ["current_story", "api_contracts", "code_standards", "architecture_decisions"],
            "qa": ["current_story", "acceptance_criteria", "test_criteria", "known_issues"],
            "sm": ["sprint_goals", "blockers", "priorities"],
            "architect": ["tech_stack", "patterns", "architecture_decisions"],
            "po": ["epics", "priorities", "success_criteria"],
            "pm": ["project_goals", "constraints", "success_criteria"]
        }

        relevant_categories = relevance_map.get(target_agent, [])

        # Filter items
        relevant = []
        for item in items:
            # Always include critical items
            if item.priority == ContextPriority.CRITICAL:
                relevant.append(item)
            # Include if category matches
            elif item.category in relevant_categories:
                relevant.append(item)
            # Include high priority items up to 30% of budget
            elif item.priority == ContextPriority.HIGH and len(relevant) < 10:
                relevant.append(item)

        return relevant

    def save_state(self):
        """Save context state to disk."""
        state_file = self.context_dir / "context_state.json"

        state = {
            "agents": {}
        }

        for agent, items in self.contexts.items():
            state["agents"][agent] = {
                "item_count": len(items),
                "total_tokens": self._calculate_total_tokens(agent),
                "critical_count": len([i for i in items if i.priority == ContextPriority.CRITICAL]),
                "categories": list(set(i.category for i in items if i.category))
            }

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Context state saved: {len(state['agents'])} agents")

    def get_active_context(self, agent: str = None) -> Dict[str, List[ContextItem]]:
        """Get active context items for an agent or all agents.
        
        Args:
            agent: Optional agent name. If None, returns all contexts.
            
        Returns:
            Dictionary mapping agent names to their context items.
        """
        if agent:
            return {agent: self.contexts.get(agent, [])}
        return self.contexts.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get context statistics."""
        stats = {
            "agents": {},
            "total_tokens": 0,
            "total_items": 0
        }

        for agent in self.contexts:
            tokens = self._calculate_total_tokens(agent)
            items = len(self.contexts[agent])

            stats["agents"][agent] = {
                "tokens": tokens,
                "items": items,
                "utilization": f"{(tokens / self.AGENT_CONTEXT_LIMITS.get(agent, 8000)) * 100:.1f}%"
            }

            stats["total_tokens"] += tokens
            stats["total_items"] += items

        return stats

    def get_status(self) -> Dict[str, Any]:
        """Get context manager status (alias for YOLO integration)."""
        stats = self.get_statistics()

        # Restructure for YOLO integration
        return {
            "total_context_items": stats["total_items"],
            "total_tokens": stats["total_tokens"],
            "agent_contexts": stats["agents"]
        }


# Example usage for continuous work
class ContinuousWorkManager:
    """Manages continuous work with context refresh."""

    def __init__(self):
        """Initialize continuous work manager."""
        self.context_system = ContextRefreshSystem()
        self.work_queue = []

    def execute_with_context(self, agent: str, task: str) -> Dict[str, Any]:
        """Execute task with optimized context."""
        # Add task to context
        self.context_system.add_context(
            agent,
            f"Current task: {task}",
            ContextPriority.CRITICAL,
            "current_task"
        )

        # Get optimized context
        context = self.context_system.get_context(agent)

        # Simulate task execution
        result = {
            "agent": agent,
            "task": task,
            "context_tokens": self.context_system._calculate_total_tokens(agent),
            "status": "completed"
        }

        # Add result to context for next task
        self.context_system.add_context(
            agent,
            f"Previous result: {result['status']}",
            ContextPriority.MEDIUM,
            "previous_result"
        )

        return result

    def handoff_work(self, from_agent: str, to_agent: str, next_task: str):
        """Hand off work between agents with context."""
        # Perform handoff
        handoff = self.context_system.handoff_context(from_agent, to_agent)

        # Add next task
        self.context_system.add_context(
            to_agent,
            f"Next task from {from_agent}: {next_task}",
            ContextPriority.HIGH,
            "handoff_task"
        )

        return handoff


if __name__ == "__main__":
    # Demo the context refresh system
    system = ContextRefreshSystem()

    # Add context for dev agent
    system.add_context("dev", "Implement user authentication", ContextPriority.CRITICAL, "current_task")
    system.add_context("dev", "Use FastAPI framework", ContextPriority.HIGH, "tech_stack")
    system.add_context("dev", "Follow PEP8 standards", ContextPriority.MEDIUM, "code_standards")

    # Add lots of context to trigger refresh
    for i in range(100):
        system.add_context("dev", f"Previous commit {i}: Fixed bug in module {i}", ContextPriority.LOW, "history")

    # Get statistics
    stats = system.get_statistics()
    print(f"Context Statistics: {json.dumps(stats, indent=2)}")

    # Handoff to QA
    handoff = system.handoff_context("dev", "qa")
    print(f"Handoff result: {json.dumps(handoff, indent=2)}")

    # Save state
    system.save_state()
