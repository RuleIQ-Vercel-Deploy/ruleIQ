"""
OpenTelemetry Distributed Tracing Configuration for ruleIQ

Provides comprehensive tracing for API calls, database operations, 
external service calls, and user interactions.
"""

import os
import logging
from typing import Dict, Any, Optional
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

logger = logging.getLogger(__name__)

class TracingConfig:
    """OpenTelemetry tracing configuration for ruleIQ"""

    def __init__(self):
        self.service_name = os.getenv("OTEL_SERVICE_NAME", "ruleiq-api")
        self.service_version = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT")
        self.tracing_enabled = os.getenv("TRACING_ENABLED", "true").lower() == "true"

    def setup_tracing(self) -> Optional[trace.Tracer]:
        """Initialize OpenTelemetry tracing"""
        if not self.tracing_enabled:
            logger.info("Tracing is disabled")
            return None

        try:
            # Create resource
            resource = Resource.create({
                SERVICE_NAME: self.service_name,
                SERVICE_VERSION: self.service_version,
                "environment": self.environment,
                "service.instance.id": f"{self.service_name}-{os.getpid()}",
            })

            # Set up tracer provider
            tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(tracer_provider)

            # Set up exporters
            self._setup_exporters(tracer_provider)

            # Set up propagators
            set_global_textmap(B3MultiFormat())

            # Instrument libraries
            self._instrument_libraries()

            logger.info(f"Tracing initialized for {self.service_name}")
            return trace.get_tracer(__name__)

        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            return None

    def _setup_exporters(self, tracer_provider: TracerProvider):
        """Set up trace exporters"""
        exporters = []

        # OTLP Exporter (for production)
        if self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            exporters.append(otlp_exporter)
            logger.info(f"OTLP exporter configured: {self.otlp_endpoint}")

        # Jaeger Exporter (for development)
        if self.jaeger_endpoint and self.environment == "development":
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
                collector_endpoint=self.jaeger_endpoint,
            )
            exporters.append(jaeger_exporter)
            logger.info(f"Jaeger exporter configured: {self.jaeger_endpoint}")

        # Add batch processors for each exporter
        for exporter in exporters:
            span_processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(span_processor)

    def _instrument_libraries(self):
        """Automatically instrument common libraries"""
        try:
            # FastAPI instrumentation
            FastAPIInstrumentor.instrument()

            # HTTP requests instrumentation
            RequestsInstrumentor().instrument()

            # SQLAlchemy instrumentation
            SQLAlchemyInstrumentor().instrument()

            # Redis instrumentation
            RedisInstrumentor().instrument()

            # Celery instrumentation
            CeleryInstrumentor().instrument()

            logger.info("Auto-instrumentation completed")

        except Exception as e:
            logger.error(f"Failed to instrument libraries: {e}")

class CustomTracer:
    """Custom tracer wrapper for ruleIQ-specific tracing"""

    def __init__(self, tracer: Optional[trace.Tracer]):
        self.tracer = tracer
        self.enabled = tracer is not None

    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL
    ):
        """Start a new span with custom attributes"""
        if not self.enabled:
            return trace.INVALID_SPAN

        span = self.tracer.start_span(name, kind=kind)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

        return span

    def trace_api_call(self, endpoint: str, method: str, user_id: Optional[str] = None):
        """Trace API endpoint calls"""
        attributes = {
            "http.method": method,
            "http.route": endpoint,
            "service.name": "ruleiq-api"
        }

        if user_id:
            attributes["user.id"] = user_id

        return self.start_span(
            f"{method} {endpoint}",
            attributes=attributes,
            kind=trace.SpanKind.SERVER
        )

    def trace_database_operation(self, operation: str, table: str, query_id: Optional[str] = None):
        """Trace database operations"""
        attributes = {
            "db.operation": operation,
            "db.table": table,
            "db.system": "postgresql"
        }

        if query_id:
            attributes["db.query.id"] = query_id

        return self.start_span(
            f"db.{operation}",
            attributes=attributes,
            kind=trace.SpanKind.CLIENT
        )

    def trace_external_call(self, service: str, endpoint: str, method: str = "GET"):
        """Trace external service calls"""
        attributes = {
            "http.method": method,
            "http.url": endpoint,
            "service.name": service
        }

        return self.start_span(
            f"external.{service}",
            attributes=attributes,
            kind=trace.SpanKind.CLIENT
        )

    def trace_ai_operation(self, operation: str, model: str, tokens: Optional[int] = None):
        """Trace AI service operations"""
        attributes = {
            "ai.operation": operation,
            "ai.model": model
        }

        if tokens:
            attributes["ai.tokens"] = tokens

        return self.start_span(
            f"ai.{operation}",
            attributes=attributes
        )

    def add_user_context(self, span, user_id: str, business_profile_id: Optional[str] = None):
        """Add user context to spans"""
        if not self.enabled:
            return

        span.set_attribute("user.id", user_id)
        if business_profile_id:
            span.set_attribute("business.profile.id", business_profile_id)

# Global tracer instance
_tracing_config = TracingConfig()
_base_tracer = _tracing_config.setup_tracing()
tracer = CustomTracer(_base_tracer)

# Convenience decorators
def trace_endpoint(endpoint: str, method: str = "GET"):
    """Decorator to trace FastAPI endpoints"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not tracer.enabled:
                return func(*args, **kwargs)

            with tracer.trace_api_call(endpoint, method):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def trace_db_operation(operation: str, table: str):
    """Decorator to trace database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not tracer.enabled:
                return func(*args, **kwargs)

            with tracer.trace_database_operation(operation, table):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def trace_external_service(service: str):
    """Decorator to trace external service calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not tracer.enabled:
                return func(*args, **kwargs)

            with tracer.trace_external_call(service, str(args[0]) if args else "unknown"):
                return func(*args, **kwargs)
        return wrapper
    return decorator
