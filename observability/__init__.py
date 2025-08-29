"""
Observability package for OpenTelemetry instrumentation.

This package provides structured observability signals including metrics and tracing.
"""

from .metrics import MetricsManager
from .tracing import TracingManager

__version__ = "0.1.0"
__all__ = ["MetricsManager", "TracingManager"]
