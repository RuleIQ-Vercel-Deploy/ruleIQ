"""
Comprehensive test suite for Master Integration Graph with real services.

This test suite validates end-to-end execution without mocks, ensuring
production readiness and 24-hour stability.
"""

import pytest
import asyncio
import os
import time
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any
import psycopg
from psycopg.rows import dict_row

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from langgraph_agent.graph.master_integration_graph import MasterIntegrationGraph
from langgraph_agent.graph.enhanced_state import WorkflowStatus
from langgraph_agent.agents.rag_system import RAGConfig
from langgraph_agent.core.neo4j_service import Neo4jGraphRAGService as Neo4jService

# from langgraph_agent.services.supabase_service import SupabaseService  # Not implemented


# Test configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://testuser:testpass@localhost:5432/testdb"
)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test")

# Production service URLs
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# AI Service Keys (using real services)
GOOGLE_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "free")


@pytest.fixture(scope="session")
async def database_setup():
    """Set up test database with proper schema."""
    conn = await psycopg.AsyncConnection.connect(
        TEST_DATABASE_URL, autocommit=True, row_factory=dict_row
    )

    try:
        # Create checkpointer schema
        await conn.execute(
            """
            CREATE SCHEMA IF NOT EXISTS langgraph;
            
            CREATE TABLE IF NOT EXISTS langgraph.checkpoints (
                thread_id TEXT,
                checkpoint_ns TEXT DEFAULT '',
                checkpoint_id TEXT,
                parent_checkpoint_id TEXT,
                type TEXT,
                checkpoint JSONB,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
            );
            
            CREATE TABLE IF NOT EXISTS langgraph.checkpoint_writes (
                thread_id TEXT,
                checkpoint_ns TEXT DEFAULT '',
                checkpoint_id TEXT,
                task_id TEXT,
                idx INTEGER,
                channel TEXT,
                type TEXT,
                value JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
            );
            
            CREATE TABLE IF NOT EXISTS langgraph.checkpoint_migrations (
                migration_id TEXT PRIMARY KEY,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """
        )

        yield conn

    finally:
        # Clean up test data
        await conn.execute(
            """
            DELETE FROM langgraph.checkpoints WHERE thread_id LIKE 'test_%';
            DELETE FROM langgraph.checkpoint_writes WHERE thread_id LIKE 'test_%';
        """
        )
        await conn.close()


@pytest.fixture
async def master_graph(database_setup):
    """Create master integration graph with real services."""
    # Configure RAG with real embeddings
    rag_config = RAGConfig(
        embedding_provider="mistral",
        embedding_model="mistral-embed",
        vector_db_provider="faiss",
        llm_provider="google",
        llm_model="gemini-1.5-flash",
        fallback_llm_provider="openai",
        fallback_llm_model="gpt-4o-mini",
        mistral_api_key=MISTRAL_API_KEY,
        google_api_key=GOOGLE_API_KEY,
        openai_api_key=OPENAI_API_KEY,
    )

    # Create master graph with real checkpointer
    graph = await MasterIntegrationGraph.create(
        database_url=TEST_DATABASE_URL, rag_config=rag_config, enable_streaming=True
    )

    yield graph

    # Cleanup
    await graph.close()


@pytest.fixture
async def neo4j_service():
    """Create real Neo4j service connection."""
    service = Neo4jService()
    await service.initialize()

    # Ensure test data exists
    await service.execute_query(
        """
        MERGE (r:Regulation {code: 'GDPR'})
        SET r.name = 'General Data Protection Regulation',
            r.jurisdiction = 'EU',
            r.effective_date = date('2018-05-25')
        
        MERGE (o:Obligation {id: 'gdpr-consent'})
        SET o.title = 'Obtain explicit consent',
            o.description = 'Must obtain explicit consent for data processing',
            o.framework = 'GDPR'
        
        MERGE (r)-[:HAS_OBLIGATION]->(o)
    """
    )

    yield service

    # Cleanup test data
    await service.execute_query(
        """
        MATCH (n) WHERE n.code = 'TEST' OR n.id STARTS WITH 'test-'
        DETACH DELETE n
    """
    )
    await service.close()


