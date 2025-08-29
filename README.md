# OpenTelemetry Hands-On Workshop

This repository contains a comprehensive hands-on workshop for learning about observability using OpenTelemetry with Python. The setup demonstrates different metric types (Counter, Histogram, Gauge, UpDownCounter), distributed tracing, and follows Python best practices with a structured observability framework.

## Architecture

```
                                          -----> Jaeger (traces)
Python App + SDK ---> OpenTelemetry Collector ---|
                                          -----> Prometheus (metrics)
```

## Project Structure

```
O11y-hands-on/
├── observability/              # Observability framework package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration management
│   ├── metrics.py             # Metrics framework with all metric types
│   └── tracing.py             # Tracing framework
├── docs/                      # Documentation
│   └── metrics-guide.md       # Comprehensive metrics guide
├── app.py                     # Enhanced demo application
├── docker-compose.yml         # Docker services orchestration
├── otel-collector.yaml        # OpenTelemetry Collector config
├── prometheus.yaml            # Prometheus configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.8+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd O11y-hands-on
```

### 2. Start the Observability Stack

Launch the OpenTelemetry Collector, Prometheus, and Jaeger using Docker Compose:

```bash
docker compose up -d
```

This will start:
- **OpenTelemetry Collector** (ports 4317, 4318, 9090)
- **Prometheus** (port 9091)
- **Jaeger** (port 16686)

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Running the Enhanced Demo Application

The enhanced application demonstrates all four metric types with Python best practices:

### Run All Demos (Default)
```bash
python app.py
```

### Run Specific Metric Type Demos
```bash
# Counter metrics demo
python app.py --demo-type counter

# Histogram metrics demo
python app.py --demo-type histogram

# Gauge metrics demo
python app.py --demo-type gauge

# UpDownCounter metrics demo
python app.py --demo-type updown

# Comprehensive demo (web server + system metrics)
python app.py --demo-type comprehensive
```

### Customize Configuration
```bash
python app.py --service-name my-service --otlp-endpoint http://localhost:4317
```

## Understanding Metric Types

The application demonstrates four different metric types:

### 1. **Counter** - Monotonically Increasing Values
- **Use cases**: Request counts, error counts, events processed
- **Examples**: `demo_events_total`, `http_requests_total`
- **Characteristics**: Always increases, resets on restart

### 2. **Histogram** - Distribution of Values
- **Use cases**: Request duration, response sizes, processing time
- **Examples**: `demo_operation_duration_seconds`, `http_request_duration_seconds`
- **Characteristics**: Provides percentiles, buckets, count, and sum

### 3. **Gauge** - Current State Values
- **Use cases**: Memory usage, CPU utilization, temperature
- **Examples**: `demo_temperature_celsius`, `memory_usage_bytes`
- **Characteristics**: Can go up or down, represents current state

### 4. **UpDownCounter** - Values That Can Increase/Decrease
- **Use cases**: Active connections, queue size, resource pools
- **Examples**: `demo_resource_pool`, `active_connections`
- **Characteristics**: Tracks changes over time, cumulative

For detailed explanations and when to use each type, see [docs/metrics-guide.md](docs/metrics-guide.md).

## Viewing Telemetry Data

### Traces in Jaeger

Open the Jaeger UI: **http://localhost:16686**

1. Select service "python-otel-metrics-demo"
2. Click "Find Traces" to view generated traces
3. Explore spans, attributes, and trace hierarchy
4. Look for different demo spans: `counter_demo`, `histogram_demo`, etc.

### Metrics in Prometheus

Open the Prometheus UI: **http://localhost:9091**

1. Click "Graph" in the navigation
2. Try these example queries:

**Counter Metrics:**
```promql
# Rate of demo events
rate(pythonapp_demo_events_total[5m])

# HTTP request rate
rate(pythonapp_http_requests_total[5m])
```

**Histogram Metrics:**
```promql
# 95th percentile operation duration
histogram_quantile(0.95, rate(pythonapp_demo_operation_duration_seconds_bucket[5m]))

# Average request duration
rate(pythonapp_http_request_duration_seconds_sum[5m]) / rate(pythonapp_http_request_duration_seconds_count[5m])
```

**Gauge Metrics:**
```promql
# Current temperature
pythonapp_demo_temperature_celsius

# Memory usage
pythonapp_memory_usage_bytes
```

**UpDownCounter Metrics:**
```promql
# Current resource pool size
pythonapp_demo_resource_pool

# Active connections
pythonapp_active_connections
```

## Python Best Practices Demonstrated

This workshop showcases several Python best practices:

- **Structured Package Design**: Modular observability package
- **Type Hints**: Full type annotations throughout
- **Abstract Base Classes**: Extensible metric framework
- **Configuration Management**: Centralized config with dataclasses
- **Error Handling**: Proper exception handling and logging
- **Documentation**: Comprehensive docstrings and guides
- **CLI Interface**: Argparse for flexible demo execution

## Extending the Framework

### Adding Custom Metrics

```python
from observability import MetricsManager
from observability.config import ObservabilityConfig

# Initialize
config = ObservabilityConfig(service_name="my-service")
metrics_manager = MetricsManager(config)
metrics_manager.setup()

# Create custom metrics
my_counter = metrics_manager.create_counter(
    "my_custom_events_total",
    "Description of my events",
    "1"
)

# Record metrics
my_counter.record(1, {"event_type": "custom"})
```

### Adding Custom Traces

```python
from observability import TracingManager

tracing_manager = TracingManager(config)
tracing_manager.setup()

# Create spans
with tracing_manager.start_span("my_operation") as span:
    span.set_attribute("operation.type", "custom")
    # Your code here
```

## Shutting Down

To stop and remove all containers:

```bash
docker compose down
```

## Additional Resources

- **[Metrics Guide](docs/metrics-guide.md)** - Comprehensive guide to metric types
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [OpenTelemetry Collector Documentation](https://opentelemetry.io/docs/collector/)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)

## Workshop Exercises

1. **Explore Metric Types**: Run each demo type individually and observe the differences
2. **Custom Metrics**: Add your own metrics to the application
3. **Query Practice**: Practice writing PromQL queries for different metric types
4. **Trace Analysis**: Examine trace relationships and span attributes
5. **Performance Impact**: Compare overhead of different metric types
