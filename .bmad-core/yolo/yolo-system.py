#!/usr/bin/env python3
"""
BMad YOLO System - Autonomous Multi-Agent Workflow Automation

This system enables fully automated workflows with minimal human intervention.
Now integrated with context refresh system for continuous operation.
"""
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
import yaml
import sys

# Import context refresh system and retry utilities
sys.path.append(str(Path(__file__).parent))

# Import configuration manager
try:
    from config_manager import ConfigManager, YOLOConfig
except ImportError:
    ConfigManager = None
    YOLOConfig = None

# Import retry utilities
try:
    from retry_utils import async_retry, get_all_retry_metrics, RetryMetrics
except ImportError:
    # Fallback if not available
    async_retry = None
    get_all_retry_metrics = None
    RetryMetrics = None
try:
    # Try importing with underscore
    from context_refresh_system import ContextRefreshSystem, ContextPriority
except ImportError:
    try:
        # Try loading module with hyphen in filename
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "context_refresh_system", 
            Path(__file__).parent / "context-refresh-system.py"
        )
        if spec and spec.loader:
            context_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(context_module)
            ContextRefreshSystem = context_module.ContextRefreshSystem
            ContextPriority = context_module.ContextPriority
        else:
            ContextRefreshSystem = None
            ContextPriority = None
    except Exception:
        # Fallback if not available
        ContextRefreshSystem = None
        ContextPriority = None

logger = logging.getLogger(__name__)


class YOLOMode(Enum):
    """YOLO operation modes."""
    OFF = "off"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class AgentType(Enum):
    """Available agent types in BMad system."""
    PM = "pm"  # Product Manager
    ARCHITECT = "architect"
    PO = "po"  # Product Owner
    SM = "sm"  # Scrum Master
    DEV = "dev"  # Developer
    QA = "qa"  # Quality Assurance
    DEVOPS = "devops"
    SECURITY = "security"
    DOCUMENTATION = "documentation"


class WorkflowPhase(Enum):
    """Workflow phases."""
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    STORY_CREATION = "story_creation"
    DEVELOPMENT = "development"
    TESTING = "testing"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"


@dataclass
class YOLODecision:
    """Records a decision made in YOLO mode."""
    decision_id: str
    decision_type: str
    choice_made: str
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    agent: Optional[AgentType] = None
    confidence: float = 0.8


@dataclass
class YOLOState:
    """Current state of YOLO system."""
    mode: YOLOMode = YOLOMode.OFF
    current_phase: Optional[WorkflowPhase] = None
    current_agent: Optional[AgentType] = None
    next_agent: Optional[AgentType] = None
    workflow_progress: Dict[str, Any] = field(default_factory=dict)
    decisions_made: List[YOLODecision] = field(default_factory=list)
    errors_encountered: List[str] = field(default_factory=list)
    consecutive_errors: int = 0
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None


@dataclass
class HandoffPackage:
    """Package for agent handoffs."""
    from_agent: AgentType
    to_agent: AgentType
    phase: WorkflowPhase
    artifacts: Dict[str, List[str]] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    next_action: str = ""
    yolo_mode: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)


class YOLODefaults:
    """Default decisions for YOLO mode."""
    
    TECHNICAL = {
        "language": "python",
        "framework": "fastapi",
        "frontend": "nextjs",
        "database": "postgresql",
        "testing": "pytest",
        "ci_cd": "github_actions",
        "containerization": "docker",
        "orchestration": "kubernetes",
        "monitoring": "prometheus",
        "logging": "elasticsearch"
    }
    
    PROCESS = {
        "epic_count": 3,
        "stories_per_epic": 4,
        "test_coverage_target": 80,
        "code_review_required": True,
        "auto_merge_on_pass": True,
        "deploy_on_merge": False
    }
    
    WORKFLOW = {
        "on_success": "proceed_to_next",
        "on_minor_issues": "document_and_continue",
        "on_major_issues": "pause_and_alert",
        "on_critical_error": "stop_and_rollback",
        "max_retries": 3,
        "timeout_minutes": 60
    }


