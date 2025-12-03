# CWM Ingestion Flows

This document describes how data enters the Causal World Model (CWM) from
various sources and how it flows between subsystems.

## Table of Contents

- [Overview](#overview)
- [Ingestion Sources](#ingestion-sources)
- [Flow Diagrams](#flow-diagrams)
- [CWM-A Ingestion](#cwm-a-ingestion)
- [CWM-G Ingestion](#cwm-g-ingestion)
- [CWM-E Ingestion](#cwm-e-ingestion)
- [Cross-CWM Promotion](#cross-cwm-promotion)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)

## Overview

Data enters the CWM through multiple pathways:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION SOURCES                                 │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│    Talos    │   JEPA      │   Sophia    │  Knowledge  │      Human          │
│ (sensors)   │ (perception)│ (planner)   │    Base     │    (feedback)       │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │             │                 │
       ▼             ▼             ▼             ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │Validation│ → │ Conflict │ → │ Embedding│ → │ Neo4j    │ → │ Milvus   │  │
│  │          │   │  Check   │   │ Generate │   │  Write   │   │  Sync    │  │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
       │                                                              │
       ▼                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  HCG                                        │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│       CWM-A         │       CWM-G         │       CWM-E                     │
│  (Facts, Rules)     │  (Perception,       │  (Emotions, Diary)              │
│                     │   Imagination)      │                                 │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

### Pipeline Stages

1. **Validation**: SHACL shape validation, schema conformance
2. **Conflict Check**: Detect contradictions with existing knowledge
3. **Embedding Generate**: Create vector embeddings for semantic search
4. **Neo4j Write**: Persist node/relationship to graph
5. **Milvus Sync**: Index vector for similarity search

## Ingestion Sources

### Talos (Sensor Data)

Talos streams real-time sensor data:

| Data Type | Target CWM | Node Type | Example |
|-----------|------------|-----------|---------|
| Camera frames | CWM-G | `PerceptionFrame` | Video frame with objects |
| Joint states | CWM-G | `State` | Robot arm configuration |
| Force sensor | CWM-G | `State` | Gripper force reading |
| Object detection | CWM-A | `Fact` (hypothesis) | "Block detected at (x,y,z)" |

### JEPA (Perception System)

JEPA processes sensor data into predictions:

| Data Type | Target CWM | Node Type | Description |
|-----------|------------|-----------|-------------|
| Frame embeddings | CWM-G | `PerceptionFrame` | Latent representation |
| Action predictions | CWM-G | `ImaginedProcess` | Predicted action outcome |
| State predictions | CWM-G | `ImaginedState` | Future state sequence |
| Learned facts | CWM-A | `Fact` (hypothesis) | "Heavy objects fall faster" |

### Sophia (Planner)

Sophia generates planning artifacts:

| Data Type | Target CWM | Node Type | Description |
|-----------|------------|-----------|-------------|
| Plan outcomes | CWM-A | `Fact` | "Plan X succeeded" |
| Reflections | CWM-E | `PersonaEntry` | "This was challenging" |
| Emotions | CWM-E | `EmotionState` | "Confident about result" |
| Learned rules | CWM-A | `Rule` | "Use slow speed for fragile" |

### Knowledge Base

External knowledge sources:

| Data Type | Target CWM | Node Type | Description |
|-----------|------------|-----------|-------------|
| Commonsense KB | CWM-A | `Fact` (canonical) | "Water is wet" |
| Domain ontology | CWM-A | `Concept`, `Rule` | Pick-and-place rules |
| Task templates | CWM-A | `Abstraction` | "Mail a letter" workflow |

### Human Feedback

Human-in-the-loop corrections:

| Data Type | Target CWM | Node Type | Description |
|-----------|------------|-----------|-------------|
| Corrections | CWM-A | `Fact` | "Actually, that was wrong" |
| Preferences | CWM-E | `Preference` | "I prefer careful handling" |
| Annotations | CWM-A | `Association` | "These concepts are related" |
| Approvals | CWM-A | (promotion) | Promote hypothesis to canonical |

## Flow Diagrams

### Perception → CWM-G → CWM-A Flow

```
┌─────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────┐
│  Camera │ ──► │ JEPA Encoder    │ ──► │ PerceptionFrame │ ──► │ Milvus   │
│  Frame  │     │ (embedding)     │     │ (CWM-G)         │     │ (index)  │
└─────────┘     └─────────────────┘     └────────┬────────┘     └──────────┘
                                                 │
                       ┌─────────────────────────┘
                       │
                       ▼
               ┌───────────────────┐     ┌───────────────────┐
               │ JEPA Predictor    │ ──► │ ImaginedProcess   │
               │ (simulation)      │     │ (CWM-G)           │
               └───────────────────┘     └─────────┬─────────┘
                                                   │
                       ┌───────────────────────────┘
                       │
                       ▼
               ┌───────────────────┐     ┌───────────────────┐
               │ ImaginedState     │ ──► │ Fact (hypothesis) │
               │ (sequence)        │     │ (CWM-A)           │
               └───────────────────┘     └───────────────────┘
                       │                           │
                       │       validation          │
                       │     ┌─────────────────────┘
                       │     │
                       ▼     ▼
               ┌───────────────────┐
               │ Fact (canonical)  │
               │ (promoted)        │
               └───────────────────┘
```

### Diary Reflection → CWM-E → CWM-A Flow

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Sophia    │ ──► │ Persona Module  │ ──► │ PersonaEntry    │
│ (plan done) │     │ (reflection)    │     │ (CWM-E)         │
└─────────────┘     └─────────────────┘     └────────┬────────┘
                                                     │
                       ┌─────────────────────────────┘
                       │
                       ▼
               ┌───────────────────┐     ┌───────────────────┐
               │ Emotion Analysis  │ ──► │ EmotionState      │
               │ (sentiment)       │     │ (CWM-E)           │
               └───────────────────┘     └─────────┬─────────┘
                                                   │
                       ┌───────────────────────────┘
                       │
                       ▼
               ┌───────────────────┐     ┌───────────────────┐
               │ Pattern Detector  │ ──► │ Preference        │
               │ (learning)        │     │ (CWM-E)           │
               └───────────────────┘     └─────────┬─────────┘
                                                   │
                       ┌───────────────────────────┘
                       │
                       ▼
               ┌───────────────────┐
               │ Association/Fact  │
               │ (CWM-A)           │
               └───────────────────┘
```

## CWM-A Ingestion

### Fact Ingestion

```python
# POST /api/v1/cwm/facts
{
    "subject": "block_a",
    "predicate": "is_on",
    "object": "table_1",
    "confidence": 0.85,
    "source": "jepa-detector",
    "source_type": "observation"
}
```

**Validation Rules:**
- Subject, predicate, object must be non-empty strings
- Confidence must be in [0.0, 1.0]
- Source type must be: `knowledge_base`, `observation`, `inference`, `human`
- Status defaults to `hypothesis` unless confidence > 0.9 from trusted source

**Conflict Detection:**
```cypher
// Check for contradicting facts
MATCH (existing:Fact)
WHERE existing.subject = $subject
  AND existing.predicate = $predicate
  AND existing.status = 'canonical'
  AND existing.object <> $object
RETURN existing
```

### Rule Ingestion

```python
# POST /api/v1/cwm/rules
{
    "name": "FragileHandling",
    "condition": "object.fragile == true",
    "consequent": "action.force <= 2.0",
    "rule_type": "constraint",
    "priority": 10,
    "domain": "manipulation"
}
```

**Validation Rules:**
- Name must be unique within domain
- Condition and consequent must be valid expressions
- Rule type must be: `constraint`, `preference`, `inference`, `default`
- Priority must be non-negative integer

### Association Ingestion

```python
# POST /api/v1/cwm/associations
{
    "source_concept": "coffee",
    "target_concept": "morning",
    "relationship_type": "temporal",
    "strength": 0.8,
    "context": "daily_routine"
}
```

**Validation Rules:**
- Source and target concepts must exist in graph
- Strength must be in [0.0, 1.0]
- Bidirectional relationships create two edges

## CWM-G Ingestion

### PerceptionFrame Ingestion

```python
# POST /api/v1/cwm/perception
{
    "timestamp": "2024-01-15T10:30:00Z",
    "format": "jepa_v1",
    "embedding": [0.1, 0.2, ...],  # 768-dim vector
    "detected_objects": [
        {"label": "block", "bbox": [100, 200, 50, 50], "confidence": 0.95}
    ],
    "source_modality": "camera",
    "camera_id": "cam_01"
}
```

**Processing Steps:**
1. Validate embedding dimensions match model config
2. Store frame in Neo4j with metadata
3. Index embedding in Milvus
4. Optionally trigger JEPA simulation if novel

### ImaginedProcess Ingestion

```python
# POST /api/v1/cwm/imagination
{
    "capability_id": "grasp",
    "trigger_frame_id": "frame-12345",
    "horizon": 10,
    "states": [
        {"step": 0, "embedding": [...], "confidence": 0.95},
        {"step": 1, "embedding": [...], "confidence": 0.90},
        # ... up to horizon
    ]
}
```

**Processing Steps:**
1. Create `ImaginedProcess` linked to trigger frame
2. Create `ImaginedState` sequence with `PRECEDES` relationships
3. Index all embeddings in Milvus
4. Extract high-confidence predictions as hypothesis facts

## CWM-E Ingestion

### PersonaEntry Ingestion

```python
# POST /api/v1/cwm/diary
{
    "summary": "Successfully completed block stacking task",
    "sentiment": "confident",
    "related_process_id": "process-67890",
    "detail": "The approach worked well on first try",
    "lessons": ["parallel approach saves time"]
}
```

**Processing Steps:**
1. Create `PersonaEntry` with timestamp
2. Link to related `Process` if specified
3. Extract emotion signals for `EmotionState` creation
4. Update preference patterns based on sentiment

### EmotionState Ingestion

```python
# POST /api/v1/cwm/emotions
{
    "emotion_type": "curious",
    "intensity": 0.7,
    "context": "novel object encountered",
    "source": "perception",
    "target_id": "entity-novel-block"
}
```

**Processing Steps:**
1. Create `EmotionState` node
2. Create `TAGGED_ON` relationship to target entity/process
3. If derived from diary, create `GENERATED_BY` link to `PersonaEntry`
4. Update running emotional state for persona

### Preference Learning

Preferences are learned from patterns in PersonaEntry and EmotionState:

```python
# Automatic preference extraction
{
    "context": "fragile_objects",
    "preference": "cautious_handling",
    "strength": 0.85,
    "evidence_count": 5,
    "source_entries": ["persona-1", "persona-2", ...]
}
```

## Cross-CWM Promotion

### Hypothesis to Canonical Promotion

CWM nodes start as hypotheses and can be promoted:

```python
# POST /api/v1/cwm/promote
{
    "node_id": "fact-12345",
    "promotion_type": "canonical",
    "evidence": ["frame-001", "frame-002", "persona-003"],
    "confidence_update": 0.95,
    "reviewer": "auto"  # or human username
}
```

**Promotion Criteria:**
1. **Confidence Threshold**: confidence >= 0.8
2. **Supporting Evidence**: >= 3 supporting observations
3. **No Contradictions**: No canonical facts with same subject/predicate
4. **Temporal Stability**: Observed consistently over time window

### Cross-CWM Derivation

Nodes in one CWM can derive nodes in another:

| Source | Target | Example |
|--------|--------|---------|
| CWM-G `ImaginedState` | CWM-A `Fact` | "Block will fall" → "Block at position X" |
| CWM-E `Preference` | CWM-A `Rule` | "Prefer careful" → "IF fragile THEN slow" |
| CWM-A `Fact` | CWM-E `EmotionState` | "Task failed" → "frustrated" |
| CWM-G `PerceptionFrame` | CWM-E `EmotionState` | "Novel object" → "curious" |

## API Endpoints

### Fact Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cwm/facts` | Create fact |
| GET | `/api/v1/cwm/facts/{id}` | Get fact |
| PATCH | `/api/v1/cwm/facts/{id}` | Update fact |
| DELETE | `/api/v1/cwm/facts/{id}` | Deprecate fact |
| GET | `/api/v1/cwm/facts/search` | Search facts |

### Perception Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cwm/perception` | Ingest frame |
| GET | `/api/v1/cwm/perception/{id}` | Get frame |
| POST | `/api/v1/cwm/perception/search` | Semantic search |

### Imagination Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cwm/imagination` | Create simulation |
| GET | `/api/v1/cwm/imagination/{id}` | Get simulation |
| GET | `/api/v1/cwm/imagination/{id}/states` | Get state sequence |

### Diary Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cwm/diary` | Create entry |
| GET | `/api/v1/cwm/diary` | List entries |
| GET | `/api/v1/cwm/diary/{id}` | Get entry |

### Emotion Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cwm/emotions` | Create emotion |
| GET | `/api/v1/cwm/emotions/current` | Get current state |
| GET | `/api/v1/cwm/emotions/history` | Get history |

### Promotion Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cwm/promote` | Promote node |
| GET | `/api/v1/cwm/promote/pending` | Get pending promotions |

## Error Handling

### Validation Errors

```python
# 400 Bad Request
{
    "error": "validation_error",
    "details": [
        {"field": "confidence", "message": "must be between 0.0 and 1.0"},
        {"field": "subject", "message": "cannot be empty"}
    ]
}
```

### Conflict Errors

```python
# 409 Conflict
{
    "error": "conflict",
    "conflicting_node": "fact-existing-123",
    "message": "Contradicts canonical fact: block_a is_on table_2",
    "resolution_options": [
        "supersede",  # Mark old as deprecated, new as canonical
        "hypothesis", # Keep new as hypothesis for review
        "reject"      # Reject new fact
    ]
}
```

### Rate Limiting

```python
# 429 Too Many Requests
{
    "error": "rate_limit",
    "message": "Ingestion rate limit exceeded",
    "retry_after": 5  # seconds
}
```

## See Also

- [CWM State Overview](./CWM_STATE.md) - High-level CWM architecture
- [CWM-A Schema](./CWM_A.md) - Abstract world model nodes
- [CWM-G Schema](./CWM_G.md) - Generative world model nodes
- [CWM-E Schema](./CWM_E.md) - Emotional world model nodes
- [HCG Data Layer](../HCG_DATA_LAYER.md) - Core ontology and queries
