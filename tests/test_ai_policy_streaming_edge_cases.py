"""
Edge case tests for AI Policy streaming functionality.
Tests timeout handling, partial failures, reconnection scenarios, and buffer management.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import time
from typing import AsyncGenerator

from fastapi import HTTPException
from api.schemas.ai_policy import (
    PolicyGenerationRequest,
    PolicyType,
    BusinessContext,
    PolicyStreamingChunk
)
from services.ai.policy_generator import PolicyGenerator
from database.compliance_framework import ComplianceFramework


class TestStreamingEdgeCases:
    """Test edge cases in policy streaming."""
    
    @pytest.fixture
    def policy_generator(self):
        """Create a PolicyGenerator instance with mocked dependencies."""
        with patch('services.ai.google_client.GoogleAIClient'), \
             patch('services.ai.openai_client.OpenAIClient'):
            generator = PolicyGenerator()
            generator.google_client = Mock()
            generator.openai_client = Mock()
            generator.circuit_breaker = Mock()
            generator.template_processor = Mock()
            return generator
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample request."""
        return PolicyGenerationRequest(
            framework_id="gdpr",
            business_context=BusinessContext(
                organization_name="Test Company",
                industry="Technology",
                processes_personal_data=True
            ),
            policy_type=PolicyType.PRIVACY_POLICY
        )
    
    @pytest.fixture
    def sample_framework(self):
        """Create a sample framework."""
        framework = Mock(spec=ComplianceFramework)
        framework.id = "gdpr"
        framework.name = "GDPR"
        return framework
    
    @pytest.mark.asyncio
    async def test_streaming_timeout_handling(self, policy_generator, sample_request, sample_framework):
        """Test handling of timeouts during streaming."""
        async def mock_slow_stream(*args, **kwargs):
            yield PolicyStreamingChunk(
                chunk_id="1",
                content="Start of content",
                chunk_type="content"
            )
            # Simulate a timeout
            await asyncio.sleep(10)
            yield PolicyStreamingChunk(
                chunk_id="2",
                content="This should timeout",
                chunk_type="content"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_slow_stream):
            chunks = []
            try:
                async with asyncio.timeout(1):  # 1 second timeout
                    async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                        chunks.append(chunk)
            except asyncio.TimeoutError:
                pass
            
            # Should have received at least metadata and first content chunk
            assert len(chunks) >= 2
            assert any(c.chunk_type == "metadata" for c in chunks)
            assert any(c.content == "Start of content" for c in chunks)
    
    @pytest.mark.asyncio
    async def test_streaming_partial_failure_recovery(self, policy_generator, sample_request, sample_framework):
        """Test recovery from partial failures during streaming."""
        call_count = [0]
        
        async def mock_partial_failure(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First attempt fails after some chunks
                yield PolicyStreamingChunk(
                    chunk_id="1",
                    content="Partial content",
                    chunk_type="content"
                )
                raise ConnectionError("Network interrupted")
            else:
                # Fallback succeeds
                yield PolicyStreamingChunk(
                    chunk_id="2",
                    content="Recovered content",
                    chunk_type="content"
                )
                yield PolicyStreamingChunk(
                    chunk_id="3",
                    content="",
                    chunk_type="complete"
                )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_partial_failure), \
             patch.object(policy_generator, '_stream_with_openai', side_effect=mock_partial_failure):
            
            chunks = []
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                chunks.append(chunk)
            
            # Should have recovered with fallback
            assert any(c.content == "Recovered content" for c in chunks)
    
    @pytest.mark.asyncio
    async def test_streaming_empty_response_handling(self, policy_generator, sample_request, sample_framework):
        """Test handling of empty or null responses during streaming."""
        async def mock_empty_stream(*args, **kwargs):
            # Yield some None/empty chunks
            yield PolicyStreamingChunk(
                chunk_id="1",
                content="",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="2",
                content=None,
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="3",
                content="Actual content",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="4",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_empty_stream):
            chunks = []
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                if chunk.chunk_type == "content" and chunk.content:
                    chunks.append(chunk)
            
            # Should only have non-empty content
            content_chunks = [c for c in chunks if c.chunk_type == "content"]
            assert all(c.content for c in content_chunks)
    
    @pytest.mark.asyncio
    async def test_streaming_unicode_handling(self, policy_generator, sample_request, sample_framework):
        """Test handling of unicode and special characters in streaming."""
        async def mock_unicode_stream(*args, **kwargs):
            # Test various unicode scenarios
            yield PolicyStreamingChunk(
                chunk_id="1",
                content="Unicode test: €£¥ émojis: 😀🚀 中文字符",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="2",
                content="Special chars: \n\t\r \"quotes\" 'apostrophes'",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="3",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_unicode_stream):
            chunks = []
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                chunks.append(chunk)
            
            # Verify unicode content preserved
            content = "".join(c.content for c in chunks if c.chunk_type == "content")
            assert "€£¥" in content
            assert "😀🚀" in content
            assert "中文字符" in content
    
    @pytest.mark.asyncio
    async def test_streaming_large_chunk_handling(self, policy_generator, sample_request, sample_framework):
        """Test handling of very large chunks."""
        async def mock_large_chunk_stream(*args, **kwargs):
            # Generate a very large chunk
            large_content = "x" * (1024 * 1024)  # 1MB chunk
            yield PolicyStreamingChunk(
                chunk_id="1",
                content=large_content,
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="2",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_large_chunk_stream):
            chunks = []
            total_size = 0
            
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                chunks.append(chunk)
                if chunk.chunk_type == "content":
                    total_size += len(chunk.content)
            
            # Should handle large chunks
            assert total_size >= 1024 * 1024
            assert chunks[-1].chunk_type == "complete"
    
    @pytest.mark.asyncio
    async def test_streaming_rapid_chunks(self, policy_generator, sample_request, sample_framework):
        """Test handling of rapid consecutive chunks."""
        async def mock_rapid_stream(*args, **kwargs):
            # Generate many chunks rapidly
            for i in range(100):
                yield PolicyStreamingChunk(
                    chunk_id=str(i),
                    content=f"Chunk {i}",
                    chunk_type="content"
                )
                # No delay between chunks
            yield PolicyStreamingChunk(
                chunk_id="complete",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_rapid_stream):
            chunks = []
            start_time = time.time()
            
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                chunks.append(chunk)
            
            elapsed = time.time() - start_time
            
            # Should process all chunks quickly
            assert len(chunks) > 100  # metadata + 100 content + complete
            assert elapsed < 2  # Should be fast
    
    @pytest.mark.asyncio
    async def test_streaming_cancellation(self, policy_generator, sample_request, sample_framework):
        """Test graceful cancellation of streaming."""
        async def mock_cancellable_stream(*args, **kwargs):
            try:
                for i in range(100):
                    yield PolicyStreamingChunk(
                        chunk_id=str(i),
                        content=f"Chunk {i}",
                        chunk_type="content"
                    )
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                # Clean up on cancellation
                yield PolicyStreamingChunk(
                    chunk_id="cancelled",
                    content="Stream cancelled",
                    chunk_type="error"
                )
                raise
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_cancellable_stream):
            chunks = []
            
            async def consume_stream():
                async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                    chunks.append(chunk)
                    if len(chunks) >= 5:  # Cancel after 5 chunks
                        raise asyncio.CancelledError()
            
            with pytest.raises(asyncio.CancelledError):
                await consume_stream()
            
            # Should have received some chunks before cancellation
            assert len(chunks) >= 5
            assert len(chunks) < 100  # Not all chunks
    
    @pytest.mark.asyncio
    async def test_streaming_duplicate_chunk_ids(self, policy_generator, sample_request, sample_framework):
        """Test handling of duplicate chunk IDs."""
        async def mock_duplicate_ids(*args, **kwargs):
            # Generate chunks with duplicate IDs
            yield PolicyStreamingChunk(
                chunk_id="duplicate",
                content="First chunk",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="duplicate",  # Same ID
                content="Second chunk",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="unique",
                content="Third chunk",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="complete",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_duplicate_ids):
            chunks = []
            chunk_ids = set()
            
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                chunks.append(chunk)
                if chunk.chunk_id in chunk_ids and chunk.chunk_type != "metadata":
                    # Track duplicates but don't fail
                    pass
                chunk_ids.add(chunk.chunk_id)
            
            # Should handle duplicates gracefully
            assert len(chunks) == 5  # metadata + 4 chunks
            content = "".join(c.content for c in chunks if c.chunk_type == "content")
            assert "First chunk" in content
            assert "Second chunk" in content
    
    @pytest.mark.asyncio
    async def test_streaming_malformed_json_in_metadata(self, policy_generator, sample_request, sample_framework):
        """Test handling of malformed JSON in metadata chunks."""
        async def mock_malformed_metadata(*args, **kwargs):
            # First send malformed metadata
            yield PolicyStreamingChunk(
                chunk_id="metadata",
                content="{invalid json}",
                chunk_type="metadata"
            )
            yield PolicyStreamingChunk(
                chunk_id="content",
                content="Regular content",
                chunk_type="content"
            )
            yield PolicyStreamingChunk(
                chunk_id="complete",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(policy_generator, '_stream_with_google', side_effect=mock_malformed_metadata):
            chunks = []
            errors = []
            
            async for chunk in policy_generator.generate_policy_stream(sample_request, sample_framework):
                chunks.append(chunk)
                if chunk.chunk_type == "metadata":
                    try:
                        json.loads(chunk.content)
                    except json.JSONDecodeError as e:
                        errors.append(e)
            
            # Should continue despite malformed metadata
            assert len(chunks) >= 2
            assert any(c.content == "Regular content" for c in chunks)


class TestStreamingConcurrency:
    """Test concurrent streaming scenarios."""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_streams(self):
        """Test multiple concurrent streaming requests."""
        generator = PolicyGenerator()
        
        async def mock_stream(request_id):
            for i in range(5):
                yield PolicyStreamingChunk(
                    chunk_id=f"{request_id}_{i}",
                    content=f"Request {request_id} chunk {i}",
                    chunk_type="content"
                )
                await asyncio.sleep(0.01)
            yield PolicyStreamingChunk(
                chunk_id=f"{request_id}_complete",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(generator, '_stream_with_google', side_effect=lambda *args, **kwargs: mock_stream(kwargs.get('request_id', 'default'))):
            # Create multiple concurrent streaming tasks
            async def consume_stream(request_id):
                chunks = []
                request = PolicyGenerationRequest(
                    framework_id="gdpr",
                    business_context=BusinessContext(
                        organization_name=f"Company {request_id}",
                        industry="Tech",
                        processes_personal_data=True
                    ),
                    policy_type=PolicyType.PRIVACY_POLICY
                )
                framework = Mock()
                framework.id = "gdpr"
                
                async for chunk in generator.generate_policy_stream(request, framework):
                    chunks.append(chunk)
                return chunks
            
            # Run multiple streams concurrently
            results = await asyncio.gather(
                consume_stream(1),
                consume_stream(2),
                consume_stream(3)
            )
            
            # Each stream should complete independently
            assert len(results) == 3
            for i, chunks in enumerate(results):
                assert len(chunks) > 5  # metadata + content + complete
                assert chunks[-1].chunk_type == "complete"
    
    @pytest.mark.asyncio
    async def test_stream_isolation(self):
        """Test that streams don't interfere with each other."""
        generator = PolicyGenerator()
        
        stream_data = {}
        
        async def mock_isolated_stream(prompt, request):
            org_name = request.business_context.organization_name
            stream_data[org_name] = []
            
            for i in range(3):
                chunk = PolicyStreamingChunk(
                    chunk_id=f"{org_name}_{i}",
                    content=f"Content for {org_name}",
                    chunk_type="content"
                )
                stream_data[org_name].append(chunk)
                yield chunk
                await asyncio.sleep(0.01)
            
            yield PolicyStreamingChunk(
                chunk_id=f"{org_name}_complete",
                content="",
                chunk_type="complete"
            )
        
        with patch.object(generator, '_stream_with_google', side_effect=mock_isolated_stream):
            # Create different requests
            requests = []
            for i in range(3):
                requests.append(PolicyGenerationRequest(
                    framework_id="gdpr",
                    business_context=BusinessContext(
                        organization_name=f"Company_{i}",
                        industry="Tech",
                        processes_personal_data=True
                    ),
                    policy_type=PolicyType.PRIVACY_POLICY
                ))
            
            framework = Mock()
            framework.id = "gdpr"
            
            # Consume streams concurrently
            async def consume(request):
                chunks = []
                async for chunk in generator.generate_policy_stream(request, framework):
                    chunks.append(chunk)
                return chunks
            
            results = await asyncio.gather(*[consume(req) for req in requests])
            
            # Verify isolation
            for i, chunks in enumerate(results):
                org_name = f"Company_{i}"
                content_chunks = [c for c in chunks if c.chunk_type == "content"]
                for chunk in content_chunks:
                    assert org_name in chunk.content or org_name in chunk.chunk_id