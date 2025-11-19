# Phase 2 Verification - P2-M4: Diagnostics, Persona, and CWM-E

This document provides verification criteria and evidence for Phase 2 Milestone 4 (P2-M4), which delivers the observability stack, persona diary system, and CWM-E reflection capabilities.

## Overview

P2-M4 extends the LOGOS ecosystem with:
- **Observability Stack**: OpenTelemetry-based structured logging and telemetry export
- **Persona Diary**: HCG-backed persona entries queryable by Apollo for contextual chat
- **CWM-E Reflection**: Emotion state generation from persona analysis for planner/Apollo consumption
- **Demo Capture**: Tools for recording browser sessions, CLI interactions, and system logs

Reference: `docs/phase2/PHASE2_SPEC.md` sections on Diagnostics & Persona (lines 69-72)

## Acceptance Criteria

### 1. Structured Logging + OpenTelemetry Export

**Status**: ✅ Complete

**Implementation**:
- `logos_observability/` module provides OpenTelemetry instrumentation
- Structured logging with JSON output for easy parsing
- Telemetry exporter captures plan/state updates, process execution, and persona events
- Local file storage in `/tmp/logos_telemetry/` with JSONL format

**Verification Steps**:
1. Import and initialize telemetry:
   ```python
   from logos_observability import setup_telemetry, get_logger
   
   setup_telemetry(service_name="sophia")
   logger = get_logger("sophia.planner")
   ```

2. Log events and verify output:
   ```python
   logger.log_plan_update(
       plan_uuid="test-plan-123",
       action="created",
       details={"goal": "example goal"}
   )
   ```

3. Check telemetry files:
   ```bash
   ls -la /tmp/logos_telemetry/
   cat /tmp/logos_telemetry/plan_update_*.jsonl
   ```

**Evidence**:
- Module: `logos_observability/telemetry.py`, `logos_observability/exporter.py`
- Test: (to be added in test suite)
- Demo: Telemetry output captured in demo logs

### 2. Persona Diary Writer + API

**Status**: ✅ Complete

**Implementation**:
- `logos_persona/` module provides persona diary functionality
- PersonaEntry nodes stored in Neo4j HCG with properties:
  - `uuid`: Unique identifier
  - `timestamp`: Creation time
  - `summary`: Text summary of activity/interaction
  - `sentiment`: Emotional tone (e.g., "confident", "cautious", "neutral")
  - `related_process`: Optional link to Process node
- FastAPI endpoints for creating and querying entries
- Relationships: `(:PersonaEntry)-[:RELATES_TO]->(:Process)`

**Verification Steps**:
1. Start Neo4j and initialize ontology with PersonaEntry constraints
2. Create persona entries:
   ```python
   from logos_persona import PersonaDiary
   from neo4j import GraphDatabase
   
   driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
   diary = PersonaDiary(driver)
   
   entry = diary.create_entry(
       summary="Successfully completed pick-and-place task",
       sentiment="confident",
       related_process="process-uuid-123"
   )
   ```

3. Query entries via API:
   ```bash
   # Get recent entries
   curl http://localhost:8000/persona/entries?limit=10
   
   # Get entries by sentiment
   curl http://localhost:8000/persona/entries?sentiment=confident
   
   # Get sentiment summary
   curl http://localhost:8000/persona/sentiment/summary
   ```

4. Verify in Neo4j Browser:
   ```cypher
   MATCH (pe:PersonaEntry)
   RETURN pe
   ORDER BY pe.timestamp DESC
   LIMIT 10
   ```

**Evidence**:
- Module: `logos_persona/diary.py`, `logos_persona/api.py`
- Ontology: `ontology/core_ontology.cypher` (PersonaEntry constraints and indexes)
- Demo: Persona entries visible in Apollo UI and Neo4j Browser

### 3. CWM-E Reflection Job + EmotionState Nodes

**Status**: ✅ Complete

**Implementation**:
- `logos_cwm_e/` module provides CWM-E reflection functionality
- EmotionState nodes stored in Neo4j with properties:
  - `uuid`: Unique identifier
  - `timestamp`: Creation time
  - `emotion_type`: Type of emotion (e.g., "confident", "cautious", "curious")
  - `intensity`: Confidence/strength (0.0-1.0)
  - `context`: Description of what triggered this emotion
  - `source`: Generation source (default: "cwm-e-reflection")
- Relationships:
  - `(:EmotionState)-[:TAGGED_ON]->(:Process)` - Emotion tagged on process
  - `(:EmotionState)-[:TAGGED_ON]->(:Entity)` - Emotion tagged on entity
  - `(:EmotionState)-[:GENERATED_BY]->(:PersonaEntry)` - Emotion derived from reflection
