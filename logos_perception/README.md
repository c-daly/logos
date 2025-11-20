# LOGOS Perception Pipeline

The perception pipeline provides media ingestion and imagination simulation capabilities for the LOGOS cognitive architecture.

## Overview

This module implements:

- **Media Ingest Service**: Upload and stream media frames (video/images/audio)
- **JEPA Runner**: k-step imagination rollout for predictive simulation
- **Storage Integration**: Neo4j (metadata) and Milvus (embeddings) persistence
- **API Endpoints**: `/simulate` for triggering imagination workflows

## Components

### Media Ingest Service

Handles media frame uploads and streaming:

```python
from logos_perception import MediaIngestService

service = MediaIngestService(neo4j_driver)

# Ingest a frame
frame = service.ingest_frame(
    data=image_bytes,
    format="image/jpeg",
    metadata={"source": "camera-1"}
)

# Store embedding
service.store_frame_embedding(frame.frame_id, embedding_vector)

# Link to simulation
service.link_frame_to_simulation(frame.frame_id, process_uuid)
```

### JEPA Runner

Performs k-step imagination rollouts:

```python
from logos_perception import JEPARunner, JEPAConfig

# Initialize with default config (CPU-friendly mode)
runner = JEPARunner()

# Run simulation
result = runner.simulate(
    capability_id="pick-and-place",
    context={"entity_id": "robot-arm-1"},
    k_steps=5
)

# Access results
print(f"Process UUID: {result.process.uuid}")
print(f"Generated {len(result.states)} imagined states")
```

### Simulation Service

Integrates JEPA runner with Neo4j/Milvus storage:

```python
from logos_sophia import SimulationService
from logos_perception import SimulationRequest

service = SimulationService(neo4j_driver)

request = SimulationRequest(
    capability_id="test-capability",
    context={"entity_id": "test-entity"},
    k_steps=5
)

result = service.run_simulation(request)
```

## API Endpoints

### POST `/sophia/simulate`

Run k-step imagination simulation.

**Request:**
```json
{
  "capability_id": "pick-and-place",
  "context": {
    "entity_id": "robot-arm-1",
    "initial_position": [1.0, 2.0, 3.0]
  },
  "k_steps": 5,
  "frame_id": "optional-frame-id"
}
```

**Response:**
```json
{
  "process_uuid": "uuid-123",
  "states_count": 5,
  "horizon": 5,
  "model_version": "jepa-v0.1"
}
```

### GET `/sophia/simulate/{process_uuid}`

Retrieve simulation results.

**Response:**
```json
{
  "process": {
    "uuid": "uuid-123",
    "capability_id": "pick-and-place",
    "imagined": true,
    "horizon": 5
  },
  "states": [
    {
      "uuid": "state-1",
      "step": 0,
      "confidence": 1.0
    }
  ]
}
```

## HCG Storage

### Neo4j Nodes

**PerceptionFrame:**
```cypher
CREATE (f:PerceptionFrame {
  uuid: "frame-123",
  timestamp: datetime(),
  format: "image/jpeg",
  metadata: {...}
})
```

**ImaginedProcess:**
```cypher
CREATE (p:ImaginedProcess {
  uuid: "process-123",
  capability_id: "pick-and-place",
  imagined: true,
  horizon: 5,
  model_version: "jepa-v0.1"
})
```

**ImaginedState:**
```cypher
CREATE (s:ImaginedState {
  uuid: "state-123",
  step: 0,
  confidence: 1.0,
  metadata: {...}
})
```

### Relationships

```cypher
(PerceptionFrame)-[:TRIGGERED_SIMULATION]->(ImaginedProcess)
(ImaginedProcess)-[:PREDICTS]->(ImaginedState)
(ImaginedState)-[:PRECEDES]->(ImaginedState)
```

## Operating Modes

### CPU-Friendly Mode (Default)

For Talos-free scenarios:
- No hardware dependencies
- Fast iteration for development
- Mock embeddings with stochastic noise
- Confidence degradation over horizon

### Hardware Simulator Mode (Optional)

For Talos/Gazebo integration:
```python
runner = JEPARunner()
runner.connect_hardware_sim("http://talos.local:11345")
```

See `docs/phase2/perception/TALOS_INTEGRATION.md` for details.

## Testing

Run perception tests:
```bash
pytest tests/phase2/perception/ -v
```

Test coverage:
- JEPA runner unit tests
- Simulation service integration tests
- API endpoint tests
- Mock and real Neo4j scenarios

## Phase 2 Milestones

This module satisfies **P2-M3: Perception & Imagination**:

- ✅ Media ingest service
- ✅ JEPA runner with k-step rollout
- ✅ `/simulate` endpoint
- ✅ Neo4j/Milvus storage
- ✅ Talos integration hooks documented
- ✅ CI workflow with smoke tests

## References

- Phase 2 Spec: `docs/phase2/PHASE2_SPEC.md`
- Talos Integration: `docs/phase2/perception/TALOS_INTEGRATION.md`
- Ontology: `ontology/core_ontology.cypher`
- SHACL Shapes: `ontology/shacl_shapes.ttl`
