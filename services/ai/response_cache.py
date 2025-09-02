"""
AI Response Caching System

Intelligent caching for AI responses to improve performance and reduce costs.
Implements smart TTL management, content-type classification, and cache optimization.
"""

import hashlib
import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from config.cache import get_cache_manager
from config.logging_config import get_logger

logger = get_logger(__name__)


class ContentType(Enum):
    """AI response content types for intelligent TTL management."""

    RECOMMENDATION = "recommendation"
    POLICY = "policy"
    WORKFLOW = "workflow"
    ANALYSIS = "analysis"
    GUIDANCE = "guidance"
    GENERAL = "general"


class CacheStrategy(Enum):
    """Caching strategies for different content types."""

    AGGRESSIVE = "aggressive"  # Long TTL, high hit rate
    MODERATE = "moderate"  # Medium TTL, balanced
    CONSERVATIVE = "conservative"  # Short TTL, fresh content
    DYNAMIC = "dynamic"  # TTL based on content analysis


class AIResponseCache:
    """
    Intelligent AI response caching system with content-aware TTL management.

    Features:
    - Content-type classification for optimal TTL
    - Prompt similarity detection for cache hits
    - Performance metrics and analytics
    - Cost optimization through intelligent caching
    """

    def __init__(self) -> None:
        self.cache_manager = None
        self.default_ttl = 3600  # 1 hour default
        self.max_ttl = 86400  # 24 hours max
        self.min_ttl = 300  # 5 minutes min

        # TTL configuration by content type
        self.ttl_config = {
            ContentType.RECOMMENDATION: 7200,  # 2 hours - recommendations change with context
            ContentType.POLICY: 86400,  # 24 hours - policies are more stable
            ContentType.WORKFLOW: 14400,  # 4 hours - workflows are moderately stable
            ContentType.ANALYSIS: 3600,  # 1 hour - analysis may change with new data
            ContentType.GUIDANCE: 7200,  # 2 hours - guidance is fairly stable
            ContentType.GENERAL: 1800,  # 30 minutes - general responses vary more
        }

        # Cache hit/miss metrics
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "cache_size_bytes": 0,
            "cost_savings": 0.0,
        }

    async def initialize(self) -> None:
        """Initialize the cache manager."""
        self.cache_manager = await get_cache_manager()
        logger.info("AI Response Cache initialized")

    async def get_cached_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.85,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached AI response for similar prompts.

        Args:
            prompt: The AI prompt to check
            context: Additional context for cache key generation
            similarity_threshold: Minimum similarity for cache hit

        Returns:
            Cached response data or None if not found
        """
        try:
            if not self.cache_manager:
                await self.initialize()

            # Generate cache key
            cache_key = self._generate_cache_key(prompt, context)

            # Try exact match first
            cached_data = await self.cache_manager.get(cache_key)
            if cached_data:
                self._record_cache_hit()
                logger.debug(f"Cache hit for prompt hash: {cache_key}")
                return cached_data

            # Try similarity-based matching for recommendations and workflows
            if context and context.get("enable_similarity_matching", True):
                similar_response = await self._find_similar_cached_response(
                    prompt, context, similarity_threshold
                )
                if similar_response:
                    self._record_cache_hit()
                    logger.debug("Similarity cache hit for prompt")
                    return similar_response

            self._record_cache_miss()
            return None

        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            self._record_cache_miss()
            return None

    async def cache_response(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Cache AI response with intelligent TTL based on content type.

        Args:
            prompt: The original prompt
            response: The AI response to cache
            context: Additional context information
            metadata: Response metadata (timing, tokens, etc.)

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            if not self.cache_manager:
                await self.initialize()

            # Classify content type
            content_type = self._classify_content_type(response, context)

            # Calculate intelligent TTL
            ttl = self._calculate_intelligent_ttl(content_type, response, context)

            # Generate cache key
            cache_key = self._generate_cache_key(prompt, context)

            # Prepare cache data
            cache_data = {
                "response": response,
                "content_type": content_type.value,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl,
                "prompt_hash": cache_key,
                "metadata": metadata or {},
                "context_summary": self._summarize_context(context),
            }

            # Cache the response
            success = await self.cache_manager.set(cache_key, cache_data, ttl)

            if success:
                # Update metrics
                self._update_cache_metrics(cache_data)
                logger.debug(
                    f"Cached response with TTL {ttl}s for content type {content_type.value}"
                )

            return success

        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
            return False

    def _generate_cache_key(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a unique cache key for the prompt and context."""
        # Normalize prompt (remove extra whitespace, lowercase)
        normalized_prompt = re.sub(r"\s+", " ", prompt.strip().lower())

        # Include relevant context in key generation
        context_key = ""
        if context:
            # Only include stable context elements that affect response
            stable_context = {
                "framework": context.get("framework"),
                "industry": context.get("business_context", {}).get("industry"),
                "org_size": context.get("business_context", {}).get("employee_count", 0)
                // 100
                * 100,  # Round to nearest 100
                "content_type": context.get("content_type"),
            }
            context_key = json.dumps(stable_context, sort_keys=True)

        # Generate hash
        combined_input = f"{normalized_prompt}|{context_key}"
        return f"ai_response:{hashlib.sha256(combined_input.encode()).hexdigest()[:16]}"

    def _classify_content_type(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> ContentType:
        """Classify the content type of the AI response for optimal caching."""
        response_lower = response.lower()

        # Check context first for explicit type
        if context and context.get("content_type"):
            try:
                return ContentType(context["content_type"])
            except ValueError:
                pass

        # Pattern-based classification
        if any(
            keyword in response_lower
            for keyword in ["recommend", "suggest", "priority", "should implement"]
        ):
            return ContentType.RECOMMENDATION
        elif any(
            keyword in response_lower
            for keyword in [
                "policy",
                "procedure",
                "governance",
                "compliance requirement",
            ]
        ):
            return ContentType.POLICY
        elif any(
            keyword in response_lower
            for keyword in ["workflow", "step", "phase", "implementation"]
        ):
            return ContentType.WORKFLOW
        elif any(
            keyword in response_lower
            for keyword in ["analysis", "assessment", "evaluation", "gap"]
        ):
            return ContentType.ANALYSIS
        elif any(
            keyword in response_lower
            for keyword in ["guidance", "help", "how to", "best practice"]
        ):
            return ContentType.GUIDANCE
        else:
            return ContentType.GENERAL

    def _calculate_intelligent_ttl(
        self,
        content_type: ContentType,
        response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Calculate intelligent TTL based on content type and characteristics."""
        base_ttl = self.ttl_config[content_type]

        # Adjust TTL based on response characteristics
        response_length = len(response)

        # Longer, more detailed responses get longer TTL
        if response_length > 2000:
            base_ttl = int(base_ttl * 1.5)
        elif response_length < 500:
            base_ttl = int(base_ttl * 0.7)

        # Adjust based on context stability
        if context:
            # Business context changes affect TTL
            if context.get("business_context", {}).get("maturity_level") == "Initial":
                base_ttl = int(base_ttl * 0.8)  # Shorter TTL for rapidly changing orgs

            # Framework-specific adjustments
            framework = context.get("framework", "")
            if framework in ["GDPR", "HIPAA"]:  # Regulatory frameworks change less
                base_ttl = int(base_ttl * 1.2)

        # Ensure TTL is within bounds
        return max(self.min_ttl, min(self.max_ttl, base_ttl))

    async def _find_similar_cached_response(
        self, prompt: str, context: Dict[str, Any], threshold: float
    ) -> Optional[Dict[str, Any]]:
        """Find cached responses for similar prompts using semantic similarity."""
        try:
            # This is a simplified similarity check
            # In production, you might use embedding-based similarity

            # For now, check for similar prompts based on keywords
            set(re.findall(r"\b\w+\b", prompt.lower()))

            # Get recent cache keys for the same content type
            context.get("content_type", "general")

            # This would need to be implemented with Redis SCAN in production
            # For now, return None to indicate no similar responses found
            return None

        except Exception as e:
            logger.warning(f"Similarity search error: {e}")
            return None

    def _summarize_context(
        self, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a summary of context for cache metadata."""
        if not context:
            return {}

        return {
            "framework": context.get("framework"),
            "content_type": context.get("content_type"),
            "business_industry": context.get("business_context", {}).get("industry"),
            "has_business_context": bool(context.get("business_context")),
        }

    def _record_cache_hit(self) -> None:
        """Record a cache hit for metrics."""
        self.metrics["hits"] += 1
        self.metrics["total_requests"] += 1

    def _record_cache_miss(self) -> None:
        """Record a cache miss for metrics."""
        self.metrics["misses"] += 1
        self.metrics["total_requests"] += 1

    def _update_cache_metrics(self, cache_data: Dict[str, Any]) -> None:
        """Update cache metrics with new cached data."""
        # Estimate cost savings (rough calculation)
        response_length = len(cache_data["response"])
        estimated_tokens = response_length // 4  # Rough token estimate
        estimated_cost_savings = estimated_tokens * 0.00001  # Rough cost per token

        self.metrics["cost_savings"] += estimated_cost_savings
        self.metrics["cache_size_bytes"] += len(json.dumps(cache_data))

    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics."""
        hit_rate = (
            (self.metrics["hits"] / self.metrics["total_requests"] * 100)
            if self.metrics["total_requests"] > 0
            else 0
        )

        return {
            "hit_rate_percentage": round(hit_rate, 2),
            "total_hits": self.metrics["hits"],
            "total_misses": self.metrics["misses"],
            "total_requests": self.metrics["total_requests"],
            "estimated_cost_savings": round(self.metrics["cost_savings"], 4),
            "cache_size_mb": round(self.metrics["cache_size_bytes"] / 1024 / 1024, 2),
            "ttl_config": {ct.value: ttl for ct, ttl in self.ttl_config.items()},
        }

    async def clear_cache_pattern(self, pattern: str) -> int:
        """Clear cache entries matching a pattern."""
        if not self.cache_manager:
            await self.initialize()

        return await self.cache_manager.clear_pattern(f"ai_response:{pattern}")

    async def invalidate_user_ai_cache(self, user_id: str) -> int:
        """Invalidate all AI cache entries for a specific user."""
        # This would need user-specific cache keys in production
        # For now, return 0 as we don't store user-specific AI responses
        return 0


# Global AI response cache instance
ai_response_cache = AIResponseCache()


async def get_ai_cache() -> AIResponseCache:
    """Get the global AI response cache instance."""
    if ai_response_cache.cache_manager is None:
        await ai_response_cache.initialize()
    return ai_response_cache
