"""
Google Cached Content Integration

Implements Google's native caching system for improved performance and cost reduction.
Works alongside existing custom caching for optimal performance.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

import google.generativeai as genai
from config.ai_config import get_ai_config
from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CacheMetadata:
    """Metadata for cached content tracking."""
    cache_id: str
    framework_id: str
    business_profile_id: str
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0
    last_accessed: Optional[datetime] = None


class GoogleCachedContentManager:
    """
    Google Cached Content API integration for ruleIQ.
    
    Provides intelligent caching of assessment contexts, business profiles,
    and regulatory content using Google's native caching system.
    """
    
    def __init__(self):
        self.config = get_ai_config()
        self.cache_registry: Dict[str, CacheMetadata] = {}
        
        # TTL strategies for different content types
        self.ttl_strategies = {
            'assessment_context': timedelta(hours=2),
            'business_profile': timedelta(hours=6),
            'regulatory_content': timedelta(hours=12),
            'policy_template': timedelta(days=1),
            'framework_guidance': timedelta(hours=4)
        }
    
    def create_assessment_cache(
        self, 
        framework_id: str, 
        business_profile: dict,
        additional_context: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create cached content for assessment context.
        
        Args:
            framework_id: Compliance framework identifier
            business_profile: Business profile data
            additional_context: Additional context strings
            
        Returns:
            Cache ID if successful, None if failed
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(
                'assessment', framework_id, business_profile.get('id', 'unknown')
            )
            
            # Check if cache already exists
            if cache_key in self.cache_registry:
                existing_cache = self.cache_registry[cache_key]
                if existing_cache.expires_at > datetime.utcnow():
                    logger.info(f"Using existing cache: {cache_key}")
                    existing_cache.hit_count += 1
                    existing_cache.last_accessed = datetime.utcnow()
                    return existing_cache.cache_id
            
            # Prepare cache content
            cache_content = self._prepare_assessment_content(
                framework_id, business_profile, additional_context
            )
            
            # Create Google cached content
            cached_content = genai.caching.CachedContent.create(
                model=self.config.default_model.value,
                contents=cache_content,
                ttl=self.ttl_strategies['assessment_context'],
                display_name=f"assessment_context_{framework_id}_{business_profile.get('id', 'unknown')}"
            )
            
            # Store metadata
            metadata = CacheMetadata(
                cache_id=cached_content.name,
                framework_id=framework_id,
                business_profile_id=business_profile.get('id', 'unknown'),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + self.ttl_strategies['assessment_context']
            )
            
            self.cache_registry[cache_key] = metadata
            
            logger.info(f"Created assessment cache: {cache_key}")
            return cached_content.name
            
        except Exception as e:
            logger.error(f"Failed to create assessment cache: {e}")
            return None
    
    def create_business_profile_cache(
        self, 
        business_profile: dict,
        regulatory_context: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create cached content for business profile context.
        
        Args:
            business_profile: Complete business profile data
            regulatory_context: Relevant regulatory information
            
        Returns:
            Cache ID if successful, None if failed
        """
        try:
            cache_key = self._generate_cache_key(
                'business_profile', business_profile.get('id', 'unknown')
            )
            
            # Check existing cache
            if cache_key in self.cache_registry:
                existing_cache = self.cache_registry[cache_key]
                if existing_cache.expires_at > datetime.utcnow():
                    existing_cache.hit_count += 1
                    existing_cache.last_accessed = datetime.utcnow()
                    return existing_cache.cache_id
            
            # Prepare content
            cache_content = self._prepare_business_profile_content(
                business_profile, regulatory_context
            )
            
            # Create cached content
            cached_content = genai.caching.CachedContent.create(
                model=self.config.default_model.value,
                contents=cache_content,
                ttl=self.ttl_strategies['business_profile'],
                display_name=f"business_profile_{business_profile.get('id', 'unknown')}"
            )
            
            # Store metadata
            metadata = CacheMetadata(
                cache_id=cached_content.name,
                framework_id='',
                business_profile_id=business_profile.get('id', 'unknown'),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + self.ttl_strategies['business_profile']
            )
            
            self.cache_registry[cache_key] = metadata
            
            logger.info(f"Created business profile cache: {cache_key}")
            return cached_content.name
            
        except Exception as e:
            logger.error(f"Failed to create business profile cache: {e}")
            return None
    
    def get_cached_model(self, cache_id: str) -> Optional[Any]:
        """
        Get a model instance with cached content.
        
        Args:
            cache_id: Google cached content ID
            
        Returns:
            Model instance with cached content or None
        """
        try:
            # Get cached content
            cached_content = genai.caching.CachedContent.get(cache_id)
            
            # Create model with cached content
            model = genai.GenerativeModel(
                model_name=cached_content.model,
                cached_content=cached_content
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to get cached model: {e}")
            return None
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            cache_key: Cache key to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if cache_key in self.cache_registry:
                metadata = self.cache_registry[cache_key]
                
                # Delete from Google
                cached_content = genai.caching.CachedContent.get(metadata.cache_id)
                cached_content.delete()
                
                # Remove from registry
                del self.cache_registry[cache_key]
                
                logger.info(f"Invalidated cache: {cache_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False
    
    def cleanup_expired_caches(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of caches cleaned up
        """
        cleaned_count = 0
        current_time = datetime.utcnow()
        expired_keys = []
        
        for cache_key, metadata in self.cache_registry.items():
            if metadata.expires_at <= current_time:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            if self.invalidate_cache(cache_key):
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired caches")
        return cleaned_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_caches = len(self.cache_registry)
        total_hits = sum(metadata.hit_count for metadata in self.cache_registry.values())
        
        # Calculate hit rates by type
        framework_caches = [m for m in self.cache_registry.values() if m.framework_id]
        profile_caches = [m for m in self.cache_registry.values() if not m.framework_id]
        
        return {
            'total_caches': total_caches,
            'total_hits': total_hits,
            'framework_caches': len(framework_caches),
            'profile_caches': len(profile_caches),
            'average_hits_per_cache': total_hits / total_caches if total_caches > 0 else 0,
            'cache_registry_size': len(self.cache_registry)
        }
    
    def _generate_cache_key(self, content_type: str, *identifiers: str) -> str:
        """Generate a unique cache key."""
        key_data = f"{content_type}:{'|'.join(identifiers)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _prepare_assessment_content(
        self, 
        framework_id: str, 
        business_profile: dict,
        additional_context: Optional[List[str]] = None
    ) -> List[str]:
        """Prepare content for assessment caching."""
        content = [
            f"Assessment Framework: {framework_id}",
            f"Business Profile: {json.dumps(business_profile, indent=2)}",
            f"Industry: {business_profile.get('industry', 'Unknown')}",
            f"Company Size: {business_profile.get('employee_count', 'Unknown')}",
            f"Location: {business_profile.get('location', 'Unknown')}"
        ]
        
        if additional_context:
            content.extend(additional_context)
        
        return content
    
    def _prepare_business_profile_content(
        self, 
        business_profile: dict,
        regulatory_context: Optional[List[str]] = None
    ) -> List[str]:
        """Prepare content for business profile caching."""
        content = [
            f"Business Profile: {json.dumps(business_profile, indent=2)}",
            f"Regulatory Requirements: {regulatory_context or []}"
        ]
        
        return content


# Global instance
google_cache_manager = GoogleCachedContentManager()
