"""
Optimized Assessment Service with caching and performance improvements.

Implements query optimization, caching, and batch operations for assessments.
"""

from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from core.exceptions import DatabaseException, NotFoundException
from database.assessment_session import AssessmentSession
from database.business_profile import BusinessProfile
from database.user import User
from services.framework_service import get_relevant_frameworks

from infrastructure.performance import (
    CacheManager,
    cached_query,
    cache_key_builder,
    QueryCache,
    measure_performance,
    get_metrics,
    EagerLoadingOptimizer
)

logger = logging.getLogger(__name__)


class OptimizedAssessmentService:
    """
    Optimized assessment service with caching and query optimization.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.query_cache = QueryCache()
        self.metrics = get_metrics()
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the service."""
        if not self._initialized:
            await self.cache_manager.initialize()
            await self.query_cache.initialize()
            self._initialized = True
            
    @measure_performance("assessment.start_session")
    async def start_assessment_session(
        self,
        db: AsyncSession,
        user: User,
        session_type: str = "compliance_scoping",
        business_profile_id: Optional[UUID] = None,
    ) -> AssessmentSession:
        """Start a new assessment session with caching."""
        await self.initialize()
        
        # Check cache for active session
        cache_key = cache_key_builder(
            "assessment:active",
            user_id=str(user.id)
        )
        
        cached_session = await self.cache_manager.get(cache_key)
        if cached_session:
            self.metrics.increment_counter("cache.assessment.hit")
            return AssessmentSession(**cached_session)
            
        try:
            # Optimized query with eager loading
            stmt = (
                select(AssessmentSession)
                .where(AssessmentSession.user_id == user.id)
                .where(AssessmentSession.status == "in_progress")
                .order_by(AssessmentSession.created_at.desc())
                .options(
                    selectinload(AssessmentSession.business_profile),
                    selectinload(AssessmentSession.questions)
                )
            )
            
            result = await db.execute(stmt)
            existing_session = result.scalars().first()
            
            if existing_session:
                # Cache the active session
                await self.cache_manager.set(
                    cache_key,
                    existing_session.to_dict(),
                    ttl=300  # 5 minutes
                )
                return existing_session
                
            # Get business profile if not provided
            if not business_profile_id:
                # Use cached query for business profile
                profile = await self._get_cached_business_profile(db, user.id)
                business_profile_id = profile.id if profile else None
                
            # Create new session
            new_session = AssessmentSession(
                user_id=user.id,
                business_profile_id=business_profile_id,
                session_type=session_type,
                status="in_progress",
                total_stages=5,
                current_stage=1,
                responses={},
            )
            
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            
            # Cache the new session
            await self.cache_manager.set(
                cache_key,
                new_session.to_dict(),
                ttl=300
            )
            
            # Invalidate user's session list cache
            await self._invalidate_user_sessions_cache(user.id)
            
            return new_session
            
        except sa.exc.SQLAlchemyError as e:
            await db.rollback()
            self.metrics.increment_counter("assessment.error.start_session")
            raise DatabaseException(f"Error starting assessment session: {e}")
            
    @cached_query(ttl=600, prefix="assessment:session")
    async def get_assessment_session(
        self,
        db: AsyncSession,
        user: User,
        session_id: UUID
    ) -> Optional[AssessmentSession]:
        """Get assessment session with caching."""
        try:
            # Optimized query with eager loading
            stmt = (
                select(AssessmentSession)
                .where(AssessmentSession.id == session_id)
                .where(AssessmentSession.user_id == user.id)
                .options(
                    joinedload(AssessmentSession.business_profile),
                    selectinload(AssessmentSession.questions),
                    selectinload(AssessmentSession.frameworks)
                )
            )
            
            result = await db.execute(stmt)
            return result.scalars().first()
            
        except sa.exc.SQLAlchemyError as e:
            self.metrics.increment_counter("assessment.error.get_session")
            raise DatabaseException(f"Error retrieving assessment session: {e}")
            
    @measure_performance("assessment.get_current_session")
    async def get_current_assessment_session(
        self,
        db: AsyncSession,
        user: User
    ) -> Optional[AssessmentSession]:
        """Get current active session with optimized query."""
        await self.initialize()
        
        # Check cache first
        cache_key = cache_key_builder(
            "assessment:current",
            user_id=str(user.id)
        )
        
        cached = await self.cache_manager.get(cache_key)
        if cached:
            self.metrics.increment_counter("cache.assessment.current.hit")
            return AssessmentSession(**cached)
            
        try:
            # Optimized query
            stmt = (
                select(AssessmentSession)
                .where(AssessmentSession.user_id == user.id)
                .where(AssessmentSession.status == "in_progress")
                .order_by(AssessmentSession.created_at.desc())
                .options(
                    joinedload(AssessmentSession.business_profile),
                    selectinload(AssessmentSession.questions)
                )
            )
            
            result = await db.execute(stmt)
            session = result.scalars().first()
            
            if session:
                # Cache the result
                await self.cache_manager.set(
                    cache_key,
                    session.to_dict(),
                    ttl=300
                )
                
            return session
            
        except sa.exc.SQLAlchemyError as e:
            self.metrics.increment_counter("assessment.error.get_current")
            raise DatabaseException(f"Error retrieving current session: {e}")
            
    @cached_query(ttl=1800, prefix="assessment:user_sessions")
    async def get_user_assessment_sessions(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 50,
        offset: int = 0
    ) -> List[AssessmentSession]:
        """Get user's assessment sessions with pagination and caching."""
        try:
            # Optimized query with eager loading and pagination
            stmt = (
                select(AssessmentSession)
                .where(AssessmentSession.user_id == user.id)
                .order_by(AssessmentSession.created_at.desc())
                .limit(limit)
                .offset(offset)
                .options(
                    selectinload(AssessmentSession.business_profile),
                    selectinload(AssessmentSession.frameworks)
                )
            )
            
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except sa.exc.SQLAlchemyError as e:
            self.metrics.increment_counter("assessment.error.get_user_sessions")
            raise DatabaseException(f"Error retrieving user sessions: {e}")
            
    async def update_assessment_response(
        self,
        db: AsyncSession,
        user: User,
        session_id: UUID,
        question_id: str,
        answer: Dict,
    ) -> AssessmentSession:
        """Update assessment response with cache invalidation."""
        await self.initialize()
        
        try:
            # Get session (may use cache)
            session = await self.get_assessment_session(db, user, session_id)
            if not session:
                raise NotFoundException(f"Assessment session {session_id} not found")
                
            if session.status != "in_progress":
                raise ValueError("Assessment session is not in progress")
                
            # Update responses
            if not session.responses:
                session.responses = {}
            session.responses[question_id] = answer
            session.updated_at = datetime.utcnow()
            
            # Determine stage progression
            if await self._should_progress_stage(session, question_id):
                session.current_stage += 1
                
            await db.commit()
            await db.refresh(session)
            
            # Invalidate relevant caches
            await self._invalidate_session_caches(user.id, session_id)
            
            return session
            
        except sa.exc.SQLAlchemyError as e:
            await db.rollback()
            self.metrics.increment_counter("assessment.error.update_response")
            raise DatabaseException(f"Error updating assessment response: {e}")
            
    async def complete_assessment(
        self,
        db: AsyncSession,
        user: User,
        session_id: UUID
    ) -> AssessmentSession:
        """Complete an assessment session."""
        await self.initialize()
        
        try:
            session = await self.get_assessment_session(db, user, session_id)
            if not session:
                raise NotFoundException(f"Assessment session {session_id} not found")
                
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            
            # Calculate and store results
            session.results = await self._calculate_assessment_results(session)
            
            await db.commit()
            await db.refresh(session)
            
            # Invalidate all related caches
            await self._invalidate_session_caches(user.id, session_id)
            await self._invalidate_user_sessions_cache(user.id)
            
            return session
            
        except sa.exc.SQLAlchemyError as e:
            await db.rollback()
            self.metrics.increment_counter("assessment.error.complete")
            raise DatabaseException(f"Error completing assessment: {e}")
            
    # Batch operations for performance
    async def get_bulk_assessments(
        self,
        db: AsyncSession,
        session_ids: List[UUID]
    ) -> List[AssessmentSession]:
        """Get multiple assessment sessions in a single query."""
        await self.initialize()
        
        # Check cache for each ID
        cache_keys = [
            cache_key_builder("assessment:session", session_id=str(sid))
            for sid in session_ids
        ]
        
        cached_results = await self.cache_manager.mget(cache_keys)
        
        # Find missing sessions
        missing_ids = []
        results = []
        
        for sid, cached in zip(session_ids, cached_results.values()):
            if cached:
                results.append(AssessmentSession(**cached))
            else:
                missing_ids.append(sid)
                
        if missing_ids:
            # Fetch missing sessions from database
            stmt = (
                select(AssessmentSession)
                .where(AssessmentSession.id.in_(missing_ids))
                .options(
                    selectinload(AssessmentSession.business_profile),
                    selectinload(AssessmentSession.questions)
                )
            )
            
            result = await db.execute(stmt)
            db_sessions = result.scalars().all()
            
            # Cache the fetched sessions
            cache_mapping = {}
            for session in db_sessions:
                cache_key = cache_key_builder(
                    "assessment:session",
                    session_id=str(session.id)
                )
                cache_mapping[cache_key] = session.to_dict()
                results.append(session)
                
            if cache_mapping:
                await self.cache_manager.mset(cache_mapping, ttl=600)
                
        return results
        
    # Helper methods
    async def _get_cached_business_profile(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[BusinessProfile]:
        """Get business profile with caching."""
        cache_key = cache_key_builder("business_profile", user_id=str(user_id))
        
        cached = await self.cache_manager.get(cache_key)
        if cached:
            return BusinessProfile(**cached)
            
        stmt = select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        result = await db.execute(stmt)
        profile = result.scalars().first()
        
        if profile:
            await self.cache_manager.set(cache_key, profile.to_dict(), ttl=3600)
            
        return profile
        
    async def _should_progress_stage(
        self,
        session: AssessmentSession,
        question_id: str
    ) -> bool:
        """Determine if stage should progress."""
        # Implementation depends on business logic
        # This is a simplified example
        stage_questions = {
            1: ['basic_info', 'company_size'],
            2: ['industry', 'sub_industry'],
            3: ['data_types', 'data_processing'],
            4: ['tech_stack', 'cloud_providers'],
            5: ['compliance_goals', 'timeline']
        }
        
        current_stage_questions = stage_questions.get(session.current_stage, [])
        answered_questions = set(session.responses.keys())
        
        return all(q in answered_questions for q in current_stage_questions)
        
    async def _calculate_assessment_results(
        self,
        session: AssessmentSession
    ) -> Dict[str, Any]:
        """Calculate assessment results."""
        # Implementation depends on business logic
        return {
            'score': 85,
            'recommendations': [],
            'identified_frameworks': [],
            'risk_level': 'medium'
        }
        
    async def _invalidate_session_caches(
        self,
        user_id: UUID,
        session_id: UUID
    ) -> None:
        """Invalidate caches related to a session."""
        keys_to_delete = [
            cache_key_builder("assessment:session", session_id=str(session_id)),
            cache_key_builder("assessment:active", user_id=str(user_id)),
            cache_key_builder("assessment:current", user_id=str(user_id))
        ]
        
        for key in keys_to_delete:
            await self.cache_manager.delete(key)
            
    async def _invalidate_user_sessions_cache(self, user_id: UUID) -> None:
        """Invalidate user's session list cache."""
        pattern = f"assessment:user_sessions:*{user_id}*"
        await self.cache_manager.delete_pattern(pattern)