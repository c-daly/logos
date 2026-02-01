# OpenTelemetry Instrumentation Design

**Date:** 2026-02-01
**Tracking:** logos#321, sub-tickets #334-344
**Goal:** Operational visibility across Sophia, Hermes, and Apollo via OpenTelemetry

---

## Overview

Instrument all three LOGOS services with OpenTelemetry tracing and metrics using the existing `logos_observability` library (bundled in `logos-foundry`). Enable end-to-end distributed tracing across service boundaries with W3C trace context propagation. Export to OTel Collector → Jaeger (traces) + Prometheus (metrics).

## Data Flow

```
Sophia/Hermes/Apollo
  └─ logos_observability.setup_telemetry(service_name, otlp_endpoint)
       └─ TracerProvider + MeterProvider
            └─ OTLPSpanExporter → OTel Collector (:4319 gRPC)
                 ├─ Jaeger (:16686 UI) — traces
                 └─ Prometheus (:9090) — metrics
```

## Key Decisions

- **Centralized OTel deps**: All OpenTelemetry packages live in `logos-foundry`, not per-service
- **Always-on instrumentation, opt-in export**: Code is always instrumented; OTLP export enabled via `OTEL_EXPORTER_OTLP_ENDPOINT` env var
- **Auto + manual spans**: `FastAPIInstrumentor` for request-level spans, manual `get_tracer()` spans for key internal operations
- **No Grafana dashboards initially**: Jaeger UI + Prometheus sufficient for operational visibility
- **Graceful degradation**: No collector → no export → zero service impact (BatchSpanProcessor drops silently)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `None` (disabled) | OTel collector gRPC endpoint |
| `OTEL_EXPORT_CONSOLE` | `false` | Enable console span export (dev mode) |

---

## Phase 0 — Foundry Update (logos repo, prerequisite)

**Ticket coverage:** Prerequisite for #334, #337, #340

1. Add `opentelemetry-instrumentation-httpx = "^0.41b0"` to `logos/pyproject.toml`
2. Add `opentelemetry-instrumentation-fastapi` if not already present (verify)
3. Run tests, tag `v0.3.0`
4. Verify: `poetry run python -c "from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor"`

**Output:** logos-foundry v0.3.0 tagged with all OTel instrumentation deps

---

## Phase 1 — Service Instrumentation (parallel: Sophia, Hermes, Apollo)

**Ticket coverage:** #334+#335 (Sophia), #337+#338 (Hermes), #340+#341 (Apollo)

Each agent performs the same pattern in its repo:

### Step 1: Update foundry dep
- Update `pyproject.toml` to pin `logos-foundry` v0.3.0
- `poetry lock && poetry install`
- Verify: `poetry run python -c "from logos_observability import setup_telemetry, get_tracer"`

### Step 2: Wire telemetry on app startup
In the FastAPI app factory (`create_app()` or equivalent):

```python
import os
from logos_observability import setup_telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# In create_app():
setup_telemetry(
    service_name="sophia",  # or "hermes" / "apollo"
    otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    export_to_console=os.getenv("OTEL_EXPORT_CONSOLE", "").lower() == "true",
)
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
```

### Step 3: Add manual spans on key operations

**Sophia** (key spans):
- `sophia.plan` — planning pipeline (goal, step count, duration)
- `sophia.simulate` — simulation runs (k-steps, confidence)
- `sophia.hcg.read` / `sophia.hcg.write` — HCG client operations
- `sophia.state.read` / `sophia.state.write` — CWM state operations
- Link trace IDs to plan IDs in Neo4j node properties

**Hermes** (key spans):
- `hermes.embed` — embedding generation (model, vector dimension, duration)
- `hermes.llm` — LLM calls (provider, model, token counts, latency)
- `hermes.nlp` — NLP pipeline operations
- `hermes.milvus` — Milvus insert/query operations

**Apollo** (key spans):
- `apollo.command` — CLI command dispatch (command type, duration, success/failure)
- `apollo.api.sophia` — outbound calls to Sophia
- `apollo.api.hermes` — outbound calls to Hermes

### Step 4: PR per service
- Branch: `feature/otel-instrumentation` per repo
- Run `ruff check`, `black --check`, `mypy`, existing tests before pushing

---

## Phase 2 — Testing & Documentation (parallel: Sophia, Hermes, Apollo)

**Ticket coverage:** #336 (Sophia), #339 (Hermes), #342 (Apollo)

### Per service:

1. **Smoke test** using in-memory span exporter:
   - Verify spans created for key operations
   - Verify correct `service.name` attribute
   - Verify key span attributes present (e.g., `plan.id`, `model.name`)
   - Pattern: use `InMemorySpanExporter` (see `logos/tests/integration/observability/test_otel_smoke.py`)

2. **Verify no test regression**:
   - Run full test suite with OTel instrumented
   - Ensure `FastAPIInstrumentor` doesn't interfere with test clients

3. **Documentation**:
   - Add OTel section to service README or `docs/operations/`:
     - Environment variables for configuration
     - How to enable/disable export
     - How to view traces in Jaeger

---

## Phase 3 — Infra Verification (logos repo, sequential)

**Ticket coverage:** #344 (partial — Jaeger + Prometheus only, no Grafana)

1. Verify `docker-compose.otel.yml` stack starts cleanly (collector + Jaeger + Prometheus)
2. Start all three services with `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4319`
3. Make cross-service requests (Apollo → Sophia → Hermes)
4. Confirm in Jaeger UI:
   - End-to-end trace with correct service names
   - Parent-child span relationships across service boundaries
   - Manual span attributes visible (plan IDs, model names, etc.)
5. Confirm Prometheus scraping metrics from collector
6. Update `docs/operations/PHASE2_VERIFY.md` with OTel verification steps
7. Close remaining tickets

---

## Execution Strategy

- Phases 0 must complete before Phase 1 (foundry dep)
- Phase 1 runs in parallel across all three repos (independent agents)
- Phase 2 runs in parallel across all three repos (independent agents)
- Phase 3 is sequential, after Phase 1+2 are merged
- Total PRs: 1 (foundry) + 3 (instrumentation) + 3 (testing) + 1 (verification) = 8

## Dependencies

- `logos-foundry` v0.3.0 must be tagged before service work begins
- Services must be runnable locally for Phase 3 verification
- Docker/Compose required for OTel collector stack
