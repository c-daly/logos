# LOGOS CWM-E Module

Causal World Model - Emotional/Social reflection for generating emotion state tags.

## Overview

The `logos_cwm_e` module provides:
- **CWM-E reflection** that analyzes persona entries and HCG context
- **EmotionState nodes** tagged on processes and entities
- **Emotion queries** for planners, executors, and Apollo
- **FastAPI endpoints** for triggering reflection and querying emotions

## CWM-E Design Philosophy

CWM-E (Causal World Model - Emotional/Social) is the third layer of Sophia's world model, complementing:
- **CWM-A**: Abstract/commonsense reasoning in the HCG
- **CWM-G**: Grounded physics/perception (JEPA-style predictions)
- **CWM-E**: Affective/social signals derived from reflection

CWM-E reflects on stored memories (persona entries) to infer confidence, trust, or other affective signals. These emotion states are written back to the HCG as tags on processes and entities, allowing planners and Apollo to adjust behavior and tone.

## Usage

### Basic Usage

```python
from logos_cwm_e import CWMEReflector
from neo4j import GraphDatabase

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
reflector = CWMEReflector(driver)

# Create an emotion state
emotion = reflector.create_emotion_state(
    emotion_type="confident",
    intensity=0.85,
    context="After successful task completion"
)

# Tag a process
reflector.tag_process(emotion.uuid, "process-uuid-123")
```

### Running Reflection

The reflection job analyzes recent persona entries and generates emotion states:

```python
# Analyze last 10 persona entries
emotions = reflector.reflect_on_persona_entries(limit=10)

for emotion in emotions:
    print(f"Generated: {emotion.emotion_type} (intensity: {emotion.intensity})")
```

### Querying Emotions

```python
# Get emotions for a process
process_emotions = reflector.get_emotions_for_process("process-uuid-123")

# Get emotions for an entity
entity_emotions = reflector.get_emotions_for_entity("entity-uuid-456")

# Use in planning
if any(e.emotion_type == "cautious" and e.intensity > 0.7 for e in process_emotions):
    # Use more conservative planning strategy
    plan_conservatively()
```

## Node Schema

EmotionState nodes have the following properties:

```cypher
(:EmotionState {
    uuid: String,          // Unique identifier (required)
    timestamp: String,     // ISO 8601 timestamp (required)
    emotion_type: String,  // Type of emotion (required)
    intensity: Float,      // Confidence/strength 0.0-1.0 (required)
    context: String,       // Description of trigger (optional)
    source: String         // Generation source (default: "cwm-e-reflection")
})
```

Relationships:
- `(:EmotionState)-[:TAGGED_ON]->(:Process)` - Tagged on process
- `(:EmotionState)-[:TAGGED_ON]->(:Entity)` - Tagged on entity
- `(:EmotionState)-[:GENERATED_BY]->(:PersonaEntry)` - Derived from reflection

## Emotion Types

Common emotion types in LOGOS:
- `confident` - High certainty, successful outcomes
- `cautious` - Low certainty, potential risks detected
- `curious` - Exploring new situations or strategies
- `neutral` - No strong affective signal
- `concerned` - Issues detected, low success probability

Intensity values (0.0-1.0):
- `0.0-0.3` - Weak signal
- `0.4-0.6` - Moderate signal
- `0.7-1.0` - Strong signal

## FastAPI Integration

Create API endpoints for triggering reflection and querying emotions:

```python
from fastapi import FastAPI
from logos_cwm_e import create_cwm_e_api

app = FastAPI()

# Add CWM-E routes
cwm_e_router = create_cwm_e_api(driver)
app.include_router(cwm_e_router)
```

### API Endpoints

#### Run Reflection Job
```bash
POST /cwm-e/reflect?limit=10
```

#### Create Emotion State
```bash
POST /cwm-e/emotions
{
    "emotion_type": "confident",
    "intensity": 0.85,
    "context": "After successful task"
}
```

#### Tag Process
```bash
POST /cwm-e/emotions/tag-process
{
    "emotion_uuid": "emotion-uuid",
    "process_uuid": "process-uuid"
}
```

#### Get Emotions for Process
```bash
GET /cwm-e/emotions/process/{process_uuid}
```

#### Get Emotions for Entity
```bash
GET /cwm-e/emotions/entity/{entity_uuid}
```

## Integration with Planner

Planners can query emotion states to adjust behavior:

```python
# Check confidence before executing risky action
emotions = reflector.get_emotions_for_process(current_process_uuid)
high_confidence = any(
    e.emotion_type == "confident" and e.intensity > 0.7
    for e in emotions
)

if not high_confidence:
    # Request human confirmation or use safer alternative
    plan_with_confirmation()
```

## Integration with Apollo

Apollo can display emotions in diagnostics and adjust chat tone:

```typescript
// Query emotions for process
const response = await fetch(`/cwm-e/emotions/process/${processUuid}`);
const emotions = await response.json();

// Adjust chat tone based on emotions
const isCautious = emotions.some(e => 
    e.emotion_type === 'cautious' && e.intensity > 0.6
);

if (isCautious) {
    tone = "careful and thorough";
}
```

## Reflection Algorithm

The Phase 2 implementation uses simple rule-based inference:

1. Query recent PersonaEntry nodes from Neo4j
2. For each entry with a sentiment:
   - Map sentiment → emotion type + intensity
   - Create EmotionState node
   - Link back to PersonaEntry (GENERATED_BY)
   - If entry has related_process, tag the process (TAGGED_ON)

Future phases will use:
- ML models for sentiment analysis
- Process outcome analysis (success/failure patterns)
- HCG context analysis (preconditions, causal chains)

## Neo4j Queries

### View Recent Emotions
```cypher
MATCH (es:EmotionState)
RETURN es
ORDER BY es.timestamp DESC
LIMIT 10
```

### Emotions Tagged on Process
```cypher
MATCH (es:EmotionState)-[:TAGGED_ON]->(p:Process {uuid: 'process-uuid'})
RETURN es, p
```

### Emotion Generation Chain
```cypher
MATCH (es:EmotionState)-[:GENERATED_BY]->(pe:PersonaEntry)-[:RELATES_TO]->(p:Process)
RETURN es, pe, p
```

## See Also

- `docs/phase2/VERIFY.md` - P2-M4 verification checklist
- `docs/phase2/PHASE2_SPEC.md` - Phase 2 specification (CWM-E section)
- `docs/spec/LOGOS_SPEC_FLEXIBLE.md` - CWM-E design principles
- `logos_persona/` - Persona diary module
- `examples/p2_m4_demo.py` - Example usage
