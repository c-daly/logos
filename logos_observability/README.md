# LOGOS Observability Module

OpenTelemetry-based observability stack for LOGOS services.

## Overview

The `logos_observability` module provides:
- **Structured logging** with JSON output for easy parsing
- **OpenTelemetry integration** for distributed tracing
- **Telemetry exporter** for capturing events to local files or external collectors

## Usage

### Basic Setup

```python
from logos_observability import setup_telemetry, get_logger

# Initialize OpenTelemetry
setup_telemetry(service_name="sophia", export_to_console=True)

# Get a structured logger
logger = get_logger("sophia.planner")
```

### Logging Events

The structured logger provides specialized methods for LOGOS events:

```python
# Log plan updates
logger.log_plan_update(
    plan_uuid="plan-123",
    action="created",
    details={"goal": "pick and place", "steps": 5}
)

# Log state changes
logger.log_state_change(
    entity_uuid="entity-456",
    state_uuid="state-789",
    old_state="idle",
    new_state="moving"
)

# Log process execution
logger.log_process_execution(
    process_uuid="process-101",
    status="completed",
    duration_ms=1250.5
)

# Log persona entries
logger.log_persona_entry(
    entry_uuid="entry-202",
    summary="Successfully completed task",
    sentiment="confident"
)

# Log emotion states
logger.log_emotion_state(
    emotion_uuid="emotion-303",
    emotion_type="confident",
    intensity=0.85,
    context="After successful task completion"
)
```

### Telemetry Export

Export telemetry events to local files:

```python
from logos_observability import TelemetryExporter

# Initialize exporter
exporter = TelemetryExporter(output_dir="/tmp/logos_telemetry")

# Export events
event = {
    "timestamp": "2025-11-19T23:00:00Z",
    "event_type": "plan_update",
    "plan_uuid": "plan-123",
    "action": "created"
}
exporter.export_event(event)

# Retrieve events
events = exporter.get_events(event_type="plan_update")

# Get summary
summary = exporter.get_summary()
print(summary)
```

## Output Format

Events are stored as JSON Lines (JSONL) files:

```bash
/tmp/logos_telemetry/
├── plan_update_2025-11-19.jsonl
├── state_change_2025-11-19.jsonl
├── persona_entry_2025-11-19.jsonl
└── emotion_state_2025-11-19.jsonl
```

Each line is a valid JSON object:

```json
{"timestamp": "2025-11-19T23:00:00Z", "event_type": "plan_update", "plan_uuid": "plan-123", "action": "created"}
```

## Integration with Services

### Sophia Service

```python
from logos_observability import setup_telemetry, get_logger

setup_telemetry(service_name="sophia")
logger = get_logger("sophia.orchestrator")

# In planner
logger.log_plan_update(plan_uuid=plan.uuid, action="validated")

# In executor
logger.log_process_execution(
    process_uuid=process.uuid,
    status="completed",
    duration_ms=duration
)
```

### Hermes Service

```python
from logos_observability import setup_telemetry, get_logger

setup_telemetry(service_name="hermes")
logger = get_logger("hermes.embedding")

# Log embedding creation
logger._log_event(
    event_type="embedding_created",
    embedding_id=embedding_id,
    text_length=len(text),
    model=model_name
)
```

### Apollo Client

```python
from logos_observability import setup_telemetry, get_logger

setup_telemetry(service_name="apollo-cli")
logger = get_logger("apollo.cli")

# Log user interactions
logger._log_event(
    event_type="user_command",
    command="plan",
    args=args
)
```

## Configuration

Environment variables for configuration:

- `LOGOS_TELEMETRY_DIR` - Output directory for telemetry files (default: `/tmp/logos_telemetry`)
- `LOGOS_TELEMETRY_CONSOLE` - Enable console output (default: `false`)
- `LOGOS_SERVICE_NAME` - Service name for telemetry (default: `logos-service`)

## See Also

- `docs/phase2/VERIFY.md` - P2-M4 verification checklist
- `docs/phase2/PHASE2_SPEC.md` - Phase 2 specification (Diagnostics section)
- `examples/p2_m4_demo.py` - Example usage
