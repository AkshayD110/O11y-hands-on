"""
Metrics module for OpenTelemetry instrumentation.

This module provides a comprehensive metrics framework demonstrating different
metric types: Counter, Histogram, Gauge, and UpDownCounter.
"""

import logging
import time
from typing import Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from enum import Enum

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from .config import ObservabilityConfig

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enumeration of different metric types."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    UP_DOWN_COUNTER = "up_down_counter"


class BaseMetric(ABC):
    """Base class for all metric types."""
    
    def __init__(self, name: str, description: str, unit: str = "1"):
        self.name = name
        self.description = description
        self.unit = unit
        self._instrument = None
    
    @abstractmethod
    def create_instrument(self, meter: metrics.Meter):
        """Create the OpenTelemetry instrument."""
        pass
    
    @abstractmethod
    def record(self, value: Union[int, float], attributes: Optional[Dict[str, Any]] = None):
        """Record a value for this metric."""
        pass


class CounterMetric(BaseMetric):
    """
    Counter metric - monotonically increasing value.
    
    Use cases:
    - Request counts
    - Error counts
    - Task completion counts
    - Events processed
    """
    
    def create_instrument(self, meter: metrics.Meter):
        """Create a counter instrument."""
        self._instrument = meter.create_counter(
            name=self.name,
            description=self.description,
            unit=self.unit
        )
        logger.debug(f"Created counter metric: {self.name}")
    
    def record(self, value: Union[int, float], attributes: Optional[Dict[str, Any]] = None):
        """Add to the counter value."""
        if self._instrument is None:
            raise RuntimeError(f"Instrument not created for metric {self.name}")
        
        if value < 0:
            raise ValueError("Counter values must be non-negative")
        
        self._instrument.add(value, attributes=attributes or {})


class HistogramMetric(BaseMetric):
    """
    Histogram metric - distribution of values.
    
    Use cases:
    - Request duration
    - Response size
    - Queue depth
    - Processing time
    """
    
    def create_instrument(self, meter: metrics.Meter):
        """Create a histogram instrument."""
        self._instrument = meter.create_histogram(
            name=self.name,
            description=self.description,
            unit=self.unit
        )
        logger.debug(f"Created histogram metric: {self.name}")
    
    def record(self, value: Union[int, float], attributes: Optional[Dict[str, Any]] = None):
        """Record a value in the histogram."""
        if self._instrument is None:
            raise RuntimeError(f"Instrument not created for metric {self.name}")
        
        self._instrument.record(value, attributes=attributes or {})


class GaugeMetric(BaseMetric):
    """
    Gauge metric - current value that can go up or down.
    
    Use cases:
    - Memory usage
    - CPU utilization
    - Temperature
    - Active connections
    - Queue size
    """
    
    def __init__(self, name: str, description: str, unit: str = "1"):
        super().__init__(name, description, unit)
        self._current_value = 0.0
    
    def create_instrument(self, meter: metrics.Meter):
        """Create a gauge instrument using observable gauge."""
        def get_current_value(options):
            return [metrics.Observation(self._current_value)]
        
        self._instrument = meter.create_observable_gauge(
            name=self.name,
            description=self.description,
            unit=self.unit,
            callbacks=[get_current_value]
        )
        logger.debug(f"Created gauge metric: {self.name}")
    
    def record(self, value: Union[int, float], attributes: Optional[Dict[str, Any]] = None):
        """Set the gauge value."""
        self._current_value = float(value)
    
    def get_value(self) -> float:
        """Get the current gauge value."""
        return self._current_value


class UpDownCounterMetric(BaseMetric):
    """
    UpDownCounter metric - value that can increase or decrease.
    
    Use cases:
    - Active sessions
    - Items in queue
    - Connection pool size
    - Cache size
    """
    
    def create_instrument(self, meter: metrics.Meter):
        """Create an up-down counter instrument."""
        self._instrument = meter.create_up_down_counter(
            name=self.name,
            description=self.description,
            unit=self.unit
        )
        logger.debug(f"Created up-down counter metric: {self.name}")
    
    def record(self, value: Union[int, float], attributes: Optional[Dict[str, Any]] = None):
        """Add to the up-down counter (can be negative)."""
        if self._instrument is None:
            raise RuntimeError(f"Instrument not created for metric {self.name}")
        
        self._instrument.add(value, attributes=attributes or {})


