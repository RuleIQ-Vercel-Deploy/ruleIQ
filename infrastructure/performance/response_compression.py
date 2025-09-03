"""
Response compression middleware for API performance optimization.

Provides automatic compression of API responses to reduce bandwidth.
"""

import gzip
import logging
from typing import Optional, Set, Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers, MutableHeaders
import brotli
import zstandard as zstd

logger = logging.getLogger(__name__)


class ResponseCompressor:
    """Handles response compression with multiple algorithms."""
    
    # Minimum size for compression (bytes)
    MIN_SIZE = 1000
    
    # Content types to compress
    COMPRESSIBLE_TYPES = {
        'application/json',
        'application/javascript', 
        'application/xml',
        'text/plain',
        'text/html',
        'text/css',
        'text/csv',
        'text/xml',
    }
    
    @staticmethod
    def should_compress(
        content_type: Optional[str],
        content_length: Optional[int],
        accept_encoding: Optional[str]
    ) -> bool:
        """Determine if response should be compressed."""
        if not accept_encoding:
            return False
            
        if not content_type:
            return False
            
        # Check content type
        base_type = content_type.split(';')[0].strip().lower()
        if base_type not in ResponseCompressor.COMPRESSIBLE_TYPES:
            return False
            
        # Check size threshold
        if content_length and content_length < ResponseCompressor.MIN_SIZE:
            return False
            
        return True
        
    @staticmethod
    def get_best_encoding(accept_encoding: str) -> Optional[str]:
        """Get the best encoding based on client preferences."""
        accept_encoding = accept_encoding.lower()
        
        # Priority order: br > zstd > gzip > deflate
        if 'br' in accept_encoding:
            return 'br'
        elif 'zstd' in accept_encoding:
            return 'zstd'
        elif 'gzip' in accept_encoding:
            return 'gzip'
        elif 'deflate' in accept_encoding:
            return 'deflate'
            
        return None
        
    @staticmethod
    def compress_data(data: bytes, encoding: str) -> Optional[bytes]:
        """Compress data using specified encoding."""
        try:
            if encoding == 'gzip':
                return gzip.compress(data, compresslevel=6)
            elif encoding == 'br':
                return brotli.compress(data, quality=4)
            elif encoding == 'zstd':
                cctx = zstd.ZstdCompressor(level=3)
                return cctx.compress(data)
            elif encoding == 'deflate':
                import zlib
                return zlib.compress(data)
        except Exception as e:
            logger.error(f"Compression failed for {encoding}: {e}")
            
        return None


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic response compression.
    """
    
    def __init__(
        self,
        app,
        minimum_size: int = 1000,
        exclude_paths: Optional[Set[str]] = None,
        exclude_mediatype: Optional[Set[str]] = None
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.exclude_paths = exclude_paths or {'/health', '/metrics'}
        self.exclude_mediatype = exclude_mediatype or {'image/', 'video/', 'audio/'}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and compress response if applicable."""
        
        # Check if path should be excluded
        if request.url.path in self.exclude_paths:
            return await call_next(request)
            
        # Get accept-encoding header
        accept_encoding = request.headers.get('accept-encoding', '')
        
        # Process request
        response = await call_next(request)
        
        # Check if response should be compressed
        content_type = response.headers.get('content-type')
        content_length = response.headers.get('content-length')
        
        if content_type:
            # Check excluded media types
            for excluded in self.exclude_mediatype:
                if content_type.startswith(excluded):
                    return response
                    
        # Check if already compressed
        if response.headers.get('content-encoding'):
            return response
            
        # Determine if compression should be applied
        if not ResponseCompressor.should_compress(
            content_type,
            int(content_length) if content_length else None,
            accept_encoding
        ):
            return response
            
        # Get best encoding
        encoding = ResponseCompressor.get_best_encoding(accept_encoding)
        if not encoding:
            return response
            
        # For streaming responses, we need special handling
        if isinstance(response, StreamingResponse):
            return await self._compress_streaming_response(response, encoding)
            
        # Compress regular response
        return await self._compress_response(response, encoding)
        
    async def _compress_response(self, response: Response, encoding: str) -> Response:
        """Compress a regular response."""
        # Read response body
        body = b''
        async for chunk in response.body_iterator:
            body += chunk
            
        # Check minimum size
        if len(body) < self.minimum_size:
            return response
            
        # Compress body
        compressed_body = ResponseCompressor.compress_data(body, encoding)
        if not compressed_body:
            return response
            
        # Create new response with compressed body
        headers = MutableHeaders(response.headers)
        headers['content-encoding'] = encoding
        headers['content-length'] = str(len(compressed_body))
        headers.append('vary', 'accept-encoding')
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
        
    async def _compress_streaming_response(
        self,
        response: StreamingResponse,
        encoding: str
    ) -> StreamingResponse:
        """Compress a streaming response."""
        
        async def compressed_stream():
            """Generate compressed chunks."""
            if encoding == 'gzip':
                compressor = gzip.GzipFile(mode='wb', fileobj=None)
            elif encoding == 'zstd':
                compressor = zstd.ZstdCompressor(level=3).compressobj()
            else:
                # Fallback to uncompressed for unsupported streaming compression
                async for chunk in response.body_iterator:
                    yield chunk
                return
                
            try:
                async for chunk in response.body_iterator:
                    if encoding == 'gzip':
                        compressed = gzip.compress(chunk, compresslevel=6)
                    else:
                        compressed = compressor.compress(chunk)
                    if compressed:
                        yield compressed
                        
                # Flush remaining data
                if encoding == 'zstd':
                    final = compressor.flush()
                    if final:
                        yield final
            except Exception as e:
                logger.error(f"Streaming compression failed: {e}")
                # Fallback to uncompressed
                async for chunk in response.body_iterator:
                    yield chunk
                    
        # Update headers
        headers = MutableHeaders(response.headers)
        headers['content-encoding'] = encoding
        headers.append('vary', 'accept-encoding')
        if 'content-length' in headers:
            del headers['content-length']  # Remove as length changes
            
        return StreamingResponse(
            compressed_stream(),
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )


class CompressionConfig:
    """Configuration for compression settings."""
    
    def __init__(
        self,
        enabled: bool = True,
        minimum_size: int = 1000,
        compression_level: int = 6,
        algorithms: Optional[Set[str]] = None
    ):
        self.enabled = enabled
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.algorithms = algorithms or {'gzip', 'br', 'zstd', 'deflate'}
        
    def create_middleware(self, app) -> CompressionMiddleware:
        """Create compression middleware with this configuration."""
        if not self.enabled:
            # Return a no-op middleware
            class NoOpMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    return await call_next(request)
            return NoOpMiddleware(app)
            
        return CompressionMiddleware(
            app,
            minimum_size=self.minimum_size
        )