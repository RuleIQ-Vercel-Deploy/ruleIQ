"""
Smart Evidence Collection System

AI-driven evidence collection prioritization and automation with intelligent
task scheduling for optimal compliance workflow management.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


class EvidencePriority(Enum):
    """Evidence collection priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class CollectionStatus(Enum):
    """Evidence collection status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class AutomationLevel(Enum):
    """Automation level for evidence collection."""

    FULLY_AUTOMATED = "fully_automated"
    SEMI_AUTOMATED = "semi_automated"
    MANUAL = "manual"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class EvidenceTask:
    """Individual evidence collection task."""

    task_id: str
    framework: str
    control_id: str
    evidence_type: str
    title: str
    description: str
    priority: EvidencePriority
    automation_level: AutomationLevel
    estimated_effort_hours: float
    dependencies: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    status: CollectionStatus = CollectionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectionPlan:
    """Evidence collection plan with prioritized tasks."""

    plan_id: str
    business_profile_id: str
    framework: str
    total_tasks: int
    estimated_total_hours: float
    completion_target_date: datetime
    tasks: List[EvidenceTask] = field(default_factory=list)
    automation_opportunities: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class SmartEvidenceCollector:
    """
    Smart Evidence Collection System

    Features:
    - AI-driven task prioritization
    - Intelligent automation detection
    - Dynamic scheduling and resource allocation
    - Progress tracking and optimization
    - Dependency management
    - Performance analytics
    """

    def __init__(self) -> None:
        self.active_plans: Dict[str, CollectionPlan] = {}
        self.task_queue: List[EvidenceTask] = []
        self.automation_rules: Dict[str, Dict[str, Any]] = {}

        # Initialize automation rules
        self._initialize_automation_rules()

        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "automation_success_rate": 0.0,
            "average_completion_time": 0.0,
            "efficiency_score": 0.0,
        }

    def _initialize_automation_rules(self) -> None:
        """Initialize automation rules for different evidence types."""
        self.automation_rules = {
            "policy_document": {
                "automation_level": AutomationLevel.SEMI_AUTOMATED,
                "tools": ["Document management systems", "Policy templates"],
                "effort_reduction": 0.6,
                "success_rate": 0.85,
            },
            "system_configuration": {
                "automation_level": AutomationLevel.FULLY_AUTOMATED,
                "tools": ["Configuration management tools", "Infrastructure as Code"],
                "effort_reduction": 0.8,
                "success_rate": 0.95,
            },
            "log_analysis": {
                "automation_level": AutomationLevel.FULLY_AUTOMATED,
                "tools": ["SIEM systems", "Log analysis tools"],
                "effort_reduction": 0.9,
                "success_rate": 0.9,
            },
            "vulnerability_assessment": {
                "automation_level": AutomationLevel.SEMI_AUTOMATED,
                "tools": ["Vulnerability scanners", "Security assessment tools"],
                "effort_reduction": 0.7,
                "success_rate": 0.8,
            },
            "training_record": {
                "automation_level": AutomationLevel.MANUAL,
                "tools": ["Learning management systems"],
                "effort_reduction": 0.3,
                "success_rate": 0.7,
            },
            "interview_documentation": {
                "automation_level": AutomationLevel.MANUAL,
                "tools": ["Interview templates", "Documentation tools"],
                "effort_reduction": 0.2,
                "success_rate": 0.6,
            },
        }

    async def create_collection_plan(
        self,
        business_profile_id: str,
        framework: str,
        business_context: Dict[str, Any],
        existing_evidence: Optional[List[Dict[str, Any]]] = None,
        target_completion_weeks: int = 12,
    ) -> CollectionPlan:
        """
        Create an intelligent evidence collection plan with AI-driven prioritization.

        Args:
            business_profile_id: Business profile identifier
            framework: Compliance framework (ISO27001, GDPR, etc.)
            business_context: Business context information
            existing_evidence: Already collected evidence
            target_completion_weeks: Target completion timeframe

        Returns:
            Comprehensive collection plan with prioritized tasks
        """
        try:
            # Generate evidence requirements
            evidence_requirements = await self._generate_evidence_requirements(
                framework, business_context
            )

            # Analyze existing evidence to identify gaps
            evidence_gaps = self._analyze_evidence_gaps(
                evidence_requirements, existing_evidence or []
            )

            # Create prioritized tasks
            tasks = await self._create_prioritized_tasks(evidence_gaps, business_context, framework)

            # Optimize task scheduling
            optimized_tasks = self._optimize_task_scheduling(tasks, target_completion_weeks)

            # Calculate automation opportunities
            automation_opportunities = self._calculate_automation_opportunities(optimized_tasks)

            # Create collection plan
            plan = CollectionPlan(
                plan_id=f"plan_{business_profile_id}_{framework}_{int(datetime.utcnow().timestamp())}",
                business_profile_id=business_profile_id,
                framework=framework,
                total_tasks=len(optimized_tasks),
                estimated_total_hours=sum(task.estimated_effort_hours for task in optimized_tasks),
                completion_target_date=datetime.utcnow() + timedelta(weeks=target_completion_weeks),
                tasks=optimized_tasks,
                automation_opportunities=automation_opportunities,
            )

            # Store the plan
            self.active_plans[plan.plan_id] = plan

            logger.info(f"Created collection plan {plan.plan_id} with {len(optimized_tasks)} tasks")
            return plan

        except Exception as e:
            logger.error(f"Error creating collection plan: {e}")
            raise

    async def _generate_evidence_requirements(
        self, framework: str, business_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate evidence requirements based on framework and business context."""

        # Framework-specific evidence requirements
        framework_requirements = {
            "ISO27001": [
                {
                    "control_id": "A.5.1.1",
                    "evidence_type": "policy_document",
                    "title": "Information Security Policy",
                },
                {
                    "control_id": "A.9.1.1",
                    "evidence_type": "policy_document",
                    "title": "Access Control Policy",
                },
                {
                    "control_id": "A.12.4.1",
                    "evidence_type": "log_analysis",
                    "title": "Event Logging",
                },
                {
                    "control_id": "A.12.6.1",
                    "evidence_type": "vulnerability_assessment",
                    "title": "Vulnerability Management",
                },
                {
                    "control_id": "A.7.2.2",
                    "evidence_type": "training_record",
                    "title": "Information Security Awareness",
                },
                {
                    "control_id": "A.16.1.1",
                    "evidence_type": "policy_document",
                    "title": "Incident Management Procedures",
                },
            ],
            "GDPR": [
                {
                    "control_id": "Art.5",
                    "evidence_type": "policy_document",
                    "title": "Data Processing Principles",
                },
                {
                    "control_id": "Art.13",
                    "evidence_type": "policy_document",
                    "title": "Privacy Notices",
                },
                {
                    "control_id": "Art.25",
                    "evidence_type": "system_configuration",
                    "title": "Privacy by Design",
                },
                {
                    "control_id": "Art.32",
                    "evidence_type": "system_configuration",
                    "title": "Security of Processing",
                },
                {
                    "control_id": "Art.33",
                    "evidence_type": "policy_document",
                    "title": "Breach Notification Procedures",
                },
            ],
            "SOC2": [
                {
                    "control_id": "CC6.1",
                    "evidence_type": "system_configuration",
                    "title": "Logical Access Controls",
                },
                {
                    "control_id": "CC6.2",
                    "evidence_type": "log_analysis",
                    "title": "System Monitoring",
                },
                {
                    "control_id": "CC7.1",
                    "evidence_type": "system_configuration",
                    "title": "System Operations",
                },
                {
                    "control_id": "CC8.1",
                    "evidence_type": "policy_document",
                    "title": "Change Management",
                },
            ],
        }

        base_requirements = framework_requirements.get(framework, [])

        # Customize based on business context
        industry = business_context.get("industry", "").lower()
        employee_count = business_context.get("employee_count", 0)

        # Add industry-specific requirements
        if industry in ["healthcare", "medical"]:
            base_requirements.extend(
                [
                    {
                        "control_id": "HIPAA-1",
                        "evidence_type": "policy_document",
                        "title": "HIPAA Privacy Policy",
                    },
                    {
                        "control_id": "HIPAA-2",
                        "evidence_type": "training_record",
                        "title": "HIPAA Training Records",
                    },
                ]
            )
        elif industry in ["finance", "banking"]:
            base_requirements.extend(
                [
                    {
                        "control_id": "SOX-1",
                        "evidence_type": "policy_document",
                        "title": "Financial Controls Policy",
                    },
                    {
                        "control_id": "PCI-1",
                        "evidence_type": "system_configuration",
                        "title": "Payment Card Security",
                    },
                ]
            )

        # Add size-specific requirements
        if employee_count >= 100:
            base_requirements.extend(
                [
                    {
                        "control_id": "HR-1",
                        "evidence_type": "policy_document",
                        "title": "HR Security Procedures",
                    },
                    {
                        "control_id": "VENDOR-1",
                        "evidence_type": "policy_document",
                        "title": "Vendor Management Policy",
                    },
                ]
            )

        return base_requirements

    def _analyze_evidence_gaps(
        self, requirements: List[Dict[str, Any]], existing_evidence: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze gaps between requirements and existing evidence."""

        # Create a set of existing evidence types and controls
        existing_controls = set()
        existing_types = set()

        for evidence in existing_evidence:
            if "control_id" in evidence:
                existing_controls.add(evidence["control_id"])
            if "evidence_type" in evidence:
                existing_types.add(evidence["evidence_type"])

        # Identify gaps
        gaps = []
        for req in requirements:
            control_id = req.get("control_id")
            evidence_type = req.get("evidence_type")

            # Check if this requirement is already satisfied
            if control_id not in existing_controls:
                gaps.append(req)
            elif evidence_type not in existing_types:
                # Control exists but different evidence type needed
                gaps.append(req)

        return gaps

    async def _create_prioritized_tasks(
        self, evidence_gaps: List[Dict[str, Any]], business_context: Dict[str, Any], framework: str
    ) -> List[EvidenceTask]:
        """Create prioritized evidence collection tasks."""

        tasks = []

        for i, gap in enumerate(evidence_gaps):
            # Determine automation level and effort
            evidence_type = gap.get("evidence_type", "unknown")
            automation_info = self.automation_rules.get(
                evidence_type, {"automation_level": AutomationLevel.MANUAL, "effort_reduction": 0.0}
            )

            # Calculate base effort
            base_effort = self._estimate_base_effort(evidence_type, business_context)

            # Apply automation reduction
            effort_reduction = automation_info.get("effort_reduction", 0.0)
            estimated_effort = base_effort * (1 - effort_reduction)

            # Determine priority
            priority = self._calculate_task_priority(gap, business_context, framework)

            # Create task
            task = EvidenceTask(
                task_id=f"task_{framework}_{gap.get('control_id', i)}_{int(datetime.utcnow().timestamp())}",
                framework=framework,
                control_id=gap.get("control_id", f"CTRL_{i}"),
                evidence_type=evidence_type,
                title=gap.get("title", f"Evidence Collection Task {i + 1}"),
                description=f"Collect evidence for {gap.get('title', 'compliance requirement')}",
                priority=priority,
                automation_level=automation_info.get("automation_level", AutomationLevel.MANUAL),
                estimated_effort_hours=estimated_effort,
                metadata={
                    "automation_tools": automation_info.get("tools", []),
                    "success_rate": automation_info.get("success_rate", 0.5),
                    "base_effort": base_effort,
                    "effort_reduction": effort_reduction,
                },
            )

            tasks.append(task)

        # Sort by priority and effort
        return sorted(tasks, key=lambda t: (t.priority.value, t.estimated_effort_hours))

    def _estimate_base_effort(self, evidence_type: str, business_context: Dict[str, Any]) -> float:
        """Estimate base effort hours for evidence collection."""

        # Base effort by evidence type
        base_efforts = {
            "policy_document": 8.0,
            "system_configuration": 4.0,
            "log_analysis": 6.0,
            "vulnerability_assessment": 12.0,
            "training_record": 3.0,
            "interview_documentation": 6.0,
            "audit_report": 16.0,
            "risk_assessment": 20.0,
        }

        base_effort = base_efforts.get(evidence_type, 8.0)

        # Adjust based on organization size
        employee_count = business_context.get("employee_count", 0)
        if employee_count >= 1000:
            base_effort *= 1.5  # Enterprise complexity
        elif employee_count >= 100:
            base_effort *= 1.2  # Medium organization
        elif employee_count < 10:
            base_effort *= 0.7  # Small organization

        return base_effort

    def _calculate_task_priority(
        self, gap: Dict[str, Any], business_context: Dict[str, Any], framework: str
    ) -> EvidencePriority:
        """Calculate task priority based on multiple factors."""

        # High priority controls by framework
        high_priority_controls = {
            "ISO27001": ["A.5.1.1", "A.9.1.1", "A.16.1.1"],
            "GDPR": ["Art.5", "Art.32", "Art.33"],
            "SOC2": ["CC6.1", "CC6.2"],
        }

        control_id = gap.get("control_id", "")
        evidence_type = gap.get("evidence_type", "")

        # Check if it's a high priority control
        if control_id in high_priority_controls.get(framework, []):
            return EvidencePriority.CRITICAL

        # Policy documents are generally high priority
        if evidence_type == "policy_document":
            return EvidencePriority.HIGH

        # System configurations are medium-high priority
        if evidence_type in ["system_configuration", "log_analysis"]:
            return EvidencePriority.MEDIUM

        # Training and documentation are lower priority
        if evidence_type in ["training_record", "interview_documentation"]:
            return EvidencePriority.LOW

        return EvidencePriority.MEDIUM

    def _optimize_task_scheduling(
        self, tasks: List[EvidenceTask], target_weeks: int
    ) -> List[EvidenceTask]:
        """Optimize task scheduling based on dependencies and resources."""

        # Calculate weekly capacity (assuming 40 hours per week)
        weekly_capacity = 40.0
        weekly_capacity * target_weeks

        # Sort tasks by priority and dependencies
        optimized_tasks = []
        remaining_tasks = tasks.copy()

        # Schedule critical and high priority tasks first
        for priority in [EvidencePriority.CRITICAL, EvidencePriority.HIGH]:
            priority_tasks = [t for t in remaining_tasks if t.priority == priority]
            optimized_tasks.extend(priority_tasks)
            remaining_tasks = [t for t in remaining_tasks if t.priority != priority]

        # Schedule remaining tasks by effort (quick wins first)
        remaining_tasks.sort(key=lambda t: t.estimated_effort_hours)
        optimized_tasks.extend(remaining_tasks)

        # Set due dates based on scheduling
        current_date = datetime.utcnow()
        accumulated_effort = 0.0

        for task in optimized_tasks:
            accumulated_effort += task.estimated_effort_hours
            weeks_needed = accumulated_effort / weekly_capacity
            task.due_date = current_date + timedelta(weeks=weeks_needed)

        return optimized_tasks

    def _calculate_automation_opportunities(self, tasks: List[EvidenceTask]) -> Dict[str, Any]:
        """Calculate automation opportunities across all tasks."""

        total_tasks = len(tasks)
        automated_tasks = len(
            [
                t
                for t in tasks
                if t.automation_level
                in [AutomationLevel.FULLY_AUTOMATED, AutomationLevel.SEMI_AUTOMATED]
            ]
        )

        total_manual_effort = sum(
            t.metadata.get("base_effort", t.estimated_effort_hours) for t in tasks
        )
        total_optimized_effort = sum(t.estimated_effort_hours for t in tasks)

        effort_savings = total_manual_effort - total_optimized_effort
        savings_percentage = (
            (effort_savings / total_manual_effort * 100) if total_manual_effort > 0 else 0
        )

        return {
            "total_tasks": total_tasks,
            "automatable_tasks": automated_tasks,
            "automation_percentage": round(automated_tasks / total_tasks * 100, 1)
            if total_tasks > 0
            else 0,
            "effort_savings_hours": round(effort_savings, 1),
            "effort_savings_percentage": round(savings_percentage, 1),
            "recommended_tools": self._get_recommended_automation_tools(tasks),
        }

    def _get_recommended_automation_tools(self, tasks: List[EvidenceTask]) -> List[str]:
        """Get recommended automation tools based on task types."""

        tools = set()
        for task in tasks:
            task_tools = task.metadata.get("automation_tools", [])
            tools.update(task_tools)

        return list(tools)

    async def get_collection_plan(self, plan_id: str) -> Optional[CollectionPlan]:
        """Get a collection plan by ID."""
        return self.active_plans.get(plan_id)

    async def update_task_status(
        self,
        plan_id: str,
        task_id: str,
        status: CollectionStatus,
        completion_notes: Optional[str] = None,
    ) -> bool:
        """Update the status of a specific task."""

        plan = self.active_plans.get(plan_id)
        if not plan:
            return False

        for task in plan.tasks:
            if task.task_id == task_id:
                task.status = status
                if completion_notes:
                    task.metadata["completion_notes"] = completion_notes

                # Update metrics if completed
                if status == CollectionStatus.COMPLETED:
                    self.metrics["tasks_completed"] += 1

                logger.info(f"Updated task {task_id} status to {status.value}")
                return True

        return False

    async def get_next_priority_tasks(self, plan_id: str, limit: int = 5) -> List[EvidenceTask]:
        """Get the next priority tasks for execution."""

        plan = self.active_plans.get(plan_id)
        if not plan:
            return []

        # Get pending tasks sorted by priority and due date
        pending_tasks = [task for task in plan.tasks if task.status == CollectionStatus.PENDING]

        # Sort by priority and due date
        pending_tasks.sort(
            key=lambda t: (t.priority.value, t.due_date or datetime.max, t.estimated_effort_hours)
        )

        return pending_tasks[:limit]


# Global smart evidence collector instance
smart_evidence_collector = SmartEvidenceCollector()


async def get_smart_evidence_collector() -> SmartEvidenceCollector:
    """Get the global smart evidence collector instance."""
    return smart_evidence_collector