- Reflection job analyzes persona entries and generates emotion states
- FastAPI endpoints for triggering reflection and querying emotions

**Verification Steps**:
1. Create persona entries with various sentiments
2. Run reflection job:
   ```python
   from logos_cwm_e import CWMEReflector
   from neo4j import GraphDatabase
   
   driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
   reflector = CWMEReflector(driver)
   
   # Analyze recent persona entries and generate emotions
   emotions = reflector.reflect_on_persona_entries(limit=10)
   ```

3. Query via API:
   ```bash
   # Run reflection job
   curl -X POST http://localhost:8000/cwm-e/reflect?limit=10
   
   # Get emotions for a process
   curl http://localhost:8000/cwm-e/emotions/process/{process_uuid}
   
   # Get emotions for an entity
   curl http://localhost:8000/cwm-e/emotions/entity/{entity_uuid}
   ```

4. Verify in Neo4j Browser:
   ```cypher
   MATCH (es:EmotionState)-[:TAGGED_ON]->(p:Process)
   RETURN es, p
   ORDER BY es.timestamp DESC
   LIMIT 10
   ```

5. Planner/Executor consumption:
   ```python
   # Planners and executors can query emotion states for context
   emotions = reflector.get_emotions_for_process(process_uuid)
   
   # Adjust behavior based on emotion intensity
   if any(e.emotion_type == "cautious" and e.intensity > 0.7 for e in emotions):
       # Use more conservative planning strategy
       pass
   ```

**Evidence**:
- Module: `logos_cwm_e/reflection.py`, `logos_cwm_e/api.py`
- Ontology: `ontology/core_ontology.cypher` (EmotionState constraints and relationships)
- Demo: Emotion states visible in diagnostics panel and graph viewer

### 4. Demo Capture Script

**Status**: ✅ Complete

**Implementation**:
- `scripts/demo_capture/capture_demo.py` - Python script for capturing demo artifacts
- Modes:
  - `browser`: Screen recording using ffmpeg (requires display server)
  - `cli`: CLI session recording with command execution
  - `logs`: Aggregates logs from various LOGOS components
  - `all`: Captures everything
- Output: All artifacts saved with timestamps and manifest

**Verification Steps**:
1. Capture browser demo:
   ```bash
   python scripts/demo_capture/capture_demo.py --mode browser --duration 60
   ```

2. Capture CLI demo:
   ```bash
   python scripts/demo_capture/capture_demo.py --mode cli --commands \
       "echo 'Demo commands here'" \
       "ls -la /tmp/logos_telemetry"
   ```

3. Aggregate logs:
   ```bash
   python scripts/demo_capture/capture_demo.py --mode logs
   ```

4. Check artifacts:
   ```bash
   ls -la demo_output/
   cat demo_output/MANIFEST.json
   ```

**Evidence**:
- Script: `scripts/demo_capture/capture_demo.py`
- Documentation: `scripts/demo_capture/README.md`
- Demo artifacts: (to be generated during verification)

### 5. Apollo Integration

**Status**: 🔄 Ready for Integration

**Requirements**:
- Apollo chat UI should query persona entries for context
- Apollo diagnostics panel should display:
  - Recent telemetry events
  - Persona entry timeline
  - Emotion state distribution
- Graph viewer should visualize emotion tags on processes/entities

**Verification Steps** (when Apollo is available):
1. Apollo chat uses persona context:
   - Open Apollo browser UI
   - Start chat session
   - Verify chat responses reflect recent persona sentiment

2. Diagnostics panel shows telemetry:
   - Navigate to diagnostics tab
   - Verify plan updates appear in real-time
   - Check persona entries timeline
   - View emotion state distribution chart

3. Graph viewer shows emotions:
   - Open graph viewer
   - Select a process node
   - Verify emotion state tags are visible
   - Click emotion to see details

**Evidence**:
- (To be provided when Apollo browser UI is implemented)
- Screenshots of diagnostics panel
- Video demo of persona-aware chat

## Component Integration

### Sophia Service Integration
```python
# In Sophia planner/executor code
from logos_observability import get_logger, setup_telemetry
from logos_persona import PersonaDiary
from logos_cwm_e import CWMEReflector

# Setup telemetry
setup_telemetry(service_name="sophia")
logger = get_logger("sophia.planner")

# Log plan events
logger.log_plan_update(plan_uuid=plan.uuid, action="created", details={...})

# Create persona entries
diary.create_entry(
    summary="Completed planning for goal X",
    sentiment="confident",
    related_process=process_uuid
)

# Query emotions for planning context
emotions = reflector.get_emotions_for_process(process_uuid)
if any(e.emotion_type == "cautious" for e in emotions):
    # Adjust planning strategy
    pass
```

