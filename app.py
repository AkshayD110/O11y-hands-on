#!/usr/bin/env python3
"""
Enhanced OpenTelemetry example demonstrating different metric types.

This application showcases Counter, Histogram, Gauge, and UpDownCounter metrics
using a structured observability framework with Python best practices.
"""
import logging
import argparse
import random
import threading
import time
from typing import Optional

from observability import MetricsManager, TracingManager
from observability.config import ObservabilityConfig
from observability.metrics import MetricsExamples

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ObservabilityDemo:
    """Main demo class showcasing different observability patterns."""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.metrics_manager: Optional[MetricsManager] = None
        self.tracing_manager: Optional[TracingManager] = None
        self.metrics_examples: Optional[MetricsExamples] = None
        self._shutdown_event = threading.Event()
    
    def setup(self) -> None:
        """Initialize observability components."""
        logger.info("Setting up observability components...")
        
        # Initialize metrics
        self.metrics_manager = MetricsManager(self.config)
        self.metrics_manager.setup()
        
        # Initialize tracing
        self.tracing_manager = TracingManager(self.config)
        self.tracing_manager.setup()
        
        # Initialize examples
        self.metrics_examples = MetricsExamples(self.metrics_manager)
        
        logger.info("Observability setup completed")
    
    def run_counter_demo(self) -> None:
        """Demonstrate Counter metrics."""
        logger.info("=== Counter Metrics Demo ===")
        
        with self.tracing_manager.start_span("counter_demo") as span:
            # Create a counter for demo purposes
            demo_counter = self.metrics_manager.create_counter(
                "demo_events_total",
                "Total number of demo events",
                "1"
            )
            
            # Simulate events
            events = ["user_login", "user_logout", "page_view", "api_call"]
            
            for i in range(20):
                event_type = events[i % len(events)]
                demo_counter.record(1, {"event_type": event_type})
                logger.info(f"Recorded counter event: {event_type}")
                time.sleep(0.5)
            
            span.set_attribute("events_generated", 20)
    
    def run_histogram_demo(self) -> None:
        """Demonstrate Histogram metrics."""
        logger.info("=== Histogram Metrics Demo ===")
        
        with self.tracing_manager.start_span("histogram_demo") as span:
            # Create a histogram for demo purposes
            demo_histogram = self.metrics_manager.create_histogram(
                "demo_operation_duration_seconds",
                "Duration of demo operations",
                "s"
            )
            
            # Simulate operations with varying durations
            operations = ["database_query", "api_call", "file_processing", "calculation"]
            
            for i in range(15):
                operation = operations[i % len(operations)]
                
                # Simulate different duration patterns for different operations
                if operation == "database_query":
                    duration = max(0.01, abs(random.normalvariate(0.1, 0.05)))
                elif operation == "api_call":
                    duration = max(0.01, abs(random.normalvariate(0.2, 0.1)))
                elif operation == "file_processing":
                    duration = max(0.01, abs(random.normalvariate(0.5, 0.2)))
                else:  # calculation
                    duration = max(0.01, abs(random.normalvariate(0.05, 0.02)))
                
                demo_histogram.record(duration, {"operation": operation})
                logger.info(f"Recorded histogram: {operation} took {duration:.3f}s")
                time.sleep(0.3)
            
            span.set_attribute("operations_completed", 15)
    
    def run_gauge_demo(self) -> None:
        """Demonstrate Gauge metrics."""
        logger.info("=== Gauge Metrics Demo ===")
        
        with self.tracing_manager.start_span("gauge_demo") as span:
            # Create gauges for demo purposes
            temperature_gauge = self.metrics_manager.create_gauge(
                "demo_temperature_celsius",
                "Current temperature",
                "°C"
            )
            
            pressure_gauge = self.metrics_manager.create_gauge(
                "demo_pressure_hpa",
                "Current atmospheric pressure",
                "hPa"
            )
            
            # Simulate changing environmental conditions
            import random
            base_temp = 20.0
            base_pressure = 1013.25
            
            for i in range(10):
                # Simulate temperature fluctuation
                temp_change = random.uniform(-2, 2)
                base_temp += temp_change
                temperature_gauge.record(base_temp, {"location": "sensor_1"})
                
                # Simulate pressure fluctuation
                pressure_change = random.uniform(-5, 5)
                base_pressure += pressure_change
                pressure_gauge.record(base_pressure, {"location": "sensor_1"})
                
                logger.info(f"Updated gauges: temp={base_temp:.1f}°C, pressure={base_pressure:.1f}hPa")
                time.sleep(1)
            
            span.set_attribute("gauge_updates", 10)
    
    def run_updown_counter_demo(self) -> None:
        """Demonstrate UpDownCounter metrics."""
        logger.info("=== UpDownCounter Metrics Demo ===")
        
        with self.tracing_manager.start_span("updown_counter_demo") as span:
            # Create an up-down counter for demo purposes
            demo_updown = self.metrics_manager.create_up_down_counter(
                "demo_resource_pool",
                "Available resources in pool",
                "1"
            )
            
            # Simulate resource allocation and deallocation
            import random
            
            for i in range(15):
                # Randomly allocate or deallocate resources
                if random.random() > 0.4:  # 60% chance to allocate
                    change = random.randint(1, 5)
                    action = "allocated"
                else:  # 40% chance to deallocate
                    change = -random.randint(1, 3)
                    action = "deallocated"
                
                demo_updown.record(change, {"resource_type": "compute_units"})
                logger.info(f"Resource change: {action} {abs(change)} units")
                time.sleep(0.4)
            
            span.set_attribute("resource_operations", 15)
    
    def run_comprehensive_demo(self) -> None:
        """Run a comprehensive demo showing all metric types together."""
        logger.info("=== Comprehensive Metrics Demo ===")
        
        with self.tracing_manager.start_span("comprehensive_demo") as span:
            # Run web server simulation in a separate thread
            web_server_thread = threading.Thread(
                target=self.metrics_examples.simulate_web_server_metrics,
                args=(20,)
            )
            web_server_thread.start()
            
            # Run system metrics simulation
            self.metrics_examples.simulate_system_metrics(duration_seconds=25)
            
            # Wait for web server simulation to complete
            web_server_thread.join()
            
            span.set_attribute("demo_type", "comprehensive")
    
    def run_demo(self, demo_type: str = "all") -> None:
        """Run the specified demo type."""
        try:
            if demo_type == "counter" or demo_type == "all":
                self.run_counter_demo()
                time.sleep(2)
            
            if demo_type == "histogram" or demo_type == "all":
                self.run_histogram_demo()
                time.sleep(2)
            
            if demo_type == "gauge" or demo_type == "all":
                self.run_gauge_demo()
                time.sleep(2)
            
            if demo_type == "updown" or demo_type == "all":
                self.run_updown_counter_demo()
                time.sleep(2)
            
            if demo_type == "comprehensive" or demo_type == "all":
                self.run_comprehensive_demo()
            
            logger.info("Demo completed successfully")
            
        except KeyboardInterrupt:
            logger.info("Demo interrupted by user")
        except Exception as e:
            logger.exception(f"Error during demo: {e}")
    
    def shutdown(self) -> None:
        """Shutdown observability components."""
        logger.info("Shutting down observability components...")
        
        if self.metrics_manager:
            self.metrics_manager.shutdown()
        
        if self.tracing_manager:
            self.tracing_manager.shutdown()
        
        logger.info("Shutdown completed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="OpenTelemetry Metrics Demo")
    parser.add_argument(
        "--demo-type",
        choices=["counter", "histogram", "gauge", "updown", "comprehensive", "all"],
        default="all",
        help="Type of demo to run"
    )
    parser.add_argument(
        "--service-name",
        default="python-otel-metrics-demo",
        help="Service name for telemetry"
    )
    parser.add_argument(
        "--otlp-endpoint",
        default="http://localhost:4317",
        help="OTLP endpoint URL"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = ObservabilityConfig(
        service_name=args.service_name,
        otlp_endpoint=args.otlp_endpoint
    )
    
    # Create and run demo
    demo = ObservabilityDemo(config)
    
    try:
        demo.setup()
        demo.run_demo(args.demo_type)
    finally:
        demo.shutdown()


if __name__ == "__main__":
    main()
