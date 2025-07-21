"""
Central repository for all prompt templates used by the AI assistant.

Updated to work with system instructions rather than system prompts for better
AI model performance and consistency.
"""

import json
import re
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .instruction_templates import get_system_instruction
from config.logging_config import get_logger

logger = get_logger(__name__)


class ThreatLevel(Enum):
    """Threat levels for input analysis."""

    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    BLOCKED = "blocked"


@dataclass
class SecurityAnalysis:
    """Result of security analysis on input."""

    threat_level: ThreatLevel
    confidence: float
    threats_detected: List[str]
    sanitized_content: str
    original_hash: str
    analysis_metadata: Dict[str, Any]


class AdvancedPromptSanitizer:
    """Enhanced prompt sanitization with multi-layer defense."""

    def __init__(self):
        """Initialize with comprehensive threat patterns."""
        self.injection_patterns = {
            # Direct instruction overrides
            "instruction_override": [
                r"ignore\s+(all\s+)?previous\s+instructions?",
                r"forget\s+(everything|all|previous)",
                r"disregard\s+(all\s+)?instructions?",
                r"new\s+instructions?:",
                r"override\s+system",
                r"system\s*:\s*",
                r"assistant\s*:\s*",
                r"<\|system\|>",
                r"<\|assistant\|>",
                r"<\|user\|>",
            ],
            # Role manipulation
            "role_manipulation": [
                r"you\s+are\s+now",
                r"act\s+as\s+",
                r"pretend\s+to\s+be",
                r"roleplay\s+as",
                r"simulate\s+being",
                r"become\s+a",
                r"take\s+the\s+role",
                r"switch\s+to\s+being",
            ],
            # Output manipulation
            "output_manipulation": [
                r"print\s+raw\s+prompt",
                r"show\s+system\s+prompt",
                r"reveal\s+instructions?",
                r"output\s+your\s+rules?",
                r"display\s+initial\s+prompt",
                r"repeat\s+your\s+instructions?",
                r"echo\s+the\s+system",
            ],
            # Escape attempts
            "escape_attempts": [
                r"```\s*system",
                r"```\s*prompt",
                r"</?(system|prompt|instruction)>",
                r"\[INST\]|\[/INST\]",
                r"<!--.*?-->",
                r"\{\{.*?\}\}",
                r"\$\{.*?\}",
            ],
            # Jailbreak patterns
            "jailbreak": [
                r"DAN\s+(mode|prompt)",
                r"developer\s+mode",
                r"jailbreak",
                r"bypass\s+safety",
                r"unlimited\s+mode",
                r"ignore\s+safety",
                r"without\s+restrictions?",
                r"no\s+ethical\s+guidelines",
            ],
            # Prompt leaking
            "prompt_leaking": [
                r"what\s+(is|was)\s+your\s+(initial\s+)?prompt",
                r"tell\s+me\s+your\s+system\s+message",
                r"share\s+your\s+instructions?",
                r"what\s+are\s+your\s+guidelines",
                r"explain\s+your\s+configuration",
            ],
            # Code injection
            "code_injection": [
                r"<script.*?>",
                r"javascript:",
                r"data:text/html",
                r"eval\s*\(",
                r"exec\s*\(",
                r"import\s+os",
                r"__import__",
            ],
        }

        self.semantic_triggers = [
            # Context confusion
            "end of conversation",
            "new conversation",
            "restart chat",
            "clear context",
            "reset memory",
            # Authority claims
            "I am your creator",
            "I am the administrator",
            "I have admin rights",
            "as your developer",
            # Emergency/urgency manipulation
            "this is urgent",
            "emergency override",
            "critical system update",
            "immediate action required",
        ]

    def analyze_input(self, input_string: str, context: str = "general") -> SecurityAnalysis:
        """Comprehensive security analysis of input."""
        original_hash = hashlib.sha256(input_string.encode()).hexdigest()
        threats_detected = []
        threat_level = ThreatLevel.CLEAN
        confidence = 0.0

        # Pattern-based detection
        for category, patterns in self.injection_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, input_string, re.IGNORECASE | re.DOTALL)
                if matches:
                    threats_detected.append(f"{category}: {pattern}")
                    if category in ["instruction_override", "jailbreak", "code_injection"]:
                        threat_level = ThreatLevel.MALICIOUS
                        confidence = max(confidence, 0.9)
                    elif category in ["role_manipulation", "escape_attempts"]:
                        threat_level = max(
                            threat_level, ThreatLevel.SUSPICIOUS, key=lambda x: x.value
                        )
                        confidence = max(confidence, 0.7)
                    else:
                        threat_level = max(
                            threat_level, ThreatLevel.SUSPICIOUS, key=lambda x: x.value
                        )
                        confidence = max(confidence, 0.5)

        # Semantic analysis
        for trigger in self.semantic_triggers:
            if trigger.lower() in input_string.lower():
                threats_detected.append(f"semantic: {trigger}")
                threat_level = max(threat_level, ThreatLevel.SUSPICIOUS, key=lambda x: x.value)
                confidence = max(confidence, 0.6)

        # Statistical analysis
        stats = self._analyze_statistics(input_string)
        if stats["special_char_ratio"] > 0.3:
            threats_detected.append("statistical: high special character ratio")
            confidence = max(confidence, 0.4)

        if stats["repeated_phrases"] > 5:
            threats_detected.append("statistical: excessive repetition")
            confidence = max(confidence, 0.5)

        # Context-specific analysis
        context_threats = self._analyze_context_specific(input_string, context)
        threats_detected.extend(context_threats)

        if context_threats:
            threat_level = max(threat_level, ThreatLevel.SUSPICIOUS, key=lambda x: x.value)
            confidence = max(confidence, 0.6)

        # Sanitize the content
        sanitized_content = self._sanitize_content(input_string, threat_level, context)

        return SecurityAnalysis(
            threat_level=threat_level,
            confidence=confidence,
            threats_detected=threats_detected,
            sanitized_content=sanitized_content,
            original_hash=original_hash,
            analysis_metadata={
                "input_length": len(input_string),
                "context": context,
                "statistics": stats,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _analyze_statistics(self, text: str) -> Dict[str, Any]:
        """Statistical analysis of input text."""
        if not text:
            return {"special_char_ratio": 0, "repeated_phrases": 0}

        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_char_ratio = special_chars / len(text) if text else 0

        # Count repeated 3-word phrases
        words = text.lower().split()
        phrases = [" ".join(words[i : i + 3]) for i in range(len(words) - 2)]
        repeated_phrases = len(phrases) - len(set(phrases))

        return {
            "special_char_ratio": special_char_ratio,
            "repeated_phrases": repeated_phrases,
            "word_count": len(words),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        }

    def _analyze_context_specific(self, text: str, context: str) -> List[str]:
        """Context-specific threat analysis."""
        threats = []

        if context == "code":
            # Code context - check for dangerous functions
            code_threats = [
                r"exec\s*\(",
                r"eval\s*\(",
                r"__import__",
                r"subprocess",
                r"os\.system",
                r"shell=True",
            ]
            for pattern in code_threats:
                if re.search(pattern, text, re.IGNORECASE):
                    threats.append(f"code_threat: {pattern}")

        elif context == "query":
            # Database query context
            sql_threats = [
                r"union\s+select",
                r"drop\s+table",
                r"delete\s+from",
                r"update\s+.*\s+set",
                r"insert\s+into",
                r"--",
                r"/\*.*?\*/",
            ]
            for pattern in sql_threats:
                if re.search(pattern, text, re.IGNORECASE):
                    threats.append(f"sql_injection: {pattern}")

        return threats

    def _sanitize_content(self, content: str, threat_level: ThreatLevel, context: str) -> str:
        """Sanitize content based on threat level."""
        if threat_level == ThreatLevel.BLOCKED:
            return "[CONTENT BLOCKED]"

        sanitized = content.strip()

        # Remove null bytes and control characters
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

        # Handle different threat levels
        if threat_level == ThreatLevel.MALICIOUS:
            # Aggressive sanitization for malicious content
            for category, patterns in self.injection_patterns.items():
                for pattern in patterns:
                    sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)

        elif threat_level == ThreatLevel.SUSPICIOUS:
            # Moderate sanitization for suspicious content
            # Remove common injection patterns but preserve more content
            for pattern in self.injection_patterns["instruction_override"]:
                sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)
            for pattern in self.injection_patterns["escape_attempts"]:
                sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)

        # Context-specific sanitization
        if context == "code":
            # Preserve more characters but escape quotes
            sanitized = sanitized.replace('"', '\\"').replace("'", "\\'")
        else:
            # Escape template/format strings
            sanitized = sanitized.replace("{", "{{").replace("}", "}}")
            sanitized = sanitized.replace("$", "\\$")
            sanitized = sanitized.replace("%", "%%")

        # Limit consecutive newlines
        sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)

        return sanitized


