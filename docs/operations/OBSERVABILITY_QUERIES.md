# LOGOS Observability Query Snippets

This doc targets the current OTEL stack: Collector → Jaeger (traces) + Prometheus (metrics). Use Tempo/TraceQL only if you stand up the optional Tempo stack.

## Jaeger (traces)

- Filter by service: set `Service` dropdown to `sophia`, `hermes`, `apollo-cli`, or `apollo-webapp`.
- Filter by endpoint (Operation): e.g. `/plan`, `/state`, `/simulate`, `embed_text`.
- Filter by trace attributes (Tags):
  - `plan_id=<uuid>` to follow a specific plan.
  - `http.status_code=500` for errors.
  - `otel.status_code=ERROR` to find failing spans.
- Time filters: use “Min Duration” (`1s` for slow spans) or “Max Duration” (`100ms` for fast spans).

Suggested tag searches:
- Perception flow: `resource.service.name=sophia` + `span.name=/simulate`
- Persona/diary: `resource.service.name=sophia` + `span.name=/persona`
- NLP/embeddings: `resource.service.name=hermes` + `span.name=embed_text`

## Prometheus (metrics)

Paste these into the Prometheus UI (http://localhost:9090):
- Target health: `up`
- Collector send failures: `otelcol_exporter_send_failed_spans`
- Collector queue pressure: `otelcol_processor_batch_batch_send_size_sum`
- HTTP latencies (if exported): `http_server_request_duration_seconds_bucket`
- Exporter latency (gRPC): `otelcol_exporter_queue_size`

Common checks:
- `up{job="otel-collector"}` should be 1.
- `up{job="sophia"}` / `up{job="hermes"}` / `up{job="apollo"}` should be 1 when those services are running in the stack.
- `sum(rate(otelcol_exporter_send_failed_spans[5m])) > 0` indicates trace export problems.

## Optional: Tempo/TraceQL (archival)

If you bring back the Tempo stack, these TraceQL snippets still apply:
- All spans for a service: `{ resource.service.name="sophia" }`
- Endpoint filter: `{ span.name="/plan" }`
- Plan-scoped: `{ span.plan_id="<plan-uuid>" }`
- Errors: `{ status=error }`

### Hermes embedding operations
```traceql
{ resource.service.name="hermes" && span.name="embed_text" }
```

### High-horizon simulations (>10 steps)
```traceql
{ span.horizon > 10 }
```

## Error Analysis

### All failed operations
```traceql
{ status=error }
```

### Failed simulations
```traceql
{ span.name="/simulate" && status=error }
```

### Service-specific errors
```traceql
{ resource.service.name="sophia" && status=error }
```

## Time-Based Queries

Grafana's time picker controls the time range. Combine with other filters:

### Recent plan executions (use dashboard time picker)
```traceql
{ span.plan_id != nil }
```

### Recent simulations
```traceql
{ span.name="/simulate" }
```

## Capability-Specific Queries

### Traces for specific capability
```traceql
{ span.capability_id="<capability-uuid>" }
```

### All capability-related traces
```traceql
{ span.capability_id != nil }
```

## Advanced Queries

### Successful simulations with high horizon
```traceql
{ span.name="/simulate" && span.horizon > 5 && status=ok }
```

### Plan executions that took longer than expected
```traceql
{ span.plan_id != nil && duration > 2s }
```

### Traces with multiple services (distributed traces)
```traceql
{ resource.service.name="sophia" } && { resource.service.name="hermes" }
```

## Aggregation Queries

### Count of traces by service (use Grafana aggregation)
In Grafana, use the "Service Graph" or "Trace Statistics" panels with:
```traceql
{ }  # All traces, then group by service.name
```

### Average duration by endpoint
Use metrics panels in Grafana with trace data:
```traceql
{ span.name=~"/.*" }  # Regex for all endpoints
```

## Debugging Queries

### Find traces without plan_id (should be rare)
```traceql
{ resource.service.name="sophia" && span.plan_id = nil }
```

### Traces with unusual attributes
```traceql
{ span.http.status_code >= 500 }
```

### Long-running background processes
```traceql
{ duration > 30s }
```

## P2-M4 Verification Queries

These queries are specifically for P2-M4 acceptance criteria verification:

### Verify plan_id linking works
```traceql
{ span.plan_id != nil }
```
**Expected**: Should return traces from Sophia service with plan_id attributes

### Verify /simulate traces exist
```traceql
{ span.name="/simulate" }
```
**Expected**: Should return simulation request traces

### Verify embedding throughput tracking
```traceql
{ resource.service.name="hermes" && span.name="embed_text" }
```
**Expected**: Should return embedding operation traces

### Verify services are instrumented
```traceql
{ resource.service.name=~"sophia|hermes|apollo" }
```
**Expected**: Should return traces from all three services

## Tips

1. **Use the time picker**: Tempo searches within the selected time range
2. **Combine filters**: Use `&&` to AND conditions, `||` to OR
3. **Use regex**: `span.name=~"/sim.*"` matches `/simulate` and similar
4. **Export traces**: Click on a trace to export it for verification artifacts
5. **Create alerts**: Use these queries as basis for Grafana alerts

## Dashboard Panels

The LOGOS Key Signals dashboard includes panels for:
- Sophia Service Traces
- /simulate Endpoint Traces  
- Plan Execution Traces (with plan_id)
- Hermes Service Traces

Use these as starting points and customize with the queries above.

## See Also

- [TraceQL Documentation](https://grafana.com/docs/tempo/latest/traceql/)
- [OTEL_SETUP.md](../infra/OTEL_SETUP.md) - Complete setup guide
- [Phase 2 Spec](../docs/architecture/PHASE2_SPEC.md) - Diagnostics requirements
