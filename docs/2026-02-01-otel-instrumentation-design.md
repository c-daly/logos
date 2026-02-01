# OpenTelemetry Instrumentation Design

**Date:** 2026-02-01
**Tracking:** logos#321, sub-tickets #334-344
**Goal:** Operational visibility across Sophia, Hermes, and Apollo via OpenTelemetry

---

## Current State

### What Exists

| Component | Status | Location |
|-----------|--------|----------|
| `logos_observability` module | Complete | `logos/logos_observability/` |
| `setup_telemetry()` | Working | TracerProvider + console/OTLP exporters |
| `setup_metrics()` | Working | MeterProvider + console/OTLP exporters |
| `get_tracer()`, `get_meter()`, `get_logger()` | Working | Thin wrappers over OTel SDK |
| OTel deps in foundry | Present but in **test** dep group | `logos/pyproject.toml` |
| `opentelemetry-instrumentation-httpx` | **Missing** | Not in pyproject.toml |
| Docker compose (Tempo + Grafana) | Exists | `logos/docker-compose.otel.yml` |
| OTel smoke tests | Exist | `logos/tests/integration/observability/test_otel_smoke.py` |
| OTel stack tests | Exist but **test wrong ports** | `logos/tests/infra/test_otel_stack.py` |

### What's Missing

- OTel deps not in production dependency group — services can't use them at runtime
- No `opentelemetry-instrumentation-httpx` for outbound HTTP trace propagation
- No OTel wiring in any service's FastAPI app (Sophia, Hermes, Apollo all lack it)
- No manual spans on key operations
- No integration test for cross-service trace propagation
- `test_otel_stack.py` tests Jaeger/Prometheus ports but compose deploys Tempo/Grafana

### Service Dependency Chain

All three services pin `logos-foundry` as a git dependency at `v0.2.0`:
```
logos-foundry @ git+https://github.com/c-daly/logos.git@v0.2.0
```

---

## Key Decisions

- **Centralized OTel deps**: All OpenTelemetry packages live in `logos-foundry`, not per-service
- **Always-on instrumentation, opt-in export**: Code is always instrumented; OTLP export enabled via `OTEL_EXPORTER_OTLP_ENDPOINT` env var
- **Auto + manual spans**: `FastAPIInstrumentor` for request-level spans, `HTTPXClientInstrumentor` for outbound HTTP, manual `get_tracer()` spans for key internal operations
- **Jaeger + Prometheus first**: Wire and verify against simple backends, then upgrade to Tempo + Grafana
- **Graceful degradation**: No collector = no export = zero service impact (BatchSpanProcessor drops silently)
- **Independent service PRs**: Each service's instrumentation is independent; one failing doesn't block others

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `None` (disabled) | OTel collector gRPC endpoint |
| `OTEL_EXPORT_CONSOLE` | `false` | Enable console span export (dev mode) |

## Data Flow

```
Sophia/Hermes/Apollo
  └─ logos_observability.setup_telemetry(service_name, otlp_endpoint)
       └─ TracerProvider + MeterProvider
            └─ OTLPSpanExporter → OTel Collector (:4317 gRPC)
                 ├─ Jaeger (:16686 UI) — traces    [Phases 0-2]
                 ├─ Prometheus (:9090) — metrics    [Phases 0-2]
                 ├─ Tempo (:3200 query) — traces    [Phase 3]
                 └─ Grafana (:3001 UI) — dashboards [Phase 3]
```

---

## Phase 0 — Foundry Update (logos repo, blocking prerequisite)

**Ticket coverage:** Prerequisite for #334, #337, #340

### Steps

1. **Move OTel deps from test to production group** in `logos/pyproject.toml`:
   - `opentelemetry-api = "^1.20.0"`
   - `opentelemetry-sdk = "^1.20.0"`
   - `opentelemetry-instrumentation-fastapi = "^0.41b0"`
   - `opentelemetry-exporter-otlp-proto-grpc = "^1.20.0"`

2. **Add missing dependency**:
   - `opentelemetry-instrumentation-httpx = "^0.41b0"`

