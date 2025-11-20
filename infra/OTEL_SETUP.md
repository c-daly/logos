# OpenTelemetry Observability Stack

This document describes the observability infrastructure for LOGOS Phase 2, including distributed tracing, metrics collection, and visualization dashboards.

## Overview

The LOGOS observability stack consists of:
- **OpenTelemetry Collector**: Receives traces/metrics from services
- **Grafana Tempo**: Distributed tracing backend storage
- **Grafana**: Visualization and dashboards

## Quick Start

### 1. Start the Observability Stack

```bash
# Start OTel collector, Tempo, and Grafana
cd infra
docker-compose -f docker-compose.otel.yml up -d
```

### 2. Verify Services

```bash
# Check health
curl http://localhost:13133/  # OTel Collector health
curl http://localhost:3200/ready  # Tempo health
curl http://localhost:3001/api/health  # Grafana health
```

### 3. Access Grafana

Open your browser to: http://localhost:3001

- **Username**: admin (or anonymous access is enabled)
- **Password**: admin
- **Default Dashboard**: Navigate to "LOGOS" folder → "LOGOS Key Signals"

## Architecture

```
LOGOS Services (Sophia/Hermes/Apollo)
    │
    │ OTLP gRPC (port 4317)
    │ or HTTP (port 4318)
    ↓
OpenTelemetry Collector
    │
    │ Processes and forwards
    ↓
Grafana Tempo (Traces Storage)
    │
    │ Query API (port 3200)
    ↓
Grafana (Visualization)
    │
    │ HTTP (port 3001)
    ↓
User Browser
```

## Instrumentation

### Python Services (Sophia, Hermes)

```python
from logos_observability import setup_telemetry, get_tracer, get_logger

# Initialize telemetry
setup_telemetry(
    service_name="sophia",
    export_to_console=False,  # Disable in production
    otlp_endpoint="http://localhost:4317"
)

# Get tracer and logger
tracer = get_tracer(__name__)
logger = get_logger(__name__)

# Instrument your code
with tracer.start_as_current_span("process_plan") as span:
    span.set_attribute("plan_id", plan_id)
    span.set_attribute("user_id", user_id)
    
    # Your code here
    result = process_plan(plan_id)
    
    # Log structured events
    logger.log_plan_update(
        plan_uuid=plan_id,
        action="completed",
        details={"duration_ms": 125.5}
    )
```

### Linking Traces to Plan IDs

The Sophia `/simulate` endpoint automatically links traces to plan IDs:

```python
@router.post("/simulate")
def simulate(request: SimulationRequest):
    with tracer.start_as_current_span("simulate") as span:
        result = simulation_service.run_simulation(request)
        
        # Link trace to plan ID for correlation
        span.set_attribute("plan_id", result.process.uuid)
        span.set_attribute("capability_id", request.capability_id)
        
        return result
```

In Grafana, you can query traces by plan ID:
```
{ span.plan_id = "plan-abc-123" }
```

## Key Signals Dashboard

The pre-configured dashboard includes panels for:

1. **Sophia Service Traces**: All traces from the Sophia cognitive core
2. **/simulate Endpoint Traces**: Imagination/simulation requests
3. **Plan Execution Traces**: Traces linked to specific plan IDs
4. **Hermes Service Traces**: Embedding and NLP service traces

### Custom Queries

TraceQL examples for common queries:

```traceql
# All traces from Sophia service
{ resource.service.name="sophia" }

# Traces for a specific plan
{ span.plan_id="plan-123" }

# Failed simulations
{ span.name="/simulate" && status=error }

# Slow operations (>1s duration)
{ duration > 1s }

# Embedding operations
{ resource.service.name="hermes" && span.name="embed_text" }
```

## Configuration

### Environment Variables

Set these in your service configurations:

```bash
# Enable OTel export
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Service identification
OTEL_SERVICE_NAME=sophia  # or hermes, apollo, etc.

# Development mode
OTEL_CONSOLE_EXPORT=false  # Set to true for local debugging
```

### Docker Compose Integration

To integrate with existing services, add to your compose file:

```yaml
services:
  sophia:
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_SERVICE_NAME=sophia
    networks:
      - logos-observability-net

networks:
  logos-observability-net:
    external: true  # Created by docker-compose.otel.yml
```

## Metrics (Future Enhancement)

The collector is configured to support metrics export to Prometheus. To enable:

1. Uncomment the `prometheus` exporter in `otel-collector-config.yaml`
2. Add Prometheus service to `docker-compose.otel.yml`
3. Configure Grafana datasource for Prometheus
4. Create metric dashboards for:
   - Request rates (`/plan`, `/simulate`, `/embed_text`)
   - Error rates
   - Latency percentiles (p50, p95, p99)
   - Embedding throughput

## Troubleshooting

### No traces appearing in Grafana

1. Check if OTel collector is receiving traces:
   ```bash
   docker logs logos-otel-collector
   ```

2. Verify services are exporting to correct endpoint:
   ```bash
   # Should see spans being exported
   docker logs sophia-api  # or your service container
   ```

3. Check Tempo is receiving traces:
   ```bash
   curl http://localhost:3200/api/search
   ```

### Collector memory issues

If the collector runs out of memory, adjust limits in `otel-collector-config.yaml`:

```yaml
processors:
  memory_limiter:
    limit_mib: 1024  # Increase from 512
    spike_limit_mib: 256
```

### Grafana datasource issues

1. Verify Tempo connection in Grafana:
   - Settings → Data Sources → Tempo
   - Click "Test" button
   - Should show "Data source is working"

2. Check network connectivity:
   ```bash
   docker exec logos-grafana ping tempo
   ```

## CI/CD Integration

### Smoke Test

The CI pipeline includes a smoke test to verify OTel exporters don't break services:

```bash
# Run in CI
pytest tests/phase2/test_otel_smoke.py -v
```

This test:
1. Starts a service with OTel enabled
2. Makes a request and generates a trace
3. Verifies the service still functions correctly
4. Does NOT require collector/Tempo running (uses in-memory export)

### Production Deployment

For production deployments:

1. Use persistent storage for Tempo (not local filesystem)
2. Configure authentication for Grafana
3. Set retention policies for traces
4. Use external Prometheus for metrics
5. Configure alerting rules

## Demo Capture

To capture observability data for verification:

```bash
# Start all services including observability stack
docker-compose -f docker-compose.hcg.dev.yml up -d
docker-compose -f docker-compose.otel.yml up -d

# Run demo capture
cd scripts/demo_capture
python capture_demo.py --mode all --duration 120

# Access Grafana dashboard
# Take screenshots of key signals
# Export trace data for verification artifacts
```

The demo capture script will:
- Aggregate telemetry logs from `/tmp/logos_telemetry`
- Include Grafana dashboard screenshots
- Export sample traces for verification

## References

- Phase 2 Spec: `docs/phase2/PHASE2_SPEC.md` (Diagnostics section)
- OpenTelemetry Docs: https://opentelemetry.io/docs/
- Grafana Tempo: https://grafana.com/docs/tempo/
- TraceQL Guide: https://grafana.com/docs/tempo/latest/traceql/

## See Also

- `logos_observability/README.md` - Python instrumentation library
- `tests/phase2/test_observability.py` - Unit tests
- `docs/phase2/VERIFY.md` - P2-M4 acceptance criteria
