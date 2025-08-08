"""
Advanced Safety & Configuration Manager for AI Services

Provides enterprise-grade safety settings, content filtering, and compliance-focused
safety management with dynamic configuration and audit capabilities.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from uuid import uuid4

from google.generativeai.types import HarmBlockThreshold, HarmCategory
from config.logging_config import get_logger

logger = get_logger(__name__)


class SafetyLevel(Enum):
    """Safety levels for different operational contexts."""

    PERMISSIVE = "permissive"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class ContentType(Enum):
    """Content types for safety configuration."""

    ASSESSMENT_GUIDANCE = "assessment_guidance"
    COMPLIANCE_ADVICE = "compliance_advice"
    REGULATORY_INTERPRETATION = "regulatory_interpretation"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    POLICY_GENERATION = "policy_generation"
    EVIDENCE_CLASSIFICATION = "evidence_classification"
    COMPLIANCE_ANALYSIS = "compliance_analysis"
    GENERAL_QUESTION = "general_question"
    GENERAL_INQUIRY = "general_inquiry"


class SafetyDecision(Enum):
    """Safety decision outcomes."""

    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"


@dataclass
class SafetyProfile:
    """Safety configuration profile."""

    name: str
    level: SafetyLevel
    content_types: List[ContentType]

    # Google AI Safety Settings
    harassment_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    hate_speech_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    sexually_explicit_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    dangerous_content_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE

    # Confidence thresholds
    min_confidence_threshold: float = 0.7
    escalation_confidence_threshold: float = 0.5

    # Content filtering
    blocked_keywords: List[str] = field(default_factory=list)
    allowed_keywords: List[str] = field(default_factory=list)
    require_citations: bool = True

    # Compliance-specific settings
    require_regulatory_context: bool = False
    enable_audit_logging: bool = True
    max_response_length: int = 5000

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SafetyDecisionRecord:
    """Record of a safety decision for audit purposes."""

    decision_id: str
    content_type: ContentType
    safety_profile: str
    input_content: str
    decision: SafetyDecision
    confidence_score: float
    reasoning: str
    applied_filters: List[str]
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyMetrics:
    """Safety system metrics."""

    total_decisions: int = 0
    allowed_count: int = 0
    blocked_count: int = 0
    modified_count: int = 0
    escalated_count: int = 0
    avg_confidence_score: float = 0.0
    low_confidence_rate: float = 0.0
    profile_usage: Dict[str, int] = field(default_factory=dict)
    content_type_distribution: Dict[str, int] = field(default_factory=dict)


def require_permission(permission: str):
    """Decorator for role-based access control."""

    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # Check if user has required permission
            user_permissions = self.role_permissions.get(self.user_role, {})
            if not user_permissions.get(permission, False):
                logger.warning(
                    f"Access denied: User {self.user_id} with role {self.user_role} "
                    f"lacks permission '{permission}' for {func.__name__}"
                )
                raise PermissionError(
                    f"Insufficient permissions. Required: {permission}, "
                    f"Current role: {self.user_role}"
                )
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


class AdvancedSafetyManager:
    """
    Advanced safety and configuration manager for AI services.

    Provides enterprise-grade safety settings, dynamic configuration,
    content filtering, and comprehensive audit capabilities.
    """

    def __init__(self, user_context: Optional[Dict[str, Any]] = None) -> None:
        self.safety_profiles: Dict[str, SafetyProfile] = {}
        self.decision_history: List[SafetyDecisionRecord] = []
        self.metrics = SafetyMetrics()

        # Role-based authorization
        self.user_context = user_context or {}
        self.user_role = self.user_context.get("role", "viewer")
        self.user_id = self.user_context.get("user_id")
        self.organization_id = self.user_context.get("organization_id")

        # Define role permissions
        self.role_permissions = {
            "viewer": {
                "can_view_metrics": True,
                "can_view_audit_trail": False,
                "can_create_profiles": False,
                "can_modify_settings": False,
                "can_override_safety": False,
                "max_content_risk_level": "low",
            },
            "user": {
                "can_view_metrics": True,
                "can_view_audit_trail": True,
                "can_create_profiles": False,
                "can_modify_settings": False,
                "can_override_safety": False,
                "max_content_risk_level": "medium",
            },
            "compliance_officer": {
                "can_view_metrics": True,
                "can_view_audit_trail": True,
                "can_create_profiles": True,
                "can_modify_settings": True,
                "can_override_safety": False,
                "max_content_risk_level": "high",
            },
            "admin": {
                "can_view_metrics": True,
                "can_view_audit_trail": True,
                "can_create_profiles": True,
                "can_modify_settings": True,
                "can_override_safety": True,
                "max_content_risk_level": "critical",
            },
        }

        # Initialize default profiles
        self._initialize_default_profiles()

        # Content filters
        self.global_blocked_patterns = [
            r"\b(?:hack|exploit|bypass|circumvent)\b.*(?:regulation|compliance|law)\b",
            r"\b(?:illegal|unlawful|fraudulent)\b.*(?:advice|guidance|recommendation)\b",
            r"\b(?:ignore|skip|avoid)\b.*(?:requirement|obligation|mandate)\b",
        ]

        self.compliance_keywords = [
            "gdpr",
            "iso27001",
            "sox",
            "hipaa",
            "pci dss",
            "regulation",
            "compliance",
            "audit",
            "control",
            "policy",
            "procedure",
        ]

        logger.info(
            f"Initialized AdvancedSafetyManager for user {self.user_id} with role {self.user_role}"
        )

    def _initialize_default_profiles(self) -> None:
        """Initialize default safety profiles for different use cases."""

        # Permissive profile for internal testing
        self.safety_profiles["permissive"] = SafetyProfile(
            name="Permissive Testing",
            level=SafetyLevel.PERMISSIVE,
            content_types=[ContentType.GENERAL_INQUIRY],
            harassment_threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            hate_speech_threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            sexually_explicit_threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            dangerous_content_threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
            min_confidence_threshold=0.5,
            require_citations=False,
            enable_audit_logging=True,
        )

        # Standard profile for general compliance assistance
        self.safety_profiles["standard"] = SafetyProfile(
            name="Standard Compliance",
            level=SafetyLevel.STANDARD,
            content_types=[
                ContentType.ASSESSMENT_GUIDANCE,
                ContentType.COMPLIANCE_ADVICE,
                ContentType.GENERAL_INQUIRY,
            ],
            harassment_threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            hate_speech_threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            sexually_explicit_threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            dangerous_content_threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            min_confidence_threshold=0.7,
            require_citations=True,
            enable_audit_logging=True,
        )

        # Strict profile for regulatory interpretation
        self.safety_profiles["strict"] = SafetyProfile(
            name="Strict Regulatory",
            level=SafetyLevel.STRICT,
            content_types=[ContentType.REGULATORY_INTERPRETATION, ContentType.POLICY_GENERATION],
            harassment_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            hate_speech_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            sexually_explicit_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            dangerous_content_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            min_confidence_threshold=0.85,
            escalation_confidence_threshold=0.7,
            require_regulatory_context=True,
            require_citations=True,
            enable_audit_logging=True,
            max_response_length=3000,
        )

        # Enterprise profile for maximum safety
        self.safety_profiles["enterprise"] = SafetyProfile(
            name="Enterprise Maximum Safety",
            level=SafetyLevel.ENTERPRISE,
            content_types=list(ContentType),
            harassment_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            hate_speech_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            sexually_explicit_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            dangerous_content_threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            min_confidence_threshold=0.9,
            escalation_confidence_threshold=0.8,
            require_regulatory_context=True,
            require_citations=True,
            enable_audit_logging=True,
            max_response_length=2500,
            blocked_keywords=[
                "hack",
                "exploit",
                "bypass",
                "circumvent",
                "illegal",
                "unlawful",
                "fraudulent",
                "ignore",
                "skip",
                "avoid",
            ],
        )

    def check_permission(self, permission: str) -> bool:
        """Check if current user has a specific permission."""
        if not self.user_role:
            return False

        user_permissions = self.role_permissions.get(self.user_role, {})
        return user_permissions.get(permission, False)

    def require_permission(self, permission: str, action_description: str = None) -> None:
        """Require a specific permission or raise an exception."""
        if not self.check_permission(permission):
            action = action_description or permission
            raise PermissionError(
                f"User role '{self.user_role}' does not have permission for: {action}"
            )

    def get_max_risk_level(self) -> str:
        """Get the maximum content risk level allowed for current user."""
        user_permissions = self.role_permissions.get(self.user_role, {})
        return user_permissions.get("max_content_risk_level", "low")

    def can_access_content_type(self, content_type: ContentType) -> bool:
        """Check if user can access specific content type based on risk level."""
        max_risk = self.get_max_risk_level()

        # Define content type risk levels
        content_risk_levels = {
            ContentType.GENERAL_QUESTION: "low",
            ContentType.REGULATORY_INTERPRETATION: "high",
            ContentType.POLICY_GENERATION: "high",
            ContentType.EVIDENCE_CLASSIFICATION: "medium",
            ContentType.ASSESSMENT_GUIDANCE: "medium",
            ContentType.COMPLIANCE_ANALYSIS: "high",
        }

        risk_hierarchy = ["low", "medium", "high", "critical"]
        content_risk = content_risk_levels.get(content_type, "medium")
        max_risk_index = risk_hierarchy.index(max_risk)
        content_risk_index = risk_hierarchy.index(content_risk)

        return content_risk_index <= max_risk_index

    def get_role_specific_safety_profile(self, content_type: ContentType) -> str:
        """Get safety profile appropriate for user role and content type."""
        if self.user_role == "admin" and self.check_permission("can_override_safety"):
            return "permissive"
        elif self.user_role == "compliance_officer":
            return "balanced"
        elif content_type in [ContentType.REGULATORY_INTERPRETATION, ContentType.POLICY_GENERATION]:
            return "strict"
        else:
            return "standard"

    def log_authorization_decision(
        self, action: str, permission: str, granted: bool, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log authorization decisions for audit purposes."""
        decision_record = SafetyDecisionRecord(
            decision_id=str(uuid4()),
            user_id=self.user_id,
            content_type=ContentType.GENERAL_QUESTION if context and context.get("content_type") == "unknown" else ContentType.GENERAL_INQUIRY,
            safety_profile="standard",
            input_content=f"AUTHORIZATION: {action}",
            decision=SafetyDecision.ALLOW if granted else SafetyDecision.BLOCK,
            confidence_score=1.0,
            reasoning=f"Permission '{permission}' {'granted' if granted else 'denied'} for role '{self.user_role}'",
            applied_filters=[],
            timestamp=datetime.now(),
            metadata={
                "permission_requested": permission,
                "user_context": self.user_context,
                "additional_context": context or {},
            },
        )

        self.decision_history.append(decision_record)

        logger.info(
            f"Authorization decision - User: {self.user_id}, Role: {self.user_role}, "
            f"Action: {action}, Permission: {permission}, Granted: {granted}"
        )

    def get_content_filters_for_role(self) -> Dict[str, Any]:
        """Get content filters appropriate for user role."""
        base_filters = {
            "blocked_patterns": self.global_blocked_patterns.copy(),
            "compliance_keywords": self.compliance_keywords.copy(),
        }

        if self.user_role == "viewer":
            # Most restrictive for viewers
            base_filters["blocked_patterns"].extend(
                [
                    r"\\b(?:internal|confidential|restricted)\\b",
                    r"\\b(?:privileged|sensitive)\\b.*(?:information|data)\\b",
                ]
            )
        elif self.user_role == "user":
            # Standard restrictions
            base_filters["blocked_patterns"].extend(
                [r"\\b(?:confidential|restricted)\\b.*(?:internal)\\b"]
            )
        elif self.user_role == "compliance_officer":
            # Fewer restrictions, but still some safeguards
            pass
        elif self.user_role == "admin":
            # Minimal restrictions for admins
            if self.check_permission("can_override_safety"):
                base_filters["blocked_patterns"] = []

        return base_filters

    def get_safety_settings(
        self,
        content_type: ContentType,
        profile_name: str = "standard",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[HarmCategory, HarmBlockThreshold]:
        """
        Get Google AI safety settings for a specific content type and profile.

        Args:
            content_type: Type of content being processed
            profile_name: Name of safety profile to use
            context: Additional context for dynamic adjustment

        Returns:
            Dictionary of safety settings for Google AI
        """
        profile = self.safety_profiles.get(profile_name, self.safety_profiles["standard"])

        # Dynamic adjustment based on context
        settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: profile.harassment_threshold,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: profile.hate_speech_threshold,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: profile.sexually_explicit_threshold,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: profile.dangerous_content_threshold,
        }

        # Adjust for high-risk content types
        if content_type in [ContentType.REGULATORY_INTERPRETATION, ContentType.POLICY_GENERATION]:
            for category in settings:
                if settings[category] == HarmBlockThreshold.BLOCK_ONLY_HIGH:
                    settings[category] = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE

        return settings

    def evaluate_content_safety(
        self,
        input_content: str,
        response_content: str,
        content_type: ContentType,
        confidence_score: float,
        profile_name: str = "standard",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> SafetyDecisionRecord:
        """
        Evaluate content safety with role-based authorization.

        Args:
            input_content: User input content
            response_content: AI response content
            content_type: Type of content
            confidence_score: AI response confidence score
            profile_name: Safety profile to use
            user_id: Optional user ID for audit
            session_id: Optional session ID for audit

        Returns:
            Safety decision record

        Raises:
            PermissionError: If user lacks authorization for content type
        """
        # Step 1: Check role-based authorization for content type
        if not self.can_access_content_type(content_type):
            self.log_authorization_decision(
                action="evaluate_content_safety",
                permission="access_content_type",
                granted=False,
                context={"content_type": content_type.value},
            )
            raise PermissionError(
                f"User role '{self.user_role}' cannot access content type '{content_type.value}'"
            )

        # Step 2: Log successful authorization
        self.log_authorization_decision(
            action="evaluate_content_safety",
            permission="access_content_type",
            granted=True,
            context={"content_type": content_type.value},
        )

        # Step 3: Get role-appropriate safety profile
        role_appropriate_profile = self.get_role_specific_safety_profile(content_type)
        if profile_name != role_appropriate_profile:
            logger.info(
                f"Adjusting safety profile from '{profile_name}' to '{role_appropriate_profile}' "
                f"for user role '{self.user_role}'"
            )
            profile_name = role_appropriate_profile

        # Step 4: Get role-specific content filters
        self.get_content_filters_for_role()
        profile = self.safety_profiles.get(profile_name, self.safety_profiles["standard"])

        # Check if user can evaluate content at this risk level
        user_permissions = self.role_permissions.get(self.user_role, {})
        max_risk_level = user_permissions.get("max_content_risk_level", "low")

        # Map profile levels to risk levels for comparison
        risk_level_map = {
            "minimal": "low",
            "standard": "medium",
            "strict": "high",
            "regulatory": "critical",
        }

        profile_risk = risk_level_map.get(profile.level.value, "medium")
        allowed_levels = {
            "low": ["low"],
            "medium": ["low", "medium"],
            "high": ["low", "medium", "high"],
            "critical": ["low", "medium", "high", "critical"],
        }

        if profile_risk not in allowed_levels.get(max_risk_level, ["low"]):
            logger.warning(
                f"User {user_id or self.user_id} with role {self.user_role} attempted to use "
                f"profile '{profile_name}' exceeding allowed risk level"
            )
            # Downgrade to highest allowed profile
            if max_risk_level == "low":
                profile = self.safety_profiles["minimal"]
                profile_name = "minimal"
            elif max_risk_level == "medium":
                profile = self.safety_profiles["standard"]
                profile_name = "standard"
            elif max_risk_level == "high":
                profile = self.safety_profiles["strict"]
                profile_name = "strict"

        decision_id = str(uuid4())
        applied_filters = []

        # Initial decision is to allow
        decision = SafetyDecision.ALLOW
        reasoning = "Content passed initial safety evaluation"

        # Check confidence threshold
        if confidence_score < profile.escalation_confidence_threshold:
            decision = SafetyDecision.ESCALATE
            reasoning = f"Low confidence score: {confidence_score:.3f} < {profile.escalation_confidence_threshold}"
            applied_filters.append("confidence_threshold")

        elif confidence_score < profile.min_confidence_threshold:
            decision = SafetyDecision.BLOCK
            reasoning = f"Confidence below minimum threshold: {confidence_score:.3f} < {profile.min_confidence_threshold}"
            applied_filters.append("min_confidence")

        # Check blocked keywords
        blocked_found = self._check_blocked_content(input_content + " " + response_content, profile)
        if blocked_found:
            if decision == SafetyDecision.ALLOW:
                decision = SafetyDecision.MODIFY
                reasoning = f"Blocked keywords found: {', '.join(blocked_found)}"
            applied_filters.append("keyword_filter")

        # Check response length
        if len(response_content) > profile.max_response_length:
            if decision == SafetyDecision.ALLOW:
                decision = SafetyDecision.MODIFY
                reasoning = (
                    f"Response too long: {len(response_content)} > {profile.max_response_length}"
                )
            applied_filters.append("length_filter")

        # Check regulatory context requirement
        if profile.require_regulatory_context and content_type in [
            ContentType.REGULATORY_INTERPRETATION,
            ContentType.COMPLIANCE_ADVICE,
        ]:
            if not self._has_regulatory_context(response_content):
                if decision == SafetyDecision.ALLOW:
                    decision = SafetyDecision.MODIFY
                    reasoning = "Missing required regulatory context"
                applied_filters.append("regulatory_context")

        # Check citation requirement
        if profile.require_citations and not self._has_citations(response_content):
            if decision == SafetyDecision.ALLOW:
                decision = SafetyDecision.MODIFY
                reasoning = "Missing required citations"
            applied_filters.append("citation_requirement")

        # Create decision record
        record = SafetyDecisionRecord(
            decision_id=decision_id,
            content_type=content_type,
            safety_profile=profile_name,
            input_content=input_content[:500],  # Truncate for storage
            decision=decision,
            confidence_score=confidence_score,
            reasoning=reasoning,
            applied_filters=applied_filters,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            metadata={
                "response_length": len(response_content),
                "profile_level": profile.level.value,
            },
        )

        # Store decision and update metrics
        if profile.enable_audit_logging:
            self.decision_history.append(record)
            # Keep only last 10,000 decisions
            if len(self.decision_history) > 10000:
                self.decision_history = self.decision_history[-10000:]

        self._update_metrics(record)

        logger.info(f"Safety decision {decision_id}: {decision.value} - {reasoning}")

        return record

    def _check_blocked_content(self, content: str, profile: SafetyProfile) -> List[str]:
        """Check for blocked keywords and patterns."""
        blocked_found = []
        content_lower = content.lower()

        # Check profile-specific blocked keywords
        for keyword in profile.blocked_keywords:
            if keyword.lower() in content_lower:
                blocked_found.append(keyword)

        # Check global patterns using regex
        import re

        for pattern in self.global_blocked_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                blocked_found.append(f"pattern:{pattern[:20]}...")

        return blocked_found

    def _has_regulatory_context(self, content: str) -> bool:
        """Check if content has appropriate regulatory context."""
        content_lower = content.lower()

        # Look for compliance-related keywords
        compliance_mentions = sum(
            1 for keyword in self.compliance_keywords if keyword in content_lower
        )

        # Look for regulatory structure
        regulatory_indicators = [
            "regulation",
            "requirement",
            "compliance",
            "standard",
            "framework",
            "guideline",
            "mandate",
            "obligation",
        ]

        regulatory_mentions = sum(
            1 for indicator in regulatory_indicators if indicator in content_lower
        )

        # Require at least 2 compliance mentions and 1 regulatory indicator
        return compliance_mentions >= 2 and regulatory_mentions >= 1

    def _has_citations(self, content: str) -> bool:
        """Check if content has appropriate citations or references."""
        # Look for citation patterns
        citation_patterns = [
            r"\b(?:according to|as per|under|pursuant to)\b.*\b(?:regulation|standard|law|act)\b",
            r"\b(?:iso|gdpr|sox|hipaa|pci|nist)\b.*\d+",
            r"\b(?:article|section|clause|paragraph)\b.*\d+",
            r"\b(?:reference|see|cf\.)\b.*\d+",
        ]

        import re

        for pattern in citation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def _update_metrics(self, record: SafetyDecisionRecord) -> None:
        """Update safety metrics."""
        self.metrics.total_decisions += 1

        if record.decision == SafetyDecision.ALLOW:
            self.metrics.allowed_count += 1
        elif record.decision == SafetyDecision.BLOCK:
            self.metrics.blocked_count += 1
        elif record.decision == SafetyDecision.MODIFY:
            self.metrics.modified_count += 1
        elif record.decision == SafetyDecision.ESCALATE:
            self.metrics.escalated_count += 1

        # Update averages
        total_confidence = (
            self.metrics.avg_confidence_score * (self.metrics.total_decisions - 1)
            + record.confidence_score
        )
        self.metrics.avg_confidence_score = total_confidence / self.metrics.total_decisions

        # Update profile usage
        if record.safety_profile not in self.metrics.profile_usage:
            self.metrics.profile_usage[record.safety_profile] = 0
        self.metrics.profile_usage[record.safety_profile] += 1

        # Update content type distribution
        content_type_key = record.content_type.value
        if content_type_key not in self.metrics.content_type_distribution:
            self.metrics.content_type_distribution[content_type_key] = 0
        self.metrics.content_type_distribution[content_type_key] += 1

        # Calculate low confidence rate
        low_confidence_count = sum(
            1 for r in self.decision_history[-1000:] if r.confidence_score < 0.7
        )
        self.metrics.low_confidence_rate = low_confidence_count / min(
            1000, len(self.decision_history)
        )

    def modify_response_content(self, content: str, applied_filters: List[str]) -> str:
        """Modify response content based on applied filters."""
        modified_content = content

        if "length_filter" in applied_filters:
            # Truncate while preserving sentence structure
            sentences = modified_content.split(". ")
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence) + 1 <= 2500:  # Safety margin
                    truncated += sentence + ". "
                else:
                    break
            modified_content = truncated.strip()

        if "keyword_filter" in applied_filters:
            # Replace blocked keywords with placeholders
            for keyword in ["hack", "exploit", "bypass", "circumvent"]:
                modified_content = modified_content.replace(keyword, "[RESTRICTED]")

        if "citation_requirement" in applied_filters:
            modified_content += "\n\n[Note: This guidance should be verified against current regulatory requirements and legal counsel should be consulted for specific compliance decisions.]"

        if "regulatory_context" in applied_filters:
            modified_content += "\n\n[Disclaimer: This information is provided for general guidance only. Specific regulatory requirements may vary by jurisdiction and industry. Please consult relevant regulations and qualified compliance professionals.]"

        return modified_content

    def get_safety_metrics(self) -> Dict[str, Any]:
        """Get comprehensive safety metrics with role-based access control."""
        # Check permission to view metrics
        self.require_permission("can_view_metrics", "view safety metrics")

        self.log_authorization_decision(
            action="get_safety_metrics", permission="can_view_metrics", granted=True
        )
        if self.metrics.total_decisions == 0:
            return {
                "total_decisions": 0,
                "decision_rates": {
                    "allowed_rate": 0.0,
                    "blocked_rate": 0.0,
                    "modified_rate": 0.0,
                    "escalated_rate": 0.0,
                },
                "confidence_metrics": {"average_confidence": 0.0, "low_confidence_rate": 0.0},
                "profile_usage": {},
                "content_type_distribution": {},
            }

        total = self.metrics.total_decisions

        return {
            "total_decisions": total,
            "decision_rates": {
                "allowed_rate": round(self.metrics.allowed_count / total, 3),
                "blocked_rate": round(self.metrics.blocked_count / total, 3),
                "modified_rate": round(self.metrics.modified_count / total, 3),
                "escalated_rate": round(self.metrics.escalated_count / total, 3),
            },
            "confidence_metrics": {
                "average_confidence": round(self.metrics.avg_confidence_score, 3),
                "low_confidence_rate": round(self.metrics.low_confidence_rate, 3),
            },
            "profile_usage": self.metrics.profile_usage.copy(),
            "content_type_distribution": self.metrics.content_type_distribution.copy(),
            "recent_decisions": len(
                [
                    r
                    for r in self.decision_history
                    if (datetime.now() - r.timestamp).total_seconds() < 3600
                ]
            ),
        }

    async def get_audit_trail(
        self,
        hours: int = 24,
        user_id: Optional[str] = None,
        content_type: Optional[ContentType] = None,
    ) -> List[Dict[str, Any]]:
        """Get audit trail for safety decisions."""
        # Check permission
        self.require_permission("can_view_audit_trail", "view audit trail")
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_records = [
            record
            for record in self.decision_history
            if record.timestamp >= cutoff_time
            and (user_id is None or record.user_id == user_id)
            and (content_type is None or record.content_type == content_type)
        ]

        return [
            {
                "decision_id": record.decision_id,
                "timestamp": record.timestamp.isoformat(),
                "content_type": record.content_type.value,
                "decision": record.decision.value,
                "confidence_score": record.confidence_score,
                "reasoning": record.reasoning,
                "applied_filters": record.applied_filters,
                "safety_profile": record.safety_profile,
                "user_id": record.user_id,
                "session_id": record.session_id,
            }
            for record in filtered_records
        ]

    async def create_custom_profile(
        self, name: str, base_profile: str = "standard", overrides: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a custom safety profile."""
        # Check permission
        self.require_permission("can_create_profiles", "create custom safety profiles")
        if base_profile not in self.safety_profiles:
            raise ValueError(f"Base profile '{base_profile}' not found")

        base = self.safety_profiles[base_profile]

        # Create new profile with overrides
        profile_data = {
            "name": name,
            "level": base.level,
            "content_types": base.content_types.copy(),
            "harassment_threshold": base.harassment_threshold,
            "hate_speech_threshold": base.hate_speech_threshold,
            "sexually_explicit_threshold": base.sexually_explicit_threshold,
            "dangerous_content_threshold": base.dangerous_content_threshold,
            "min_confidence_threshold": base.min_confidence_threshold,
            "escalation_confidence_threshold": base.escalation_confidence_threshold,
            "blocked_keywords": base.blocked_keywords.copy(),
            "allowed_keywords": base.allowed_keywords.copy(),
            "require_citations": base.require_citations,
            "require_regulatory_context": base.require_regulatory_context,
            "enable_audit_logging": base.enable_audit_logging,
            "max_response_length": base.max_response_length,
        }

        # Apply overrides
        if overrides:
            profile_data.update(overrides)

        # Create profile
        custom_profile = SafetyProfile(**profile_data)
        profile_key = name.lower().replace(" ", "_")
        self.safety_profiles[profile_key] = custom_profile

        logger.info(f"User {self.user_id} created custom safety profile: {name}")

        return profile_key

    def validate_prompt_security(
        self, prompt_text: str, context_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Validate prompt text for security threats with role-based authorization.

        Args:
            prompt_text: Text to validate
            context_type: Context for validation

        Returns:
            Security validation report
        """
        from .prompt_templates import get_security_analysis

        # Get security analysis
        analysis = get_security_analysis(prompt_text, context_type)

        # Check if content should be blocked based on role permissions
        if not self.check_permission("process_sensitive_content") and analysis["threat_level"] in [
            "suspicious",
            "malicious",
        ]:
            analysis["recommended_action"] = "ESCALATE_FOR_REVIEW"
            analysis["reason"] = "Insufficient permissions for handling suspicious content"

        # Log security event
        self.log_authorization_decision(
            action="validate_prompt_security",
            permission="process_sensitive_content",
            granted=analysis["recommended_action"] != "ESCALATE_FOR_REVIEW",
            metadata={
                "threat_level": analysis["threat_level"],
                "confidence": analysis["confidence"],
                "context_type": context_type,
            },
        )

        return analysis


# Global safety manager instances per user context
_safety_managers: Dict[str, AdvancedSafetyManager] = {}

# Default safety manager for anonymous users
_default_safety_manager = AdvancedSafetyManager()


def get_safety_manager(user_context: Optional[Dict[str, Any]] = None) -> AdvancedSafetyManager:
    """Get safety manager instance for user context.

    Args:
        user_context: Dictionary containing user_id, role, organization_id

    Returns:
        AdvancedSafetyManager instance configured for the user
    """
    if not user_context or not user_context.get("user_id"):
        return _default_safety_manager

    user_id = user_context["user_id"]

    # Check if we already have a manager for this user
    if user_id not in _safety_managers:
        _safety_managers[user_id] = AdvancedSafetyManager(user_context)

    return _safety_managers[user_id]


def get_safety_manager_for_user(
    user: Any, organization_id: Optional[str] = None
) -> AdvancedSafetyManager:
    """Get a properly configured safety manager for a user with role-based authorization."""
    user_context = {
        "user_id": str(user.id) if hasattr(user, "id") else None,
        "role": getattr(user, "role", "user"),  # Default to 'user' role
        "organization_id": organization_id or getattr(user, "organization_id", None),
        "email": getattr(user, "email", None),
        "is_active": getattr(user, "is_active", True),
    }

    return get_safety_manager(user_context)


def validate_safety_manager_permissions(
    safety_manager: AdvancedSafetyManager, required_permissions: List[str]
) -> bool:
    """Validate that a safety manager has all required permissions."""
    return all(safety_manager.check_permission(perm) for perm in required_permissions)


class RoleBasedSafetyMiddleware:
    """Middleware for role-based safety management in AI operations."""

    def __init__(self, default_role: str = "user") -> None:
        self.default_role = default_role

    def get_safety_manager(self, user_context: Dict[str, Any]) -> AdvancedSafetyManager:
        """Get safety manager with user context."""
        return get_safety_manager(user_context)

    def check_content_access(self, user_role: str, content_type: ContentType) -> bool:
        """Check if user role can access content type."""
        temp_manager = AdvancedSafetyManager({"role": user_role})
        return temp_manager.can_access_content_type(content_type)

    def get_allowed_safety_profiles(self, user_role: str) -> List[str]:
        """Get list of safety profiles allowed for user role."""
        temp_manager = AdvancedSafetyManager({"role": user_role})

        allowed_profiles = ["minimal"]  # Everyone can use minimal

        if temp_manager.check_permission("can_view_metrics"):
            allowed_profiles.append("standard")

        if temp_manager.check_permission("can_create_profiles"):
            allowed_profiles.extend(["balanced", "strict"])

        if temp_manager.check_permission("can_override_safety"):
            allowed_profiles.append("permissive")

        return allowed_profiles