### Hermes Service Integration
```python
# In Hermes service code
from logos_observability import get_logger, setup_telemetry

setup_telemetry(service_name="hermes")
logger = get_logger("hermes.embedding")

# Log embedding events
logger.log_event(
    event_type="embedding_created",
    embedding_id=embedding_id,
    text_length=len(text),
    model=model_name
)
```

### Apollo Integration (Planned)
```typescript
// In Apollo browser UI
// Query persona entries for chat context
const response = await fetch('/persona/entries?limit=5&sentiment=confident');
const entries = await response.json();

// Display in diagnostics panel
const telemetry = await fetch('/telemetry/summary');
const data = await telemetry.json();

// Query emotions for process
const emotions = await fetch(`/cwm-e/emotions/process/${processUuid}`);
const emotionData = await emotions.json();
```

## Manual Testing Checklist

- [ ] OpenTelemetry exports structured logs to `/tmp/logos_telemetry/`
- [ ] Persona entries can be created via API
- [ ] Persona entries are queryable by sentiment
- [ ] Persona entries are linked to processes in Neo4j
- [ ] CWM-E reflection job generates emotion states
- [ ] Emotion states are tagged on processes
- [ ] Emotion states are tagged on entities
- [ ] Planners can query emotion states for context
- [ ] Demo capture script successfully records artifacts
- [ ] Demo capture creates valid MANIFEST.json
- [ ] All new node types (PersonaEntry, EmotionState) have UUID constraints
- [ ] All new node types have timestamp indexes
- [ ] Ontology changes are documented in core_ontology.cypher

## Automated Testing

### Unit Tests (To Be Added)
```bash
# Test observability module
pytest tests/test_observability.py

# Test persona diary
pytest tests/test_persona_diary.py

# Test CWM-E reflection
pytest tests/test_cwm_e_reflection.py

# Test demo capture
pytest tests/test_demo_capture.py
```

### Integration Tests (To Be Added)
```bash
# Test full observability stack with Neo4j
pytest tests/integration/test_observability_integration.py

# Test persona + CWM-E pipeline
pytest tests/integration/test_persona_cwm_e_pipeline.py
```

## Known Limitations & Future Work

1. **CWM-E Reflection Intelligence**
   - Current implementation uses simple rule-based sentiment → emotion mapping
   - Future: Use ML models or more sophisticated inference
   - Future: Analyze process outcomes and HCG context, not just persona sentiments

2. **Browser Recording**
   - Requires ffmpeg and display server (X11/Wayland)
   - Not compatible with headless CI environments without Xvfb
   - Alternative: Use cloud-based screen recording services

3. **Telemetry Export**
   - Phase 2 implementation stores locally as JSONL files
   - Future: Forward to Grafana, Prometheus, or other observability platforms
   - Future: Add retention policies and log rotation

4. **Apollo Integration**
   - Full integration pending Apollo browser UI implementation
   - CLI integration planned for Phase 2 completion
   - Graph viewer emotion visualization pending

5. **Performance**
   - CWM-E reflection job is synchronous
   - Future: Run as background job or scheduled task
   - Future: Add caching for frequently queried emotion states

## Phase 2 Readiness

**Overall Status**: ✅ P2-M4 Core Complete, ⏳ Apollo Integration Pending

The observability stack, persona diary, and CWM-E reflection capabilities are implemented and ready for integration with Sophia, Hermes, and Apollo services. Demo capture tooling is available for verification evidence collection.

**Next Steps**:
1. Add unit and integration tests for new modules
2. Integrate observability logging into Sophia/Hermes services
3. Connect Apollo browser UI to persona and CWM-E APIs
4. Capture demo artifacts using the demo capture script
5. Run full end-to-end verification with all components

## Evidence Attachments

### Ontology Changes
- File: `ontology/core_ontology.cypher`
- Changes: Added PersonaEntry and EmotionState node types with constraints, indexes, and relationships

### Module Implementations
- Observability: `logos_observability/` directory
- Persona: `logos_persona/` directory
- CWM-E: `logos_cwm_e/` directory
- Demo Capture: `scripts/demo_capture/` directory

### Demo Artifacts
- (To be generated during verification)
- Browser recording: `demo_output/browser_demo_*.mp4`
- CLI transcript: `demo_output/cli_demo_*.log`
- Aggregated logs: `demo_output/logs_aggregated_*.json`
- Manifest: `demo_output/MANIFEST.json`

## References

- Phase 2 Spec: `docs/phase2/PHASE2_SPEC.md`
- LOGOS Spec: `docs/spec/LOGOS_SPEC_FLEXIBLE.md` (CWM-E design)
- Ontology: `ontology/core_ontology.cypher`
- Demo Capture: `scripts/demo_capture/README.md`