3. **Create `docker-compose.otel.yml`** with Jaeger + Prometheus stack (replacing existing Tempo+Grafana content — that content is preserved in git and restored in Phase 3):
   ```yaml
   services:
     otel-collector:
       image: otel/opentelemetry-collector-contrib:0.91.0
       container_name: logos-otel-collector
       command: ["--config=/etc/otel-collector-config.yaml"]
       volumes:
         - ./infra/otel-collector-config.yaml:/etc/otel-collector-config.yaml:ro
       ports:
         - "4317:4317"   # OTLP gRPC
         - "4318:4318"   # OTLP HTTP
         - "8888:8888"   # Collector metrics
         - "13133:13133" # Health check
       networks:
         - logos-observability-net
       restart: unless-stopped

     jaeger:
       image: jaegertracing/all-in-one:1.53
       container_name: logos-jaeger
       environment:
         - COLLECTOR_OTLP_ENABLED=true
       ports:
         - "16686:16686" # Jaeger UI
         - "14268:14268" # Jaeger collector HTTP
       networks:
         - logos-observability-net
       restart: unless-stopped

     prometheus:
       image: prom/prometheus:v2.48.1
       container_name: logos-prometheus
       volumes:
         - ./infra/prometheus.yml:/etc/prometheus/prometheus.yml:ro
       ports:
         - "9090:9090"
       networks:
         - logos-observability-net
       restart: unless-stopped

   networks:
     logos-observability-net:
       driver: bridge
   ```

4. **Update `otel-collector-config.yaml`** to export traces to Jaeger and metrics to Prometheus.

5. **Update `test_otel_stack.py`** to match Jaeger+Prometheus ports (it currently tests the right ports but against the wrong compose).

6. **Run tests** — full suite including `test_otel_smoke.py` and `test_otel_stack.py`.

7. **Tag `v0.3.0`**, push tag.

### Verification
```bash
poetry run python -c "from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor"
docker compose -f docker-compose.otel.yml up -d
# Jaeger UI: http://localhost:16686
# Prometheus: http://localhost:9090
```

### Gate
Tag `v0.3.0` exists before Phase 1 begins.

---

## Phase 1 — Service Instrumentation + Smoke Tests (parallel: Sophia, Hermes, Apollo)

**Ticket coverage:** #334+#335+#336 (Sophia), #337+#338+#339 (Hermes), #340+#341+#342 (Apollo)

### Orchestration Protocol

1. Main agent creates `feature/otel-instrumentation` branch in all three repos
2. Main agent updates `pyproject.toml` in each repo to pin `logos-foundry@v0.3.0` and runs `poetry lock`
3. Main agent dispatches three subagents in parallel, one per repo
4. Each subagent is responsible for: wiring telemetry, adding manual spans, adding smoke tests
5. Each subagent creates a PR when done — PRs are independent, no cross-service blocking

### Per-Service Steps

#### Step 1: Wire telemetry on app startup

In the FastAPI lifespan or `create_app()`:

```python
import os
from logos_observability import setup_telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# In lifespan or create_app():
setup_telemetry(
    service_name="sophia",  # or "hermes" / "apollo"
    otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    export_to_console=os.getenv("OTEL_EXPORT_CONSOLE", "").lower() == "true",
)
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
```

#### Step 2: Add manual spans on key operations

Use inline context managers with `{service}.{operation}` naming:

```python
from logos_observability import get_tracer

tracer = get_tracer("sophia.planner")

async def create_plan(goal: str) -> Plan:
    with tracer.start_as_current_span("sophia.plan") as span:
        span.set_attribute("plan.goal", goal)
        result = await self._run_planning(goal)
        span.set_attribute("plan.step_count", len(result.steps))
        return result
```

**Suggested spans per service** (subagents should add these where they make sense — guidance, not a hard requirement):

**Sophia:**
- `sophia.plan` — planning pipeline (goal, step count)
- `sophia.simulate` — simulation runs (k-steps, confidence)
- `sophia.hcg.read` / `sophia.hcg.write` — HCG client operations
- `sophia.state.read` / `sophia.state.write` — CWM state operations

**Hermes:**
- `hermes.embed` — embedding generation (model, vector dimension)
- `hermes.llm` — LLM calls (provider, model, token counts)
- `hermes.nlp` — NLP pipeline operations
- `hermes.milvus` — Milvus insert/query operations

**Apollo:**
- `apollo.command` — CLI command dispatch (command type, success/failure)
- `apollo.api.sophia` — outbound calls to Sophia
- `apollo.api.hermes` — outbound calls to Hermes

#### Step 3: Add smoke tests

Pattern (uses `InMemorySpanExporter`, no collector required — runs in CI):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from logos_observability import setup_telemetry, get_tracer

class InMemorySpanExporter:
    def __init__(self):
        self.spans = []
    def export(self, spans):
        self.spans.extend(spans)
        return trace.SpanExportResult.SUCCESS
    def shutdown(self):
        pass

