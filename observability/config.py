"""
Configuration module for observability components.
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ObservabilityConfig:
    """Configuration for observability components."""
    
    service_name: str = "python-otel-example"
    service_version: str = "0.1.0"
    environment: str = "development"
    otlp_endpoint: str = "http://localhost:4317"
    
    def to_resource_attributes(self) -> Dict[str, Any]:
        """Convert config to OpenTelemetry resource attributes."""
        return {
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.environment,
        }
