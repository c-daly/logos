# CWM-E: Emotional/Experiential World Model

CWM-E stores emotional context, persona reflection, and learned preferences.
It enables Sophia to maintain a consistent persona, learn from experience,
and incorporate emotional valence into planning and communication.

## Table of Contents

- [Overview](#overview)
- [Node Types](#node-types)
- [Relationships](#relationships)
- [Properties Reference](#properties-reference)
- [Persona Integration](#persona-integration)
- [Query Patterns](#query-patterns)
- [Examples](#examples)

## Overview

CWM-E provides emotional and experiential grounding:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CWM-E                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────────┐                    │
│  │   Process    │      │    EmotionState  │                    │
│  │  (action)    │◄────►│   (tagged on)    │                    │
│  └──────────────┘      └────────┬─────────┘                    │
│         │                       │                               │
│         ▼                       ▼                               │
│  ┌──────────────┐      ┌──────────────────┐                    │
│  │ PersonaEntry │◄─────│   GENERATED_BY   │                    │
│  │   (diary)    │      └──────────────────┘                    │
│  └──────┬───────┘                                              │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                              │
│  │  Preference  │                                              │
│  │  (learned)   │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases

1. **Persona-Aware Responses**: "I prefer careful handling of fragile items"
2. **Emotional State Tracking**: "I'm curious about this novel object"
3. **Experience Learning**: "Last time this approach worked well"
4. **Preference Formation**: "I find this task sequence efficient"

## Node Types

### EmotionState

Represents an emotional tag associated with an entity, process, or situation.

```cypher
CREATE (es:EmotionState {
    uuid: 'emotion-curious-novel-object-001',
    timestamp: datetime(),
    emotion_type: 'curious',
    intensity: 0.8,
    valence: 0.6,  // positive
    arousal: 0.7,  // moderately aroused
    context: 'Encountered unfamiliar object type',
    source: 'novelty_detection',
    duration_ms: 30000,
    created_at: datetime()
})
```

**Emotion Types:**
- Cognitive: `curious`, `confused`, `focused`, `distracted`
- Confidence: `confident`, `uncertain`, `cautious`
- Social: `helpful`, `patient`, `collaborative`
- Task-related: `satisfied`, `frustrated`, `determined`

### PersonaEntry

Represents a diary entry summarizing activity and reflection.

```cypher
CREATE (pe:PersonaEntry {
    uuid: 'persona-20251201-afternoon-001',
    timestamp: datetime(),
    summary: 'Successfully completed 5 pick-and-place tasks with 100% accuracy',
    sentiment: 'confident',
    activity_type: 'manipulation',
    duration_ms: 3600000,
    success_count: 5,
    failure_count: 0,
    notable_events: '["First time handling glass object", "New user interaction"]',
    reflection: 'The careful approach for fragile items is effective',
    created_at: datetime()
})
```

### Preference

Represents a learned preference derived from experience.

```cypher
CREATE (pref:Preference {
    uuid: 'pref-fragile-handling-001',
    context: 'manipulation.fragile_objects',
    preference: 'approach.cautious',
    strength: 0.85,
    formation_type: 'experience',  // experience, instruction, default
    evidence_count: 12,
    last_reinforced: datetime(),
    created_at: datetime()
})
```

## Relationships

### EmotionState Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `TAGGED_ON` | Entity/Process | What the emotion is about |
| `TRIGGERED_BY` | Event/State | What caused the emotion |
| `GENERATED_BY` | PersonaEntry | Derived from reflection |
| `INFLUENCES` | Preference | Shapes preferences |

### PersonaEntry Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `RELATES_TO` | Process | Activity being reflected on |
| `MENTIONS` | Entity | Entities involved |
| `EXPRESSES` | EmotionState | Emotions in this entry |
| `FORMS` | Preference | Preferences derived |
| `FOLLOWS` | PersonaEntry | Sequential diary entries |

### Preference Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `APPLIES_TO` | Concept/Context | Where preference applies |
| `INFLUENCED_BY` | EmotionState+ | Emotions that shaped it |
| `DERIVED_FROM` | PersonaEntry+ | Experience basis |
| `OVERRIDES` | Preference | Newer preference supersedes |

## Properties Reference

### EmotionState Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `emotion-` |
| `timestamp` | datetime | ✓ | When emotion occurred |
| `emotion_type` | string | ✓ | Type (curious, confident, etc.) |
| `intensity` | decimal | ✓ | 0.0-1.0 strength |
| `valence` | decimal | | -1.0 (negative) to 1.0 (positive) |
| `arousal` | decimal | | 0.0 (calm) to 1.0 (excited) |
| `context` | string | | Situation description |
| `source` | string | | What triggered emotion |
| `duration_ms` | integer | | How long it lasted |

### PersonaEntry Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `persona-` |
| `timestamp` | datetime | ✓ | Entry creation time |
| `summary` | string | ✓ | Activity summary |
| `sentiment` | string | | Overall sentiment |
| `activity_type` | string | | Category of activity |
| `duration_ms` | integer | | Activity duration |
| `success_count` | integer | | Successful actions |
| `failure_count` | integer | | Failed actions |
| `notable_events` | JSON | | Significant occurrences |
| `reflection` | string | | Self-reflection text |

### Preference Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `pref-` |
| `context` | string | ✓ | Where preference applies |
| `preference` | string | ✓ | The preferred option/approach |
| `strength` | decimal | ✓ | 0.0-1.0 preference strength |
| `formation_type` | enum | | experience/instruction/default |
| `evidence_count` | integer | | Supporting experiences |
| `last_reinforced` | datetime | | Last confirmation |

## Persona Integration

### Emotion Detection Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Process/Event   │───►│ Emotion Engine  │───►│  EmotionState   │
│  (trigger)      │    │  (detection)    │    │   (tagged)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Diary Generation Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Activity Log    │───►│ LLM Summarizer  │───►│  PersonaEntry   │
│ (processes)     │    │  (reflection)   │    │   (diary)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Preference    │
                       │  (extraction)   │
                       └─────────────────┘
```

### Emotion Types Reference

| Category | Types | Valence | Arousal |
|----------|-------|---------|---------|
| Cognitive | curious, confused, focused, distracted | varies | medium-high |
| Confidence | confident, uncertain, cautious | positive/neutral | medium |
| Social | helpful, patient, collaborative | positive | medium |
| Task | satisfied, frustrated, determined | varies | varies |
| Novel | surprised, intrigued, skeptical | neutral | high |

## Query Patterns

### Get Current Emotional State

```cypher
// Find most recent emotions
MATCH (es:EmotionState)
WHERE es.timestamp > datetime() - duration('PT5M')
RETURN es
ORDER BY es.timestamp DESC
LIMIT 5
```

### Find Emotions for Entity

```cypher
// Get emotion history for an entity
MATCH (es:EmotionState)-[:TAGGED_ON]->(e:Entity {uuid: $entity_uuid})
RETURN es
ORDER BY es.timestamp DESC
LIMIT 20
```

### Get Persona Diary

```cypher
// Recent diary entries
MATCH (pe:PersonaEntry)
WHERE pe.timestamp > datetime() - duration('P7D')
RETURN pe
ORDER BY pe.timestamp DESC
```

### Find Preferences for Context

```cypher
// Get applicable preferences
MATCH (pref:Preference)
WHERE pref.context STARTS WITH $context_prefix
  AND pref.strength >= 0.5
RETURN pref
ORDER BY pref.strength DESC
```

### Trace Preference Formation

```cypher
// How was a preference formed?
MATCH (pref:Preference {uuid: $pref_uuid})
OPTIONAL MATCH (pref)<-[:FORMS]-(pe:PersonaEntry)
OPTIONAL MATCH (pref)<-[:INFLUENCES]-(es:EmotionState)
RETURN pref, collect(DISTINCT pe) as diary_entries, 
       collect(DISTINCT es) as emotions
```

## Examples

### Handling a Novel Object

```cypher
// Detect curiosity about novel object
CREATE (es:EmotionState {
    uuid: 'emotion-curious-glass-vase',
    timestamp: datetime(),
    emotion_type: 'curious',
    intensity: 0.7,
    valence: 0.5,
    arousal: 0.6,
    context: 'First encounter with glass vase',
    source: 'novelty_detection'
})

// Tag on the entity
MATCH (e:Entity {uuid: 'entity-glass-vase-001'})
CREATE (es)-[:TAGGED_ON]->(e)

// Also tag cautious due to fragility
CREATE (es2:EmotionState {
    uuid: 'emotion-cautious-glass-vase',
    timestamp: datetime(),
    emotion_type: 'cautious',
    intensity: 0.8,
    valence: 0.3,
    arousal: 0.4,
    context: 'Glass object detected as fragile',
    source: 'material_classification'
})

CREATE (es2)-[:TAGGED_ON]->(e)
```

### End of Day Diary Entry

```cypher
// Create diary entry
CREATE (pe:PersonaEntry {
    uuid: 'persona-20251201-eod',
    timestamp: datetime(),
    summary: 'Completed 8 manipulation tasks including first glass object handling',
    sentiment: 'satisfied',
    activity_type: 'manipulation',
    duration_ms: 28800000,
    success_count: 8,
    failure_count: 0,
    notable_events: '["First glass object", "New cautious grip learned"]',
    reflection: 'The extra caution for glass objects was worthwhile. I should apply similar care to ceramic items.'
})

// Link to relevant processes
MATCH (p:Process) 
WHERE p.start_time > datetime() - duration('P1D')
CREATE (pe)-[:RELATES_TO]->(p)

// Express learned preference
CREATE (pref:Preference {
    uuid: 'pref-glass-handling-001',
    context: 'manipulation.material.glass',
    preference: 'grip.force.reduced',
    strength: 0.75,
    formation_type: 'experience',
    evidence_count: 1
})

CREATE (pe)-[:FORMS]->(pref)
```

### Preference Reinforcement

```cypher
// Reinforce existing preference after successful use
MATCH (pref:Preference {uuid: 'pref-glass-handling-001'})
SET pref.evidence_count = pref.evidence_count + 1,
    pref.strength = CASE 
        WHEN pref.strength < 0.95 THEN pref.strength + 0.05
        ELSE pref.strength
    END,
    pref.last_reinforced = datetime()
RETURN pref
```

### Emotional Influence on Response

```cypher
// Get emotional context for response generation
MATCH (es:EmotionState)
WHERE es.timestamp > datetime() - duration('PT5M')
WITH es ORDER BY es.intensity DESC LIMIT 3
WITH collect(es) as recent_emotions

MATCH (pref:Preference)
WHERE pref.context = $current_context
  AND pref.strength >= 0.5
WITH recent_emotions, collect(pref) as preferences

RETURN recent_emotions, preferences
```

## See Also

- [CWM State Overview](./CWM_STATE.md) - High-level CWM architecture
- [CWM-A Schema](./CWM_A.md) - Abstract world model
- [CWM-G Schema](./CWM_G.md) - Generative world model
- [Persona Diary](../../apollo/docs/PERSONA_DIARY.md) - Apollo UI integration
- [Ingestion Flows](./INGESTION.md) - How data enters CWM-E