def test_service_creates_spans():
    setup_telemetry(service_name="sophia", export_to_console=False)
    exporter = InMemorySpanExporter()
    provider = trace.get_tracer_provider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    tracer = get_tracer("sophia.planner")
    with tracer.start_as_current_span("sophia.plan") as span:
        span.set_attribute("plan.goal", "test")

    provider.force_flush()

    assert len(exporter.spans) > 0
    assert exporter.spans[0].name == "sophia.plan"
    assert exporter.spans[0].resource.attributes["service.name"] == "sophia"
```

Verify existing test suite still passes with OTel instrumented (FastAPIInstrumentor compatibility).

#### Step 4: PR per service

- Branch: `feature/otel-instrumentation` (created by main agent)
- Run `ruff check`, `ruff format --check`, `mypy`, existing tests before pushing
- PR title: `feat(otel): instrument {service} with OpenTelemetry tracing`

---

## Phase 2 — Integration Verification (sequential, after all Phase 1 PRs merged)

**Ticket coverage:** #344

### Steps

1. Start Jaeger + Prometheus compose:
   ```bash
   docker compose -f docker-compose.otel.yml up -d
   ```

2. Start all three services with OTel export enabled:
   ```bash
   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 uvicorn sophia...
   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 uvicorn hermes...
   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 uvicorn apollo...
   ```

3. Make cross-service requests (Apollo -> Sophia -> Hermes).

4. Verify in Jaeger UI (`http://localhost:16686`):
   - All three service names appear in the service dropdown
   - End-to-end trace with parent-child span relationships across service boundaries
   - Manual span attributes visible (plan IDs, model names, etc.)
   - W3C trace context propagated correctly (single trace ID across services)

5. Verify Prometheus (`http://localhost:9090`):
   - Collector metrics being scraped
   - Service metrics visible

6. Run `test_otel_stack.py` against the live compose.

7. Document verification results and close remaining tickets.

---

## Phase 3 — Backend Upgrade to Tempo + Grafana (sequential)

### Steps

1. Update `docker-compose.otel.yml` to Tempo + Grafana stack (restore git-preserved content with corrected ports):
   - OTel Collector (:4317 gRPC, :4318 HTTP)
   - Tempo (:3200 query frontend)
   - Grafana (:3001 UI)

2. Update `otel-collector-config.yaml` to export to Tempo instead of Jaeger.

3. Update `test_otel_stack.py` for Tempo + Grafana ports and endpoints.

4. Verify traces visible in Grafana via Tempo datasource.

5. Repeat cross-service verification from Phase 2, now viewing traces in Grafana.

---

## Execution Summary

| Phase | Scope | Blocking? | PRs |
|-------|-------|-----------|-----|
| 0 | Foundry: deps + compose + tag | Yes — gate for Phase 1 | 1 |
| 1 | Service instrumentation + tests (parallel) | No cross-service blocking | 3 |
| 2 | Integration verification (sequential) | Requires all Phase 1 merged | 1 |
| 3 | Tempo + Grafana upgrade (sequential) | Requires Phase 2 complete | 1 |

**Total PRs:** 6

---

## Follow-Up Considerations

### `logos_config` Integration
Currently, `setup_telemetry()` takes `otlp_endpoint` as a parameter fed by `os.getenv()`. When formal environments are introduced, this should be routed through `logos_config` instead:

```python
from logos_config import get_config
setup_telemetry(
    service_name="sophia",
    otlp_endpoint=get_config().otel_endpoint,
)
```

This enables environment-specific config profiles without per-service code changes. The env var override (`OTEL_EXPORTER_OTLP_ENDPOINT`) continues to work via the OTel SDK natively.

### Environment Migration Path
The architecture is environment-agnostic by design:
- **Service code** never changes — it calls `setup_telemetry()` with a configured endpoint
- **OTel Collector** is the routing layer — different collector configs per environment (sampling rates, exporters, memory limits)
- **Infrastructure** (compose files, k8s manifests) defines what backends are deployed
- **Sampling**: Currently 100%. Production environments should configure `OTEL_TRACES_SAMPLER` env var (head-based or tail-based sampling). Zero code changes required.

### Apollo DiagnosticsManager
Apollo has a custom `DiagnosticsManager` with WebSocket telemetry streaming that is parallel to OTel. A future ticket could bridge these — e.g., feeding OTel metrics into the diagnostics WebSocket, or replacing the custom telemetry with OTel metrics.

### Talos Telemetry
Talos has its own `TelemetryRecorder` for hardware-level events (actuator positions, gripper state). This is not OTel-integrated. A future ticket could bridge Talos events into OTel spans if hardware observability is needed in the trace view.