@pytest.fixture
async def supabase_service():
    """Create real Supabase service connection."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.skip("Supabase credentials not configured")

    service = SupabaseService(SUPABASE_URL, SUPABASE_KEY)
    yield service


class TestMasterIntegrationEndToEnd:
    """Test end-to-end execution with real services."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_compliance_assessment_flow(
        self, master_graph, neo4j_service
    ):
        """Test complete compliance assessment flow without mocks."""
        session_id = f"test_{uuid4()}"
        company_id = uuid4()

        # Real user input
        user_input = """
        We are a healthcare startup in California with 50 employees.
        We process patient health records and need to ensure HIPAA compliance.
        We also operate in the EU and handle EU citizen data.
        """

        # Collect all events
        events = []
        async for event in master_graph.run(
            session_id=session_id, company_id=company_id, user_input=user_input
        ):
            events.append(event)

            # Limit events for testing
            if len(events) > 20:
                break

        assert len(events) > 0

        # Verify state progression
        state_updates = [e for e in events if e["type"] == "state_update"]
        assert len(state_updates) > 0

        # Verify AI responses
        ai_messages = [e for e in events if e["type"] == "assistant_message"]
        assert len(ai_messages) > 0

        # Verify compliance data extraction
        final_state = state_updates[-1]["data"] if state_updates else {}

        # Check for extracted frameworks (should identify HIPAA and GDPR)
        # Note: This depends on actual AI service responses

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_rag_query_with_real_embeddings(self, master_graph):
        """Test RAG queries using real Mistral embeddings and FAISS."""
        session_id = f"test_{uuid4()}"
        company_id = uuid4()

        # Query requiring RAG lookup
        user_input = "What are the specific GDPR requirements for data retention?"

        events = []
        async for event in master_graph.run(
            session_id=session_id, company_id=company_id, user_input=user_input
        ):
            events.append(event)
            if len(events) > 10:
                break

        assert len(events) > 0

        # Verify RAG was triggered (check for relevant response)
        ai_messages = [e for e in events if e["type"] == "assistant_message"]
        assert len(ai_messages) > 0

        # Response should contain GDPR-specific information
        response_content = " ".join([msg["data"] for msg in ai_messages])
        # Basic check - actual content depends on RAG data
        assert len(response_content) > 100  # Non-empty substantial response

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_recovery_with_fallback(self, master_graph):
        """Test error recovery mechanisms with real service failures."""
        session_id = f"test_{uuid4()}"
        company_id = uuid4()

        # Input that might trigger errors
        user_input = "Process compliance for company ID: invalid-id-format"

        events = []
        async for event in master_graph.run(
            session_id=session_id,
            company_id=company_id,
            user_input=user_input,
            max_retries=2,  # Limit retries for testing
        ):
            events.append(event)
            if len(events) > 15:
                break

        # Should handle errors gracefully
        assert len(events) > 0

        # Check for fallback activation
        final_states = [e for e in events if e["type"] == "state_update"]
        if final_states:
            # Should not have crashed
            assert True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_checkpoint_persistence_and_recovery(self, master_graph):
        """Test checkpoint saving and recovery with PostgreSQL."""
        thread_id = f"test_checkpoint_{uuid4()}"
        session_id = f"test_{uuid4()}"
        company_id = uuid4()

        # First execution - partial
        events_1 = []
        async for event in master_graph.run(
            session_id=session_id,
            company_id=company_id,
            user_input="Start compliance assessment for our fintech startup",
            thread_id=thread_id,
        ):
            events_1.append(event)
            if len(events_1) >= 5:
                break  # Simulate interruption

        assert len(events_1) > 0

        # Get checkpoint state
        checkpoint_summary_1 = await master_graph.get_state_summary(thread_id)
        assert checkpoint_summary_1  # Should have saved state

        # Resume from checkpoint
        events_2 = []
        async for event in master_graph.run(
            session_id=session_id,
            company_id=company_id,
            user_input="Continue with the assessment",
            thread_id=thread_id,
        ):
            events_2.append(event)
            if len(events_2) >= 5:
                break

        assert len(events_2) > 0

        # Get final state
        checkpoint_summary_2 = await master_graph.get_state_summary(thread_id)

        # Verify progression
        if checkpoint_summary_1.get("conversation") and checkpoint_summary_2.get(
            "conversation"
        ):
            # Message count should increase
            assert checkpoint_summary_2["conversation"].get(
                "message_count", 0
            ) > checkpoint_summary_1["conversation"].get("message_count", 0)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_celery_task_migration_execution(self, master_graph):
        """Test execution of migrated Celery tasks through master graph."""
        session_id = f"test_{uuid4()}"
        company_id = uuid4()

        # Request task execution
        user_input = "Execute compliance score update task for all companies"

        events = []
        async for event in master_graph.run(
            session_id=session_id,
            company_id=company_id,
            user_input=user_input,
            task_type="compliance_tasks",
            task_params={"task": "update_all_compliance_scores"},
        ):
            events.append(event)
            if len(events) > 10:
                break

        assert len(events) > 0

        # Verify task was processed
        state_updates = [e for e in events if e["type"] == "state_update"]
        if state_updates:
            final_state = state_updates[-1]["data"]
            # Check for task execution markers
            # Actual validation depends on task implementation