# Global sanitizer instance
_sanitizer = AdvancedPromptSanitizer()


def sanitize_input(input_string: str, context: str = "general") -> str:
    """
    Advanced sanitization using comprehensive threat analysis.

    Args:
        input_string: The user input to sanitize
        context: The context of usage (general, code, query, etc.)

    Returns:
        Sanitized string safe for prompt inclusion with safety fencing
    """
    if not input_string:
        return create_safety_fence("", "user")

    # Perform comprehensive security analysis
    analysis = _sanitizer.analyze_input(input_string, context)

    # Log security events
    if analysis.threat_level != ThreatLevel.CLEAN:
        logger.warning(
            f"Security analysis detected {analysis.threat_level.value} content "
            f"(confidence: {analysis.confidence:.2f}): {analysis.threats_detected[:3]}"
        )

        # Log full details for high-confidence threats
        if analysis.confidence > 0.8:
            logger.error(
                f"High-confidence threat detected: {analysis.original_hash[:8]}... "
                f"Threats: {analysis.threats_detected}"
            )

    # Block malicious content entirely
    if analysis.threat_level == ThreatLevel.MALICIOUS and analysis.confidence > 0.8:
        logger.critical(f"Blocking malicious input: {analysis.original_hash[:8]}...")
        return create_safety_fence("[MALICIOUS CONTENT BLOCKED]", "user")

    # Apply safety fencing to sanitized content
    return create_safety_fence(analysis.sanitized_content, "user")


