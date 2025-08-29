"""
Tracing module for OpenTelemetry instrumentation.
"""

import logging
from typing import Optional
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import ObservabilityConfig

logger = logging.getLogger(__name__)


class TracingManager:
    """Manages OpenTelemetry tracing setup and operations."""
    
    def __init__(self, config: ObservabilityConfig):
        """Initialize the tracing manager with configuration."""
        self.config = config
        self._tracer_provider: Optional[TracerProvider] = None
        self._tracer: Optional[trace.Tracer] = None
    
    def setup(self) -> None:
        """Setup the tracer provider and configure tracing."""
        resource = Resource(attributes=self.config.to_resource_attributes())
        
        # Create a tracer provider
        self._tracer_provider = TracerProvider(resource=resource)
        
        # Create an OTLP exporter and add it to the tracer provider
        otlp_exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
        self._tracer_provider.add_span_processor(span_processor)
        
        # Set the tracer provider
        trace.set_tracer_provider(self._tracer_provider)
        
        # Get a tracer
        self._tracer = trace.get_tracer(__name__)
        
        logger.info("Tracing initialized successfully")
    
    def get_tracer(self) -> trace.Tracer:
        """Get the configured tracer."""
        if self._tracer is None:
            raise RuntimeError("Tracing not initialized. Call setup() first.")
        return self._tracer
    
    @contextmanager
    def start_span(self, name: str, **kwargs):
        """Context manager for creating spans."""
        tracer = self.get_tracer()
        with tracer.start_as_current_span(name, **kwargs) as span:
            yield span
    
    def shutdown(self) -> None:
        """Shutdown the tracer provider."""
        if self._tracer_provider:
            self._tracer_provider.shutdown()
            logger.info("Tracing shutdown completed")
