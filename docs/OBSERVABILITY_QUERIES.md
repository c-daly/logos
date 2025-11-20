# LOGOS Observability Query Snippets

This document contains useful TraceQL queries and examples for exploring LOGOS traces in Grafana Tempo.

## Basic Queries

### All traces from a specific service
```traceql
{ resource.service.name="sophia" }
{ resource.service.name="hermes" }
{ resource.service.name="apollo" }
```

### Traces for a specific endpoint
```traceql
{ span.name="/simulate" }
{ span.name="/plan" }
{ span.name="/state" }
{ span.name="embed_text" }
```

## Plan-Centric Queries

### All traces linked to a specific plan
```traceql
{ span.plan_id="<your-plan-uuid>" }
```

### All traces with plan_id attributes
```traceql
{ span.plan_id != nil }
```

### Failed plan executions
```traceql
{ span.plan_id != nil && status=error }
```

## Performance Queries

### Slow operations (>1 second)
```traceql
{ duration > 1s }
```

### Very slow operations (>5 seconds)
```traceql
{ duration > 5s }
```

### Fast operations (<100ms)
```traceql
{ duration < 100ms }
```

## Service-Specific Queries

### Sophia simulation traces
```traceql
{ resource.service.name="sophia" && span.name="/simulate" }
```

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
- [Phase 2 Spec](../docs/phase2/PHASE2_SPEC.md) - Diagnostics requirements
