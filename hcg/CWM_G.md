# CWM-G:Grounded World Model

CWM-G stores learned dynamics and predictions from the JEPA (Joint Embedding
Predictive Architecture) model. It enables Sophia to imagine future states,
assess action feasibility, and ground abstract plans in physical reality.

## Table of Contents

- [Overview](#overview)
- [Node Types](#node-types)
- [Relationships](#relationships)
- [Properties Reference](#properties-reference)
- [JEPA Integration](#jepa-integration)
- [Query Patterns](#query-patterns)
- [Examples](#examples)

## Overview

CWM-G provides physics-grounded predictions:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CWM-G                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────────┐                    │
│  │ Perception   │      │    Imagined      │                    │
│  │   Frame      │─────►│    Process       │                    │
│  └──────────────┘      └────────┬─────────┘                    │
│                                 │                               │
│                                 ▼                               │
│                        ┌──────────────────┐                    │
│                        │  ImaginedState   │                    │
│                        │     (t+1)        │                    │
│                        └────────┬─────────┘                    │
│                                 │                               │
│                                 ▼                               │
│                        ┌──────────────────┐                    │
│                        │  ImaginedState   │                    │
│                        │     (t+2)        │                    │
│                        └────────┬─────────┘                    │
│                                 │                               │
│                                 ▼                               │
│                               ...                               │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases

1. **Action Feasibility**: "Can I grasp this object from this angle?"
2. **Outcome Prediction**: "What happens if I push this block?"
3. **Plan Validation**: "Will this sequence of actions achieve the goal?"
4. **Visual Imagination**: "What will the scene look like after the action?"

## Node Types

### PerceptionFrame

Represents a single frame of perception input (image, video frame, sensor reading).

```cypher
CREATE (pf:PerceptionFrame {
    uuid: 'frame-20251201-143022-001',
    timestamp: datetime(),
    format: 'image/jpeg',
    width: 1920,
    height: 1080,
    source: 'camera-front',
    embedding_id: 'milvus-frame-001',
    metadata: '{"exposure": 0.016, "iso": 400}',
    created_at: datetime()
})
```

### ImaginedProcess

Represents a JEPA simulation rollout for a specific action/capability.

```cypher
CREATE (ip:ImaginedProcess {
    uuid: 'imgproc-pick-red-block-001',
    timestamp: datetime(),
    capability_id: 'capability-talos-pick',
    action_parameters: '{"target": "entity-red-block", "approach": "top"}',
    horizon: 10,
    model_version: 'jepa-v2.1',
    imagined: true,
    latent_trajectory: '[...]',  // encoded latent states
    total_confidence: 0.87,
    computation_time_ms: 250,
    created_at: datetime()
})
```

### ImaginedState

Represents a single predicted future state from a simulation.

```cypher
CREATE (is:ImaginedState {
    uuid: 'imgstate-pick-red-block-001-step-5',
    timestamp: datetime(),
    step: 5,
    confidence: 0.82,
    predicted_position: '{"x": 0.5, "y": 0.3, "z": 0.1}',
    predicted_orientation: '{"roll": 0, "pitch": 0, "yaw": 0.5}',
    latent_state: '[0.12, -0.34, ...]',
    decoded_description: 'Block grasped, moving to target',
    metadata: '{"collision_probability": 0.02}',
    created_at: datetime()
})
```

## Relationships

### PerceptionFrame Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `TRIGGERED_SIMULATION` | ImaginedProcess | Frame initiated this rollout |
| `CONTAINS` | Entity | Entities detected in frame |
| `PRECEDES` | PerceptionFrame | Temporal ordering |
| `CAPTURES` | State | Current state of entities |

### ImaginedProcess Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `PREDICTS` | ImaginedState | States predicted by this process |
| `TRIGGERED_BY` | PerceptionFrame | Source perception |
| `USES_CAPABILITY` | Capability | Capability being simulated |
| `VALIDATED_BY` | Process | Actual execution that validated |

### ImaginedState Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `PRECEDES` | ImaginedState | Next state in sequence |
| `PREDICTED_BY` | ImaginedProcess | Process that predicted this |
| `MATCHES` | State | Actual state it was compared to |
| `PROMOTED_TO` | Fact | If prediction became fact |

## Properties Reference

### PerceptionFrame Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `frame-` |
| `timestamp` | datetime | ✓ | Capture time |
| `format` | string | ✓ | MIME type (image/jpeg, video/mp4) |
| `width` | integer | | Frame width in pixels |
| `height` | integer | | Frame height in pixels |
| `source` | string | | Camera/sensor ID |
| `embedding_id` | string | | Milvus vector ID |
| `metadata` | JSON | | Sensor-specific metadata |

### ImaginedProcess Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `imgproc-` |
| `timestamp` | datetime | ✓ | Simulation start time |
| `capability_id` | string | ✓ | Capability being simulated |
| `action_parameters` | JSON | | Parameters for the action |
| `horizon` | integer | ✓ | Number of steps predicted |
| `model_version` | string | ✓ | JEPA model version |
| `imagined` | boolean | ✓ | Must be true |
| `latent_trajectory` | string | | Encoded latent states |
| `total_confidence` | decimal | | Overall prediction confidence |
| `computation_time_ms` | integer | | Time to compute |

### ImaginedState Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `imgstate-` |
| `timestamp` | datetime | ✓ | Prediction time |
| `step` | integer | ✓ | Step number (0 = initial) |
| `confidence` | decimal | ✓ | 0.0-1.0 |
| `predicted_position` | JSON | | x, y, z coordinates |
| `predicted_orientation` | JSON | | roll, pitch, yaw |
| `latent_state` | string | | Encoded latent vector |
| `decoded_description` | string | | Human-readable description |
| `metadata` | JSON | | Additional predictions |

## JEPA Integration

### Simulation Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ PerceptionFrame │───►│   JEPA Model    │───►│ ImaginedProcess │
│   (current)     │    │  (prediction)   │    │ + ImaginedStates│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Milvus Vectors │
                       │ (latent states) │
                       └─────────────────┘
```

### API Flow

1. **Trigger Simulation**:
   ```http
   POST /sophia/imagine
   {
     "cwm_g_imagery": [{"type": "visual", "frame_id": "frame-001"}],
     "capability_id": "capability-talos-pick",
     "horizon": 10,
     "model_version": "v2.1"
   }
   ```

2. **JEPA Processing**:
   - Encode current frame to latent space
   - Apply action in latent space
   - Rollout for `horizon` steps
   - Decode predictions

3. **Store Results**:
   - Create `ImaginedProcess` node
   - Create `ImaginedState` nodes for each step
   - Store latent vectors in Milvus
   - Link with relationships

### Confidence Decay

Prediction confidence typically decreases with horizon:

```
confidence(step) = base_confidence * decay_rate^step
```

Default decay rate: 0.95 per step

## Query Patterns

### Find Recent Simulations for Entity

```cypher
MATCH (ip:ImaginedProcess)-[:PREDICTS]->(is:ImaginedState)
WHERE ip.timestamp > datetime() - duration('PT1H')
  AND ip.action_parameters CONTAINS $entity_uuid
RETURN ip, collect(is) as states
ORDER BY ip.timestamp DESC
```

### Find High-Confidence Predictions

```cypher
MATCH (ip:ImaginedProcess)-[:PREDICTS]->(is:ImaginedState)
WHERE is.confidence >= 0.8
RETURN ip, is
ORDER BY is.confidence DESC
LIMIT 50
```

### Trace Prediction to Perception

```cypher
MATCH (pf:PerceptionFrame)-[:TRIGGERED_SIMULATION]->(ip:ImaginedProcess)
      -[:PREDICTS]->(is:ImaginedState)
WHERE ip.uuid = $process_uuid
RETURN pf, ip, collect(is) as trajectory
```

### Compare Prediction to Reality

```cypher
MATCH (is:ImaginedState)-[:MATCHES]->(actual:State)
WHERE is.uuid STARTS WITH $process_prefix
RETURN is.step, is.confidence, 
       is.predicted_position, actual.position_x, actual.position_y, actual.position_z,
       abs(is.confidence - 1.0) as error
```

## Examples

### Pick and Place Simulation

```cypher
// Create perception frame
CREATE (pf:PerceptionFrame {
    uuid: 'frame-20251201-143022-001',
    timestamp: datetime(),
    format: 'image/jpeg',
    source: 'camera-front',
    embedding_id: 'milvus-frame-001'
})

// Create imagined process for pick action
CREATE (ip:ImaginedProcess {
    uuid: 'imgproc-pick-001',
    timestamp: datetime(),
    capability_id: 'capability-talos-pick',
    action_parameters: '{"target": "entity-red-block"}',
    horizon: 8,
    model_version: 'jepa-v2.1',
    imagined: true,
    total_confidence: 0.89
})

// Link perception to process
CREATE (pf)-[:TRIGGERED_SIMULATION]->(ip)

// Create imagined states
CREATE (is0:ImaginedState {
    uuid: 'imgstate-pick-001-0',
    timestamp: datetime(),
    step: 0,
    confidence: 0.95,
    decoded_description: 'Gripper approaching block'
})

CREATE (is1:ImaginedState {
    uuid: 'imgstate-pick-001-1',
    timestamp: datetime(),
    step: 1,
    confidence: 0.92,
    decoded_description: 'Gripper closing on block'
})

CREATE (is2:ImaginedState {
    uuid: 'imgstate-pick-001-2',
    timestamp: datetime(),
    step: 2,
    confidence: 0.88,
    decoded_description: 'Block lifted'
})

// Link process to states
CREATE (ip)-[:PREDICTS]->(is0)
CREATE (ip)-[:PREDICTS]->(is1)
CREATE (ip)-[:PREDICTS]->(is2)

// Link state sequence
CREATE (is0)-[:PRECEDES]->(is1)
CREATE (is1)-[:PRECEDES]->(is2)
```

### Validating a Prediction

```cypher
// After actual execution, link prediction to reality
MATCH (is:ImaginedState {uuid: 'imgstate-pick-001-2'})
MATCH (actual:State {uuid: 'state-gripper-001-t3'})
CREATE (is)-[:MATCHES {
    position_error: 0.02,
    orientation_error: 0.05,
    validated_at: datetime()
}]->(actual)

// Update process with validation
MATCH (ip:ImaginedProcess {uuid: 'imgproc-pick-001'})
MATCH (p:Process {uuid: 'process-pick-red-block'})
CREATE (ip)-[:VALIDATED_BY]->(p)
SET ip.validated = true,
    ip.actual_success = true
```

## See Also

- [CWM State Overview](./CWM_STATE.md) - High-level CWM architecture
- [CWM-A Schema](./CWM_A.md) - Abstract world model
- [CWM-E Schema](./CWM_E.md) - Emotional world model
- [JEPA Runner](../../sophia/src/sophia/jepa/) - JEPA implementation
- [Ingestion Flows](./INGESTION.md) - How data enters CWM-G