def create_safety_fence(content: str, fence_type: str = "user") -> str:
    """
    Create enhanced safety fence around content with multiple isolation layers.

    Args:
        content: The content to fence
        fence_type: Type of fence (user, system, output)

    Returns:
        Multi-layer fenced content with clear boundaries
    """
    fences = {
        "user": {
            "outer": "==== SECURE USER INPUT BOUNDARY ====",
            "inner": "--- USER CONTENT ---",
            "end": "==== END USER INPUT BOUNDARY ====",
        },
        "system": {
            "outer": "==== SYSTEM CONTEXT BOUNDARY ====",
            "inner": "--- SYSTEM CONTENT ---",
            "end": "==== END SYSTEM BOUNDARY ====",
        },
        "output": {
            "outer": "==== AI RESPONSE BOUNDARY ====",
            "inner": "--- AI OUTPUT ---",
            "end": "==== END AI RESPONSE BOUNDARY ====",
        },
    }

    fence_config = fences.get(fence_type, fences["user"])

    # Multi-layer fencing for maximum isolation
    return (
        f"\n{fence_config['outer']}\n"
        f"{fence_config['inner']}\n"
        f"{content}\n"
        f"{fence_config['inner']}\n"
        f"{fence_config['end']}\n"
    )


def validate_prompt_safety(
    prompt_dict: Dict[str, str], context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Validate entire prompt safety including system and user components.

    Args:
        prompt_dict: Dictionary containing system and user prompts
        context: Additional context for validation

    Returns:
        Safety validation report
    """
    validation_report = {
        "safe": True,
        "threats_detected": [],
        "confidence_scores": {},
        "recommendations": [],
        "timestamp": datetime.now().isoformat(),
    }

    # Validate each component
    for component, content in prompt_dict.items():
        if component in ["system", "system_instruction", "user"]:
            analysis = _sanitizer.analyze_input(content, context="prompt_validation")

            validation_report["confidence_scores"][component] = analysis.confidence

            if analysis.threat_level != ThreatLevel.CLEAN:
                validation_report["safe"] = False
                validation_report["threats_detected"].extend(
                    [f"{component}: {threat}" for threat in analysis.threats_detected]
                )

                # Add specific recommendations
                if analysis.threat_level == ThreatLevel.MALICIOUS:
                    validation_report["recommendations"].append(
                        f"CRITICAL: {component} component contains malicious content - block request"
                    )
                elif analysis.threat_level == ThreatLevel.SUSPICIOUS:
                    validation_report["recommendations"].append(
                        f"WARNING: {component} component contains suspicious patterns - review required"
                    )

    # Log validation results
    if not validation_report["safe"]:
        logger.warning(f"Prompt safety validation failed: {validation_report['threats_detected']}")

    return validation_report


def get_security_analysis(input_text: str, context: str = "general") -> Dict[str, Any]:
    """
    Public interface for security analysis of input text.

    Args:
        input_text: Text to analyze
        context: Context for analysis

    Returns:
        Security analysis report
    """
    analysis = _sanitizer.analyze_input(input_text, context)

    return {
        "threat_level": analysis.threat_level.value,
        "confidence": analysis.confidence,
        "threats_detected": analysis.threats_detected,
        "input_hash": analysis.original_hash,
        "metadata": analysis.analysis_metadata,
        "safe_to_proceed": analysis.threat_level in [ThreatLevel.CLEAN, ThreatLevel.SUSPICIOUS],
        "recommended_action": _get_recommended_action(analysis),
    }


def _get_recommended_action(analysis: SecurityAnalysis) -> str:
    """Generate recommended action based on security analysis."""
    if analysis.threat_level == ThreatLevel.MALICIOUS:
        if analysis.confidence > 0.8:
            return "BLOCK_REQUEST"
        else:
            return "ESCALATE_FOR_REVIEW"
    elif analysis.threat_level == ThreatLevel.SUSPICIOUS:
        if analysis.confidence > 0.6:
            return "SANITIZE_AND_MONITOR"
        else:
            return "ALLOW_WITH_LOGGING"
    else:
        return "ALLOW"


class PromptTemplates:
    """Manages and formats prompts for different AI tasks."""

    def __init__(self):
        """Initialize prompt templates with system instruction support"""
        self._instruction_cache = {}
        self._safety_enabled = True  # Enable safety validation by default

    def _validate_and_secure_prompt(
        self, prompt_dict: Dict[str, str], context: Dict[str, Any], prompt_type: str = "general"
    ) -> Dict[str, str]:
        """
        Validate prompt safety and return secured version.

        Args:
            prompt_dict: The prompt dictionary to validate
            context: Context for validation
            prompt_type: Type of prompt for logging

        Returns:
            Validated and secured prompt dictionary
        """
        if not self._safety_enabled:
            return prompt_dict

        validation_result = validate_prompt_safety(prompt_dict, context)
        if not validation_result["safe"]:
            logger.error(f"{prompt_type} prompt failed safety validation: {validation_result}")
            # Return a safe fallback prompt
            return {
                "system": "You are a helpful AI assistant. Respond safely and appropriately.",
                "user": create_safety_fence(
                    "[UNSAFE PROMPT BLOCKED - Request contains suspicious content]", "user"
                ),
            }

        return prompt_dict

    def get_system_instruction_for_task(
        self,
        task_type: str,
        framework: Optional[str] = None,
        business_profile: Optional[Dict[str, Any]] = None,
        user_persona: Optional[str] = None,
        task_complexity: str = "medium",
        **kwargs,
    ) -> str:
        """
        Get system instruction for a specific task with caching

        Args:
            task_type: Type of task ("assessment", "evidence", "chat", etc.)
            framework: Framework name
            business_profile: Business context
            user_persona: User persona
            task_complexity: Task complexity level
            **kwargs: Additional context

        Returns:
            System instruction string
        """
        # Create cache key
        cache_key = (
            task_type,
            framework,
            json.dumps(business_profile, sort_keys=True) if business_profile else None,
            user_persona,
            task_complexity,
            json.dumps(kwargs, sort_keys=True) if kwargs else None,
        )

        # Check cache first
        if cache_key in self._instruction_cache:
            return self._instruction_cache[cache_key]

        # Generate instruction
        instruction = get_system_instruction(
            task_type,
            framework=framework,
            business_profile=business_profile,
            user_persona=user_persona,
            task_complexity=task_complexity,
            **kwargs,
        )

        # Cache and return
        self._instruction_cache[cache_key] = instruction
        return instruction

    def get_user_prompt_only(self, message: str, context: Dict[str, Any]) -> str:
        """
        Helper method to create user prompts that work with system instructions

        Args:
            message: User message
            context: Context information

        Returns:
            User prompt string for use with system instructions
        """
        business_info = context.get("business_profile", {})

        prompt_parts = [f'User message: """{sanitize_input(message)}"""']

        if business_info:
            prompt_parts.append(f"Business context: {json.dumps(business_info, indent=2)}")

        if context.get("recent_evidence"):
            prompt_parts.append(
                f"Recent evidence: {json.dumps(context.get('recent_evidence', []), indent=2)}"
            )

        return "\n\n".join(prompt_parts)

    def get_intent_classification_prompt(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates the prompt for classifying the user's intent."""

        # Use system instruction instead of system prompt
        system_instruction = get_system_instruction(
            "general",  # Use general instruction for intent classification
            business_profile=context.get("business_profile"),
            additional_context={"intent_classification": True, "expected_output": "JSON"},
        )

        user_prompt = f'''
        Please classify this user message and extract relevant entities.
        
        User message: """{sanitize_input(message)}"""
        
        Business context: {json.dumps(context.get("business_profile", {}), indent=2)}
        
        Recent evidence: {json.dumps(context.get("recent_evidence", []), indent=2)}
        
        Classification options: 'evidence_query', 'compliance_check', 'guidance_request', 'general_query'
        
        Return a JSON object with this exact format:
        {{"type": "evidence_query|compliance_check|guidance_request|general_query", "confidence": 0.9, "entities": {{"frameworks": ["ISO27001"], "evidence_types": ["policies"]}}}}
        '''

        prompt_dict = {
            "system": system_instruction,  # Backwards compatibility
            "system_instruction": system_instruction,  # New format
            "user": user_prompt,
        }

        return self._validate_and_secure_prompt(prompt_dict, context, "intent_classification")

    def get_evidence_query_prompt(
        self, message: str, evidence_items: List[Any], context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates the prompt for answering evidence-related questions."""

        # Use evidence-specific system instruction
        system_instruction = get_system_instruction(
            "evidence",
            business_profile=context.get("business_profile"),
            additional_context={"evidence_analysis": True, "task_type": "evidence_query"},
        )

        evidence_summary = json.dumps(
            [
                {
                    "title": getattr(e, "evidence_name", "Unknown"),
                    "type": getattr(e, "evidence_type", "Unknown"),
                    "description": getattr(e, "description", ""),
                    "status": getattr(e, "status", "active"),
                }
                for e in evidence_items
            ],
            indent=2,
        )

        business_info = context.get("business_profile", {})

        user_prompt = f'''
        User question: """{sanitize_input(message)}"""
        
        Business context:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Frameworks: {", ".join(business_info.get("frameworks", []))}
        
        Found evidence ({len(evidence_items)} items):
        {evidence_summary}
        
        Compliance status: {json.dumps(context.get("compliance_status", {}), indent=2)}
        
        Please provide a helpful response addressing their question about this evidence.
        '''

        prompt_dict = {
            "system": system_instruction,  # Backwards compatibility
            "system_instruction": system_instruction,  # New format
            "user": user_prompt,
        }

        return self._validate_and_secure_prompt(prompt_dict, context, "evidence_query")

    def get_compliance_check_prompt(self, message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for compliance status checks."""
        system_prompt = """
        You are ComplianceGPT, a compliance expert. Provide a comprehensive compliance status overview based on the user's current state.
        
        Guidelines:
        - Assess overall compliance readiness
        - Highlight strengths and weaknesses
        - Provide specific recommendations
        - Reference industry standards and frameworks
        - Include actionable next steps
        - Use clear, professional language
        """

        business_info = context.get("business_profile", {})
        compliance_status = context.get("compliance_status", {})
        recent_evidence = context.get("recent_evidence", [])

        user_prompt = f'''
        User question: """{sanitize_input(message)}"""
        
        Business profile:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Target frameworks: {", ".join(business_info.get("frameworks", []))}
        
        Current compliance scores:
        {json.dumps(compliance_status, indent=2)}
        
        Recent evidence activity ({len(recent_evidence)} items):
        {json.dumps(recent_evidence, indent=2)}
        
        Please provide a comprehensive compliance status assessment and recommendations.
        '''

        return {"system": system_prompt, "user": user_prompt}

    def get_guidance_request_prompt(self, message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Creates the prompt for providing compliance guidance."""
        system_prompt = """
        You are ComplianceGPT, a knowledgeable compliance consultant. Provide expert guidance and recommendations based on the user's specific needs.
        
        Guidelines:
        - Offer practical, actionable advice
        - Reference relevant standards and best practices
        - Consider the user's business context and industry
        - Provide step-by-step guidance when appropriate
        - Include relevant resources or references
        - Maintain a helpful, consultative tone
        """

        business_info = context.get("business_profile", {})

        user_prompt = f'''
        User request: """{sanitize_input(message)}"""
        
        Business context:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Frameworks: {", ".join(business_info.get("frameworks", []))}
        
        Current compliance status: {json.dumps(context.get("compliance_status", {}), indent=2)}
        
        Please provide expert guidance tailored to their specific situation and requirements.
        '''

        return {"system": system_prompt, "user": user_prompt}

    def get_general_query_prompt(
        self, message: str, history: List[Dict], context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates the prompt for handling general questions."""
        system_prompt = """
        You are ComplianceGPT, a friendly and knowledgeable compliance assistant. Answer the user's question considering the conversation history and their business context.
        
        Guidelines:
        - Be helpful and informative
        - Reference previous conversation context when relevant
        - Provide compliance-focused insights when possible
        - Ask clarifying questions if needed
        - Maintain a professional but approachable tone
        - Keep responses focused and concise
        """

        history_str = "\n".join(
            [
                f"{msg['role'].title()}: {msg['content']}"
                for msg in history[-5:]  # Only include last 5 messages for context
            ]
        )

        business_info = context.get("business_profile", {})

        sanitized_message = sanitize_input(message)
        user_prompt = f"""
        Recent conversation history:
        {history_str}
        
        User's new message: {sanitized_message}
        
        Business context:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Frameworks: {", ".join(business_info.get("frameworks", []))}
        
        Please provide a helpful response that considers the conversation context and their compliance needs.
        """

        return {"system": system_prompt, "user": user_prompt}

    def get_evidence_recommendation_prompt(
        self, framework: str, business_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates prompts for recommending evidence collection."""
        system_prompt = """
        You are ComplianceGPT, an expert in compliance frameworks. Recommend specific evidence items to collect based on the framework and business context.
        
        Guidelines:
        - Provide specific, actionable recommendations
        - Prioritize by importance and feasibility
        - Consider the business industry and size
        - Include automation opportunities where possible
        - Explain the compliance value of each item
        """

        user_prompt = f"""
        Framework: {framework}
        
        Business context:
        {json.dumps(business_context, indent=2)}
        
        Please recommend the top 10 most important evidence items to collect for this framework, prioritized by compliance impact and ease of collection.
        """

        return {"system": system_prompt, "user": user_prompt}

    # Assessment-specific prompt templates for Phase 2.2 integration

    def get_assessment_help_prompt(
        self,
        question_text: str,
        framework_id: str,
        section_id: Optional[str] = None,
        business_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Creates prompts for assessment question help."""

        system_prompt = f"""You are an expert compliance consultant specializing in {framework_id}.
        Provide clear, actionable guidance for assessment questions.

        Your response should be:
        - Specific to the framework and business context
        - Practical and implementable
        - Include relevant examples when helpful
        - Highlight key considerations and potential pitfalls

        Format your response as JSON with these keys:
        - guidance: Main guidance text
        - confidence_score: Float between 0.0-1.0
        - related_topics: Array of related topics
        - follow_up_suggestions: Array of follow-up questions
        - source_references: Array of relevant documentation
        """

        business_info = business_context or {}
        user_info = user_context or {}

        user_prompt = f"""
        Assessment Question: "{question_text}"

        Framework: {framework_id}
        {f"Section: {section_id}" if section_id else ""}

        Business Context:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Size: {business_info.get("employee_count", "Unknown")} employees
        - Frameworks: {", ".join(business_info.get("frameworks", []))}

        User Context:
        {user_info}

        Please provide comprehensive guidance for answering this assessment question.
        """

        return {"system": system_prompt, "user": user_prompt}

    def get_assessment_followup_prompt(
        self,
        current_answers: Dict[str, Any],
        framework_id: str,
        business_context: Optional[Dict[str, Any]] = None,
        assessment_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Creates prompts for generating assessment follow-up questions."""

        system_prompt = f"""You are an expert compliance consultant for {framework_id}.
        Based on the user's current assessment responses, generate intelligent follow-up questions
        that will help complete their compliance assessment.

        Your follow-up questions should:
        - Build on their existing answers
        - Identify gaps or areas needing clarification
        - Be specific to their business context
        - Help prioritize next steps

        Format your response as JSON with these keys:
        - follow_up_questions: Array of specific questions
        - recommendations: Array of immediate recommendations
        - confidence_score: Float between 0.0-1.0
        """

        business_info = business_context or {}
        assessment_info = assessment_context or {}

        user_prompt = f"""
        Current Assessment Responses:
        {current_answers}

        Framework: {framework_id}

        Business Context:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Size: {business_info.get("employee_count", "Unknown")} employees

        Assessment Context:
        - Type: {assessment_info.get("assessment_type", "general")}
        - Progress: {assessment_info.get("progress", "unknown")}

        Based on these responses, what follow-up questions should we ask to complete the assessment?
        """

        return {"system": system_prompt, "user": user_prompt}

    def get_assessment_analysis_prompt(
        self,
        assessment_results: Dict[str, Any],
        framework_id: str,
        business_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Creates prompts for comprehensive assessment analysis."""

        # Use assessment-specific system instruction with framework context
        system_instruction = get_system_instruction(
            "analysis",
            framework=framework_id.lower() if framework_id else None,
            business_profile=business_context,
            task_complexity="complex",
            additional_context={
                "assessment_analysis": True,
                "structured_output": True,
                "output_format": "JSON",
            },
        )

        business_info = business_context or {}

        user_prompt = f"""
        Please provide a comprehensive analysis of these assessment results, identifying gaps and providing actionable recommendations.

        Assessment Results:
        {assessment_results}

        Framework: {framework_id}

        Business Context:
        - Company: {business_info.get("name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Size: {business_info.get("employee_count", "Unknown")} employees
        - Current Frameworks: {", ".join(business_info.get("frameworks", []))}

        Format your response as JSON with these keys:
        - gaps: Array of gap objects with id, title, description, severity, category
        - recommendations: Array of recommendation objects with id, title, description, priority, effort_estimate, impact_score
        - risk_assessment: Object with level and description
        - compliance_insights: Object with summary and key_findings
        - evidence_requirements: Array of evidence requirement objects
        """

        return {
            "system": system_instruction,  # Backwards compatibility
            "system_instruction": system_instruction,  # New format
            "user": user_prompt,
        }

    def get_assessment_recommendations_prompt(
        self,
        gaps: List[Dict[str, Any]],
        business_profile: Dict[str, Any],
        framework_id: str,
        existing_policies: Optional[List[str]] = None,
        industry_context: Optional[str] = None,
        timeline_preferences: str = "standard",
    ) -> Dict[str, str]:
        """Creates prompts for generating personalized implementation recommendations."""

        # Use recommendations-specific system instruction with framework context
        system_instruction = get_system_instruction(
            "recommendations",
            framework=framework_id.lower() if framework_id else None,
            business_profile=business_profile,
            task_complexity="complex",
            additional_context={
                "implementation_planning": True,
                "structured_output": True,
                "output_format": "JSON",
                "timeline_preferences": timeline_preferences,
            },
        )

        user_prompt = f"""
        Please provide detailed, personalized recommendations with a practical implementation plan.

        Identified Gaps:
        {gaps}

        Framework: {framework_id}

        Business Profile:
        - Company: {business_profile.get("name", "Unknown")}
        - Industry: {business_profile.get("industry", "Unknown")}
        - Size: {business_profile.get("employee_count", "Unknown")} employees
        - Budget Range: {business_profile.get("budget_range", "Unknown")}

        Existing Policies: {existing_policies or "None specified"}
        Industry Context: {industry_context or "General"}
        Timeline Preference: {timeline_preferences}

        Format your response as JSON with these keys:
        - recommendations: Array of detailed recommendation objects
        - implementation_plan: Object with phases, timeline, and resource requirements
        - success_metrics: Array of measurable success criteria
        """

        return {
            "system": system_instruction,  # Backwards compatibility
            "system_instruction": system_instruction,  # New format
            "user": user_prompt,
        }

    def get_main_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Creates the main prompt for general AI responses."""
        business_info = context.get("business_profile", {})
        recent_evidence = context.get("recent_evidence", [])

        return f'''You are ComplianceGPT, an expert AI compliance assistant. You help organizations understand and implement compliance requirements across various frameworks.

Business Context:
- Company: {business_info.get("company_name", "Unknown")}
- Industry: {business_info.get("industry", "Unknown")}
- Employee Count: {business_info.get("employee_count", "Unknown")}
- Current Frameworks: {", ".join(business_info.get("existing_frameworks", []))}
- Evidence Collected: {len(recent_evidence)} items

User Message: """{sanitize_input(message)}"""

Please provide a comprehensive, helpful response that:
1. Addresses the user's specific question or need
2. Considers their business context and industry
3. Provides actionable guidance and next steps
4. References relevant compliance frameworks when appropriate
5. Maintains a professional, consultative tone

If you need clarification on any aspect of their request, feel free to ask follow-up questions.'''

    def get_main_prompt_with_system_instruction(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Creates main prompt with system instruction for general AI responses."""

        # Use general system instruction
        system_instruction = get_system_instruction(
            "general",
            business_profile=context.get("business_profile"),
            additional_context={"conversation_mode": True, "comprehensive_response": True},
        )

        business_info = context.get("business_profile", {})
        recent_evidence = context.get("recent_evidence", [])

        user_prompt = f'''
        User Message: """{sanitize_input(message)}"""

        Business Context:
        - Company: {business_info.get("company_name", "Unknown")}
        - Industry: {business_info.get("industry", "Unknown")}
        - Employee Count: {business_info.get("employee_count", "Unknown")}
        - Current Frameworks: {", ".join(business_info.get("existing_frameworks", []))}
        - Evidence Collected: {len(recent_evidence)} items

        Please provide a comprehensive, helpful response that:
        1. Addresses the user's specific question or need
        2. Considers their business context and industry
        3. Provides actionable guidance and next steps
        4. References relevant compliance frameworks when appropriate
        5. Maintains a professional, consultative tone

        If you need clarification on any aspect of their request, feel free to ask follow-up questions.
        '''

        prompt_dict = {
            "system": system_instruction,  # Backwards compatibility
            "system_instruction": system_instruction,  # New format
            "user": user_prompt,
        }

        return self._validate_and_secure_prompt(prompt_dict, context, "main_prompt")

    def get_context_aware_recommendation_prompt(
        self,
        framework: str,
        business_context: Dict[str, Any],
        maturity_analysis: Dict[str, Any],
        gaps_analysis: Dict[str, Any],
    ) -> Dict[str, str]:
        """Creates enhanced prompts for context-aware recommendations."""

        system_prompt = f"""You are an expert compliance consultant specializing in {framework}.
        Generate intelligent, context-aware evidence collection recommendations that consider:

        1. Organization's specific business context and industry
        2. Current compliance maturity and capabilities
        3. Existing evidence gaps and priorities
        4. Resource constraints and practical implementation
        5. Automation opportunities and efficiency gains
        6. Risk-based prioritization

        Provide recommendations that are:
        - Specific and actionable
        - Prioritized by business impact and feasibility
        - Tailored to organizational maturity level
        - Include automation opportunities where applicable
        - Consider industry-specific requirements

        Return recommendations as a JSON array with detailed structure including:
        - Control mapping and references
        - Implementation steps and guidance
        - Effort estimates and timelines
        - Automation potential and tools
        - Business justification and ROI
        """

        user_prompt = f"""
        Generate context-aware recommendations for {framework} compliance.

        Business Profile:
        - Company: {business_context.get("company_name", "Unknown")}
        - Industry: {business_context.get("industry", "Unknown")}
        - Size: {business_context.get("employee_count", 0)} employees
        - Maturity Level: {maturity_analysis.get("maturity_level", "Basic")}
        - Maturity Score: {maturity_analysis.get("maturity_score", 40)}/100

        Current Compliance Status:
        - Completion: {gaps_analysis.get("completion_percentage", 0)}%
        - Evidence Items: {gaps_analysis.get("evidence_collected", 0)}
        - Critical Gaps: {len(gaps_analysis.get("critical_gaps", []))}
        - Risk Level: {gaps_analysis.get("risk_level", "Medium")}

        Generate 8-12 prioritized recommendations that address critical gaps while
        considering organizational capacity and maturity level.
        """

        return {"system": system_prompt, "user": user_prompt}

    def get_workflow_generation_prompt(
        self, framework: str, control_id: str, business_context: Dict[str, Any], workflow_type: str
    ) -> Dict[str, str]:
        """Creates prompts for intelligent workflow generation."""

        system_prompt = f"""You are an expert compliance process designer specializing in {framework}.
        Generate comprehensive, step-by-step evidence collection workflows that are:

        1. Tailored to the organization's size and maturity
        2. Practical and implementable with available resources
        3. Include both manual and automated approaches
        4. Provide realistic time estimates and dependencies
        5. Include quality checkpoints and validation criteria
        6. Consider industry-specific requirements
        7. Include role assignments and responsibilities

        Structure the workflow with clear phases, detailed steps, and practical guidance.
        Include automation opportunities and tool recommendations where applicable.
        """

        control_context = f" for control {control_id}" if control_id else ""

        user_prompt = f"""
        Generate a {workflow_type} evidence collection workflow for {framework}{control_context}.

        Organization Context:
        - Company: {business_context.get("company_name", "Unknown")}
        - Industry: {business_context.get("industry", "Unknown")}
        - Size: {business_context.get("employee_count", 0)} employees
        - Organization Type: {self._categorize_org_size(business_context.get("employee_count", 0))}

        Requirements:
        - Create 3-5 logical phases with 2-4 steps each
        - Include specific deliverables and validation criteria
        - Provide realistic effort estimates
        - Consider automation opportunities
        - Include role assignments and dependencies
        - Address potential challenges and mitigation strategies

        Generate a comprehensive workflow that can be immediately implemented.
        """

        return {"system": system_prompt, "user": user_prompt}

    def get_policy_generation_prompt(
        self,
        framework: str,
        policy_type: str,
        business_context: Dict[str, Any],
        customization_options: Dict[str, Any],
    ) -> Dict[str, str]:
        """Creates prompts for customized policy generation."""

        system_prompt = f"""You are an expert compliance policy writer specializing in {framework}.
        Generate comprehensive, business-specific policies that are:

        1. Fully compliant with {framework} requirements
        2. Tailored to the organization's industry and size
        3. Written in clear, professional language
        4. Include specific procedures and controls
        5. Address industry-specific risks and requirements
        6. Practical and implementable
        7. Include roles, responsibilities, and governance

        The policy should be comprehensive yet practical, addressing all relevant
        compliance requirements while being tailored to the organization's context.
        """

        industry = business_context.get("industry", "Unknown")
        org_size = self._categorize_org_size(business_context.get("employee_count", 0))

        user_prompt = f"""
        Generate a comprehensive {policy_type} policy for {framework} compliance.

        Organization Profile:
        - Company: {business_context.get("company_name", "Organization")}
        - Industry: {industry}
        - Size: {business_context.get("employee_count", 0)} employees ({org_size})
        - Geographic Scope: {customization_options.get("geographic_scope", "Single location")}

        Customization Requirements:
        - Tone: {customization_options.get("tone", "Professional")}
        - Detail Level: {customization_options.get("detail_level", "Standard")}
        - Industry Focus: {industry}

        Generate a policy with:
        - 5-8 comprehensive sections
        - Detailed procedures and controls
        - Clear roles and responsibilities
        - Compliance requirements mapping
        - Implementation guidance
        - Industry-specific considerations

        Ensure the policy is immediately usable and addresses all {framework} requirements.
        """

        return {"system": system_prompt, "user": user_prompt}

    def _categorize_org_size(self, employee_count: int) -> str:
        """Helper method to categorize organization size."""
        if employee_count >= 1000:
            return "enterprise"
        elif employee_count >= 100:
            return "medium"
        elif employee_count >= 10:
            return "small"
        else:
            return "micro"