class MetricsManager:
    """Manages OpenTelemetry metrics setup and operations."""
    
    def __init__(self, config: ObservabilityConfig):
        """Initialize the metrics manager with configuration."""
        self.config = config
        self._meter_provider: Optional[MeterProvider] = None
        self._meter: Optional[metrics.Meter] = None
        self._metrics: Dict[str, BaseMetric] = {}
    
    def setup(self) -> None:
        """Setup the meter provider and configure metrics."""
        resource = Resource(attributes=self.config.to_resource_attributes())
        
        # Create a meter provider
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=self.config.otlp_endpoint),
            export_interval_millis=5000  # Export every 5 seconds
        )
        self._meter_provider = MeterProvider(
            resource=resource, 
            metric_readers=[metric_reader]
        )
        
        # Set the meter provider
        metrics.set_meter_provider(self._meter_provider)
        
        # Get a meter
        self._meter = metrics.get_meter(__name__)
        
        logger.info("Metrics initialized successfully")
    
    def get_meter(self) -> metrics.Meter:
        """Get the configured meter."""
        if self._meter is None:
            raise RuntimeError("Metrics not initialized. Call setup() first.")
        return self._meter
    
    def create_counter(self, name: str, description: str, unit: str = "1") -> CounterMetric:
        """Create and register a counter metric."""
        metric = CounterMetric(name, description, unit)
        metric.create_instrument(self.get_meter())
        self._metrics[name] = metric
        return metric
    
    def create_histogram(self, name: str, description: str, unit: str = "1") -> HistogramMetric:
        """Create and register a histogram metric."""
        metric = HistogramMetric(name, description, unit)
        metric.create_instrument(self.get_meter())
        self._metrics[name] = metric
        return metric
    
    def create_gauge(self, name: str, description: str, unit: str = "1") -> GaugeMetric:
        """Create and register a gauge metric."""
        metric = GaugeMetric(name, description, unit)
        metric.create_instrument(self.get_meter())
        self._metrics[name] = metric
        return metric
    
    def create_up_down_counter(self, name: str, description: str, unit: str = "1") -> UpDownCounterMetric:
        """Create and register an up-down counter metric."""
        metric = UpDownCounterMetric(name, description, unit)
        metric.create_instrument(self.get_meter())
        self._metrics[name] = metric
        return metric
    
    def get_metric(self, name: str) -> Optional[BaseMetric]:
        """Get a registered metric by name."""
        return self._metrics.get(name)
    
    def list_metrics(self) -> Dict[str, BaseMetric]:
        """Get all registered metrics."""
        return self._metrics.copy()
    
    def shutdown(self) -> None:
        """Shutdown the meter provider."""
        if self._meter_provider:
            self._meter_provider.shutdown()
            logger.info("Metrics shutdown completed")


class MetricsExamples:
    """Examples demonstrating different metric types in real-world scenarios."""
    
    def __init__(self, metrics_manager: MetricsManager):
        self.metrics_manager = metrics_manager
        self._setup_example_metrics()
    
    def _setup_example_metrics(self):
        """Setup example metrics for demonstration."""
        # Counter examples
        self.request_counter = self.metrics_manager.create_counter(
            "http_requests_total",
            "Total number of HTTP requests",
            "1"
        )
        
        self.error_counter = self.metrics_manager.create_counter(
            "errors_total",
            "Total number of errors",
            "1"
        )
        
        # Histogram examples
        self.request_duration = self.metrics_manager.create_histogram(
            "http_request_duration_seconds",
            "Duration of HTTP requests",
            "s"
        )
        
        self.task_processing_time = self.metrics_manager.create_histogram(
            "task_processing_duration_seconds",
            "Time taken to process tasks",
            "s"
        )
        
        # Gauge examples
        self.memory_usage = self.metrics_manager.create_gauge(
            "memory_usage_bytes",
            "Current memory usage",
            "By"
        )
        
        self.cpu_usage = self.metrics_manager.create_gauge(
            "cpu_usage_percent",
            "Current CPU usage percentage",
            "%"
        )
        
        # UpDownCounter examples
        self.active_connections = self.metrics_manager.create_up_down_counter(
            "active_connections",
            "Number of active connections",
            "1"
        )
        
        self.queue_size = self.metrics_manager.create_up_down_counter(
            "queue_size",
            "Number of items in processing queue",
            "1"
        )
    
    def simulate_web_server_metrics(self, num_requests: int = 10):
        """Simulate web server metrics."""
        logger.info(f"Simulating {num_requests} web server requests")
        
        for i in range(num_requests):
            # Simulate request processing
            start_time = time.time()
            
            # Simulate processing time (0.1 to 2.0 seconds)
            import random
            processing_time = random.uniform(0.1, 2.0)
            time.sleep(processing_time)
            
            # Record metrics
            attributes = {
                "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                "status": random.choice(["200", "404", "500"]),
                "endpoint": random.choice(["/api/users", "/api/orders", "/api/products"])
            }
            
            # Counter: increment request count
            self.request_counter.record(1, attributes)
            
            # Histogram: record request duration
            self.request_duration.record(processing_time, attributes)
            
            # Simulate errors (10% chance)
            if random.random() < 0.1:
                error_attributes = {"error_type": "timeout", "service": "database"}
                self.error_counter.record(1, error_attributes)
            
            logger.info(f"Processed request {i+1}/{num_requests} in {processing_time:.2f}s")
    
    def simulate_system_metrics(self, duration_seconds: int = 30):
        """Simulate system resource metrics."""
        logger.info(f"Simulating system metrics for {duration_seconds} seconds")
        
        import random
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # Simulate changing system metrics
            
            # Gauge: memory usage (simulate between 1GB and 4GB)
            memory_bytes = random.uniform(1_000_000_000, 4_000_000_000)
            self.memory_usage.record(memory_bytes)
            
            # Gauge: CPU usage (simulate between 10% and 90%)
            cpu_percent = random.uniform(10, 90)
            self.cpu_usage.record(cpu_percent)
            
            # UpDownCounter: simulate connections coming and going
            connection_change = random.choice([-2, -1, 0, 1, 2, 3])
            self.active_connections.record(connection_change)
            
            # UpDownCounter: simulate queue size changes
            queue_change = random.choice([-3, -2, -1, 0, 1, 2, 3, 4])
            self.queue_size.record(queue_change)
            
            time.sleep(2)  # Update every 2 seconds
            
        logger.info("System metrics simulation completed")