class YOLOOrchestrator:
    """Main orchestrator for YOLO mode with context refresh capabilities."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize YOLO orchestrator with context management and configuration."""
        self.state = YOLOState()
        self.defaults = YOLODefaults()
        
        # Initialize configuration manager
        self.config_manager = None
        if ConfigManager:
            try:
                self.config_manager = ConfigManager(config_path)
                self.config = self.config_manager.config
                logger.info(f"Configuration loaded from {config_path or 'default path'}")
                
                # Apply configuration to state
                if self.config:
                    mode_str = self.config.system.get('mode', 'active')
                    self.state.mode = YOLOMode(mode_str)
                    
                    # Set logging level
                    log_level = self.config.system.get('log_level', 'INFO')
                    logger.setLevel(getattr(logging, log_level))
            except Exception as e:
                logger.warning(f"Could not load configuration: {e}")
                self.config = None
        else:
            self.config = None
            
        # Fallback to old config loading if ConfigManager not available
        if not self.config:
            self.config = self._load_config(Path(config_path) if config_path else None)
        
        self.agent_handlers: Dict[AgentType, Callable] = {}
        self.phase_transitions = self._define_transitions()
        self.safety_checks = []
        
        # Thread-safety locks
        self._state_lock = asyncio.Lock()
        self._handoff_lock = asyncio.Lock()
        self._decision_lock = asyncio.Lock()
        self._context_lock = asyncio.Lock()
        
        # Initialize context refresh system with configuration
        self.context_manager = None
        if ContextRefreshSystem:
            try:
                self.context_manager = ContextRefreshSystem()
                
                # Apply agent token limits from configuration
                if self.config and hasattr(self.config, 'agent_limits'):
                    if hasattr(self.context_manager, 'AGENT_CONTEXT_LIMITS'):
                        for agent, limit in self.config.agent_limits.items():
                            self.context_manager.AGENT_CONTEXT_LIMITS[agent] = limit
                        logger.info("Applied agent token limits from configuration")
                
                logger.info("Context refresh system initialized")
            except Exception as e:
                logger.warning(f"Context refresh system unavailable: {e}")
        self._setup_logging()
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load YOLO configuration (fallback method)."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                if config_path.suffix == '.yaml':
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        return {}
        
    def _setup_logging(self):
        """Setup YOLO logging."""
        log_path = Path(__file__).parent / 'yolo.log'
        handler = logging.FileHandler(log_path)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    def _define_transitions(self) -> Dict[WorkflowPhase, WorkflowPhase]:
        """Define workflow phase transitions."""
        return {
            WorkflowPhase.PLANNING: WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.ARCHITECTURE: WorkflowPhase.STORY_CREATION,
            WorkflowPhase.STORY_CREATION: WorkflowPhase.DEVELOPMENT,
            WorkflowPhase.DEVELOPMENT: WorkflowPhase.TESTING,
            WorkflowPhase.TESTING: WorkflowPhase.REVIEW,
            WorkflowPhase.REVIEW: WorkflowPhase.DEPLOYMENT,
            WorkflowPhase.DEPLOYMENT: WorkflowPhase.COMPLETE
        }
        
    async def activate(self, initial_phase: WorkflowPhase = WorkflowPhase.PLANNING):
        """Activate YOLO mode."""
        if self.state.mode == YOLOMode.ACTIVE:
            logger.warning("YOLO mode already active")
            return
            
        self.state.mode = YOLOMode.ACTIVE
        self.state.current_phase = initial_phase
        self.state.started_at = datetime.now(timezone.utc)
        self.state.consecutive_errors = 0
        
        logger.info(f"YOLO mode activated at phase: {initial_phase}")
        self._record_decision(
            "activation",
            "mode",
            "active",
            f"YOLO mode activated for {initial_phase} phase"
        )
        
    def deactivate(self):
        """Deactivate YOLO mode."""
        self.state.mode = YOLOMode.OFF
        logger.info("YOLO mode deactivated")
        self._save_state()
        
    def pause(self):
        """Pause YOLO mode."""
        if self.state.mode == YOLOMode.ACTIVE:
            self.state.mode = YOLOMode.PAUSED
            logger.info("YOLO mode paused")
            
    def resume(self):
        """Resume YOLO mode."""
        if self.state.mode == YOLOMode.PAUSED:
            self.state.mode = YOLOMode.ACTIVE
            logger.info("YOLO mode resumed")
            
    def make_decision(
        self,
        decision_type: str,
        options: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Make an automated decision."""
        if self.state.mode != YOLOMode.ACTIVE:
            raise RuntimeError("YOLO mode not active")
            
        # Check for safety-critical decisions
        if self._is_safety_critical(decision_type):
            logger.warning(f"Safety-critical decision: {decision_type}")
            self.pause()
            raise RuntimeError(f"Human intervention required for: {decision_type}")
            
        # Use context-aware decision making
        if context:
            decision = self._contextual_decision(decision_type, options, context)
        else:
            decision = self._default_decision(decision_type, options)
            
        self._record_decision(
            decision_type,
            "automated",
            decision,
            f"Selected from options: {options}"
        )
        
        logger.info(f"YOLO decision for {decision_type}: {decision}")
        return decision
        
    def _contextual_decision(
        self,
        decision_type: str,
        options: List[str],
        context: Dict[str, Any]
    ) -> str:
        """Make decision based on context."""
        # Priority-based selection
        if "priority" in context:
            if context["priority"] == "high":
                return options[0] if options else ""
                
        # Performance-based selection
        if "performance" in context:
            if context["performance"] < 0.5:
                # Choose safer option
                return options[-1] if options else ""
                
        # Default to first option
        return options[0] if options else ""
        
    def _default_decision(self, decision_type: str, options: List[str]) -> str:
        """Make decision using defaults."""
        # Check technical defaults
        for key, value in self.defaults.TECHNICAL.items():
            if key in decision_type.lower():
                if value in options:
                    return value
                    
        # Check process defaults
        for key, value in self.defaults.PROCESS.items():
            if key in decision_type.lower():
                if str(value) in [str(o) for o in options]:
                    return str(value)
                    
        # Default to first option
        return options[0] if options else ""
        
    def _is_safety_critical(self, decision_type: str) -> bool:
        """Check if decision is safety-critical."""
        critical_keywords = [
            "delete", "drop", "remove", "destroy",
            "payment", "billing", "charge",
            "credential", "password", "secret", "key",
            "production", "deploy", "release"
        ]
        
        decision_lower = decision_type.lower()
        return any(keyword in decision_lower for keyword in critical_keywords)
        
    async def _record_decision(
        self,
        decision_type: str,
        choice_type: str,
        choice: str,
        reasoning: str
    ):
        """Record a decision made in YOLO mode (thread-safe)."""
        async with self._decision_lock:
            decision = YOLODecision(
                decision_id=f"{datetime.now(timezone.utc).timestamp()}_{len(self.state.decisions_made)}",
                decision_type=decision_type,
                choice_made=choice,
                reasoning=reasoning,
                agent=self.state.current_agent
            )
            
            self.state.decisions_made.append(decision)
            self.state.last_activity = datetime.now(timezone.utc)
        
    async def handoff(
        self,
        to_agent: AgentType,
        artifacts: Optional[Dict[str, List[str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> HandoffPackage:
        """Create handoff package for next agent with context refresh (thread-safe)."""
        async with self._handoff_lock:
            if not self.state.current_agent:
                raise RuntimeError("No current agent to handoff from")
            
            # Refresh context if context manager available
            refreshed_context = context or {}
            if self.context_manager:
                async with self._context_lock:
                    try:
                        # Add current context items
                        if context:
                            for key, value in context.items():
                                priority = ContextPriority.HIGH if key in ['current_task', 'errors'] else ContextPriority.MEDIUM
                                self.context_manager.add_context(
                                    key, value, priority, str(self.state.current_agent.value)
                                )
                        
                        # Get refreshed context for target agent
                        refreshed_context = self.context_manager.handoff_context(
                            from_agent=self.state.current_agent.value,
                            to_agent=to_agent.value
                        )
                        logger.info(f"Context refreshed for handoff to {to_agent.value}")
                    except Exception as e:
                        logger.warning(f"Context refresh failed: {e}")
                        refreshed_context = context or {}
                
            package = HandoffPackage(
                from_agent=self.state.current_agent,
                to_agent=to_agent,
                phase=self.state.current_phase,
                artifacts=artifacts or {},
                context=refreshed_context,
                next_action=self._determine_next_action(to_agent),
                yolo_mode=self.state.mode == YOLOMode.ACTIVE
            )
            
            # Update state atomically
            async with self._state_lock:
                self.state.current_agent = to_agent
                self.state.next_agent = self._determine_next_agent(to_agent)
            
            logger.info(f"Handoff from {package.from_agent} to {package.to_agent}")
            return package
        
    def _determine_next_action(self, agent: AgentType) -> str:
        """Determine next action for agent."""
        actions = {
            AgentType.PM: "create_prd",
            AgentType.ARCHITECT: "create_architecture",
            AgentType.PO: "shard_documents",
            AgentType.SM: "create_stories",
            AgentType.DEV: "implement_story",
            AgentType.QA: "test_implementation",
            AgentType.DEVOPS: "deploy_changes",
            AgentType.SECURITY: "security_scan",
            AgentType.DOCUMENTATION: "update_docs"
        }
        return actions.get(agent, "review")
        
    def _determine_next_agent(self, current: AgentType) -> Optional[AgentType]:
        """Determine next agent in workflow."""
        flow = {
            AgentType.PM: AgentType.ARCHITECT,
            AgentType.ARCHITECT: AgentType.PO,
            AgentType.PO: AgentType.SM,
            AgentType.SM: AgentType.DEV,
            AgentType.DEV: AgentType.QA,
            AgentType.QA: AgentType.SM,  # Loop back for next story
        }
        return flow.get(current)
        
    def handle_error(self, error: str, severity: str = "minor"):
        """Handle errors in YOLO mode."""
        self.state.errors_encountered.append(error)
        logger.error(f"YOLO error ({severity}): {error}")
        
        if severity == "critical":
            self.state.consecutive_errors += 1
            if self.state.consecutive_errors >= 3:
                self.state.mode = YOLOMode.ERROR
                logger.critical("YOLO mode stopped due to critical errors")
                
        elif severity == "major":
            self.pause()
            logger.warning("YOLO mode paused due to major error")
            
    def get_status(self) -> Dict[str, Any]:
        """Get current YOLO status with context information."""
        status = {
            "mode": self.state.mode.value,
            "phase": self.state.current_phase.value if self.state.current_phase else None,
            "current_agent": self.state.current_agent.value if self.state.current_agent else None,
            "next_agent": self.state.next_agent.value if self.state.next_agent else None,
            "decisions_made": len(self.state.decisions_made),
            "errors": len(self.state.errors_encountered),
            "progress": self._calculate_progress(),
            "uptime": self._calculate_uptime()
        }
        
        # Add context manager status if available
        if self.context_manager:
            try:
                context_status = self.context_manager.get_status()
                status["context"] = {
                    "total_items": context_status["total_context_items"],
                    "total_tokens": context_status["total_tokens"],
                    "agents": context_status["agent_contexts"]
                }
            except Exception as e:
                status["context"] = {"error": str(e)}
        
        # Add retry metrics if available
        if get_all_retry_metrics:
            retry_metrics = get_all_retry_metrics()
            if retry_metrics:
                status["retry_metrics"] = retry_metrics
        
        return status
        
    def _calculate_progress(self) -> float:
        """Calculate workflow progress percentage."""
        if not self.state.current_phase:
            return 0.0
            
        phases = list(WorkflowPhase)
        current_index = phases.index(self.state.current_phase)
        return (current_index / len(phases)) * 100
        
    def _calculate_uptime(self) -> str:
        """Calculate YOLO uptime."""
        if not self.state.started_at:
            return "0:00:00"
            
        delta = datetime.now(timezone.utc) - self.state.started_at
        return str(delta).split('.')[0]
    
    def get_retry_metrics(self) -> Dict[str, Any]:
        """Get retry metrics for monitoring."""
        if get_all_retry_metrics:
            return get_all_retry_metrics()
        return {"error": "Retry metrics not available"}
        
    async def _save_state(self):
        """Save YOLO state to file (thread-safe)."""
        async with self._state_lock:
            state_file = Path('.bmad-core/yolo/state.json')
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            state_data = {
                "mode": self.state.mode.value,
                "current_phase": self.state.current_phase.value if self.state.current_phase else None,
                "current_agent": self.state.current_agent.value if self.state.current_agent else None,
                "workflow_progress": self.state.workflow_progress,
                "decisions_count": len(self.state.decisions_made),
            "errors_count": len(self.state.errors_encountered),
            "started_at": self.state.started_at.isoformat() if self.state.started_at else None,
            "last_activity": self.state.last_activity.isoformat() if self.state.last_activity else None
        }
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
            
    def load_state(self):
        """Load YOLO state from file."""
        state_file = Path('.bmad-core/yolo/state.json')
        if state_file.exists():
            with open(state_file) as f:
                data = json.load(f)
                
            self.state.mode = YOLOMode(data.get("mode", "off"))
            
            if data.get("current_phase"):
                self.state.current_phase = WorkflowPhase(data["current_phase"])
                
            if data.get("current_agent"):
                self.state.current_agent = AgentType(data["current_agent"])
                
            self.state.workflow_progress = data.get("workflow_progress", {})
            
            logger.info("YOLO state loaded from file")
            

# Apply retry decorator to handoff method if available
if async_retry:
    YOLOOrchestrator.handoff = async_retry(
        max_attempts=3,
        backoff_factor=2.0,
        max_backoff=30.0,
        retriable_exceptions=(RuntimeError, ConnectionError, TimeoutError),
        circuit_breaker=True,
        circuit_threshold=5,
        circuit_cooldown=60
    )(YOLOOrchestrator.handoff)


class YOLOCommands:
    """Command interface for YOLO system."""
    
    def __init__(self, orchestrator: YOLOOrchestrator):
        """Initialize command interface."""
        self.orchestrator = orchestrator
        self.commands = {
            "*yolo on": self.enable_yolo,
            "*yolo off": self.disable_yolo,
            "*yolo status": self.show_status,
            "*yolo pause": self.pause_yolo,
            "*yolo resume": self.resume_yolo,
            "*workflow start": self.start_workflow,
            "*auto-handoff": self.auto_handoff,
            "*yolo decisions": self.show_decisions,
            "*yolo config": self.show_config
        }
        
    async def enable_yolo(self, args: List[str] = None):
        """Enable YOLO mode."""
        phase = WorkflowPhase.PLANNING
        if args and args[0] in [p.value for p in WorkflowPhase]:
            phase = WorkflowPhase(args[0])
            
        await self.orchestrator.activate(phase)
        return f"✅ YOLO mode activated at {phase.value} phase"
        
    def disable_yolo(self, args: List[str] = None):
        """Disable YOLO mode."""
        self.orchestrator.deactivate()
        return "❌ YOLO mode deactivated"
        
    def show_status(self, args: List[str] = None):
        """Show YOLO status."""
        status = self.orchestrator.get_status()
        return f"""
YOLO Status:
- Mode: {status['mode']}
- Phase: {status['phase']}
- Current Agent: {status['current_agent']}
- Next Agent: {status['next_agent']}
- Progress: {status['progress']:.1f}%
- Decisions Made: {status['decisions_made']}
- Errors: {status['errors']}
- Uptime: {status['uptime']}
"""
        
    def pause_yolo(self, args: List[str] = None):
        """Pause YOLO mode."""
        self.orchestrator.pause()
        return "⏸️ YOLO mode paused"
        
    def resume_yolo(self, args: List[str] = None):
        """Resume YOLO mode."""
        self.orchestrator.resume()
        return "▶️ YOLO mode resumed"
        
    async def start_workflow(self, args: List[str] = None):
        """Start automated workflow."""
        phase = WorkflowPhase.PLANNING
        if args and args[0] in [p.value for p in WorkflowPhase]:
            phase = WorkflowPhase(args[0])
            
        await self.orchestrator.activate(phase)
        return f"🚀 Workflow started at {phase.value} phase"
        
    async def auto_handoff(self, args: List[str] = None):
        """Execute automatic handoff."""
        if not args or args[0] not in [a.value for a in AgentType]:
            return "❌ Please specify target agent"
            
        to_agent = AgentType(args[0])
        package = await self.orchestrator.handoff(to_agent)
        
        return f"""
📦 Handoff Package Created:
- From: {package.from_agent.value}
- To: {package.to_agent.value}
- Phase: {package.phase.value}
- Next Action: {package.next_action}
- YOLO Mode: {package.yolo_mode}
"""
        
    def show_decisions(self, args: List[str] = None):
        """Show recent YOLO decisions."""
        decisions = self.orchestrator.state.decisions_made[-10:]
        if not decisions:
            return "No decisions made yet"
            
        output = "Recent YOLO Decisions:\n"
        for d in decisions:
            output += f"- {d.decision_type}: {d.choice_made} ({d.timestamp.strftime('%H:%M:%S')})\n"
            
        return output
        
    def show_config(self, args: List[str] = None):
        """Show YOLO configuration."""
        return f"""
YOLO Configuration:
Technical Defaults:
{json.dumps(self.orchestrator.defaults.TECHNICAL, indent=2)}

Process Defaults:
{json.dumps(self.orchestrator.defaults.PROCESS, indent=2)}

Workflow Defaults:
{json.dumps(self.orchestrator.defaults.WORKFLOW, indent=2)}
"""


async def main():
    """Main entry point for YOLO system."""
    orchestrator = YOLOOrchestrator()
    commands = YOLOCommands(orchestrator)
    
    # Example usage
    print(await commands.enable_yolo())
    print(commands.show_status())
    
    # Simulate workflow
    await orchestrator.activate(WorkflowPhase.PLANNING)
    
    # Make some decisions
    decision = orchestrator.make_decision(
        "framework_choice",
        ["fastapi", "django", "flask"],
        {"priority": "high"}
    )
    print(f"Framework chosen: {decision}")
    
    # Create handoff
    package = await orchestrator.handoff(AgentType.ARCHITECT)
    print(f"Handoff created: {package}")
    
    print(commands.show_status())


if __name__ == "__main__":
    asyncio.run(main())