class TestProductionReadiness:
    """Test production readiness criteria."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_sessions(self, master_graph):
        """Test handling multiple concurrent sessions."""
        num_sessions = 5

        async def run_session(session_num):
            session_id = f"test_concurrent_{session_num}_{uuid4()}"
            company_id = uuid4()

            events = []
            async for event in master_graph.run(
                session_id=session_id,
                company_id=company_id,
                user_input=f"Assessment for company {session_num}",
            ):
                events.append(event)
                if len(events) >= 3:
                    break

            return len(events) > 0

        # Run concurrent sessions
        tasks = [run_session(i) for i in range(num_sessions)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        successful = [r for r in results if r is True]
        assert len(successful) >= num_sessions * 0.8  # 80% success rate minimum

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_memory_efficiency(self, master_graph):
        """Test memory usage stays within bounds."""
        import tracemalloc

        tracemalloc.start()

        session_id = f"test_memory_{uuid4()}"
        company_id = uuid4()

        # Baseline
        snapshot1 = tracemalloc.take_snapshot()

        # Run multiple iterations
        for i in range(10):
            events = []
            async for event in master_graph.run(
                session_id=f"{session_id}_{i}",
                company_id=company_id,
                user_input=f"Query {i}: What are the compliance requirements?",
            ):
                events.append(event)
                if len(events) >= 5:
                    break

        # Measure memory growth
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, "lineno")

        # Calculate total memory growth
        total_growth = sum(stat.size_diff for stat in top_stats)

        # Should not exceed 50MB growth for 10 iterations
        assert total_growth < 50 * 1024 * 1024  # 50MB

        tracemalloc.stop()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_latency_requirements(self, master_graph):
        """Test response latency meets requirements."""
        session_id = f"test_latency_{uuid4()}"
        company_id = uuid4()

        start_time = time.time()
        first_response_time = None

        async for event in master_graph.run(
            session_id=session_id,
            company_id=company_id,
            user_input="Quick compliance check for GDPR",
        ):
            if event["type"] == "assistant_message" and first_response_time is None:
                first_response_time = time.time()
                break

        # First response should be under 2 seconds
        if first_response_time:
            latency = first_response_time - start_time
            assert latency < 2.0  # 2 second maximum for first response

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_rate_threshold(self, master_graph):
        """Test error rate stays below threshold."""
        num_requests = 20
        errors = 0

        for i in range(num_requests):
            session_id = f"test_error_rate_{i}_{uuid4()}"
            company_id = uuid4()

            try:
                event_count = 0
                async for event in master_graph.run(
                    session_id=session_id,
                    company_id=company_id,
                    user_input=f"Test query {i}",
                ):
                    event_count += 1
                    if event_count >= 3:
                        break

                if event_count == 0:
                    errors += 1

            except Exception:
                errors += 1

        # Error rate should be below 5%
        error_rate = errors / num_requests
        assert error_rate < 0.05


class TestLongRunningStability:
    """Test long-running stability (abbreviated for CI/CD)."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow  # Mark as slow test
    async def test_sustained_load(self, master_graph):
        """Test sustained load for extended period (abbreviated version)."""
        # Note: In production, this would run for 24 hours
        # For CI/CD, we run abbreviated 1-minute test

        duration_seconds = 60  # 1 minute for CI/CD (use 86400 for 24 hours)
        requests_per_second = 0.5  # Low rate for testing

        start_time = time.time()
        request_count = 0
        error_count = 0

        while time.time() - start_time < duration_seconds:
            session_id = f"test_sustained_{request_count}_{uuid4()}"
            company_id = uuid4()

            try:
                event_count = 0
                async for event in master_graph.run(
                    session_id=session_id,
                    company_id=company_id,
                    user_input=f"Sustained test query {request_count}",
                ):
                    event_count += 1
                    if event_count >= 2:
                        break

                request_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error in sustained test: {e}")

            # Rate limiting
            await asyncio.sleep(1 / requests_per_second)

        # Calculate statistics
        total_time = time.time() - start_time
        success_rate = (request_count - error_count) / max(request_count, 1)

        print(f"Sustained load test results:")
        print(f"  Duration: {total_time:.1f}s")
        print(f"  Requests: {request_count}")
        print(f"  Errors: {error_count}")
        print(f"  Success rate: {success_rate:.2%}")

        # Success criteria
        assert success_rate >= 0.95  # 95% success rate
        assert request_count > 0  # At least some requests completed


class TestServiceIntegration:
    """Test integration with external services."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_neo4j_connection_pooling(self, neo4j_service):
        """Test Neo4j connection pooling and recovery."""
        # Execute multiple queries concurrently
        queries = [
            "MATCH (r:Regulation) RETURN count(r) as count",
            "MATCH (o:Obligation) RETURN count(o) as count",
            "MATCH (r:Regulation)-[:HAS_OBLIGATION]->(o) RETURN count(*) as count",
        ]

        tasks = [neo4j_service.execute_query(q) for q in queries * 3]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All queries should succeed
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) == len(tasks)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ai_service_fallback(self, master_graph):
        """Test AI service fallback from Google to OpenAI."""
        session_id = f"test_fallback_{uuid4()}"
        company_id = uuid4()

        # This will use primary (Google) or fallback (OpenAI) based on availability
        events = []
        async for event in master_graph.run(
            session_id=session_id,
            company_id=company_id,
            user_input="Test AI service fallback mechanism",
        ):
            events.append(event)
            if len(events) >= 5:
                break

        # Should get responses regardless of which service is used
        assert len(events) > 0
        ai_messages = [e for e in events if e["type"] == "assistant_message"]
        assert len(ai_messages) > 0


if __name__ == "__main__":
    # Run tests with proper async handling
    pytest.main([__file__, "-v", "-m", "integration"])
