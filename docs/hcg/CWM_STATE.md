# Causal World Model (CWM) Specification

The Causal World Model is LOGOS's unified representation of the world, combining
symbolic knowledge, learned dynamics, and emotional context. It consists of three
interconnected subsystems stored in the Hybrid Cognitive Graph (HCG).

## Table of Contents

- [Overview](#overview)
- [CWM Subsystems](#cwm-subsystems)
- [Node Types Reference](#node-types-reference)
- [Relationships](#relationships)
- [Lifecycle & Promotion](#lifecycle--promotion)
- [See Also](#see-also)

## Overview

The CWM provides Sophia with a rich, multi-modal understanding of the world:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Causal World Model (CWM)                     │
├─────────────────────┬─────────────────────┬─────────────────────┤
│      CWM-A          │       CWM-G         │       CWM-E         │
│    (Abstract)       │    (Generative)     │    (Emotional)      │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ • Symbolic facts    │ • JEPA predictions  │ • Emotion tags      │
│ • Associations      │ • Imagined states   │ • Persona diary     │
│ • Commonsense KB    │ • Perception frames │ • Reflection logs   │
│ • Declarative rules │ • Latent dynamics   │ • Sentiment context │
└─────────────────────┴─────────────────────┴─────────────────────┘
         │                     │                     │
         └──────────────┬──────┴─────────────────────┘
                        │
              ┌─────────▼─────────┐
              │  Sophia Planner   │
              │ (unified queries) │
              └───────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each subsystem handles a distinct cognitive function
2. **Unified Query Interface**: Sophia queries all three through the HCG
3. **Provenance Tracking**: All CWM nodes track their source and confidence
4. **Promotion Pipeline**: Hypotheses can be promoted to canonical facts
5. **Temporal Awareness**: All nodes are timestamped for state reconstruction

## CWM Subsystems

### CWM-A: Abstract/Associative World Model

CWM-A stores symbolic knowledge for commonsense reasoning:

| Purpose | Node Types | Example |
|---------|------------|---------|
| Declarative facts | `Fact` | "Mailboxes accept stamped letters" |
| Associations | `Association` | "Coffee → morning → productivity" |
| Abstractions | `Abstraction` | "Grasping requires clear approach path" |
| Commonsense rules | `Rule` | "IF object.fragile THEN handle.gently" |

**Use Cases:**
- Planning human workflows ("mail a letter")
- Commonsense inference during plan generation
- Abstract goal decomposition

See: [CWM-A Schema Reference](./CWM_A.md)

### CWM-G: Generative/Grounded World Model

CWM-G stores learned dynamics and predictions from JEPA:

| Purpose | Node Types | Example |
|---------|------------|---------|
| Perception | `PerceptionFrame` | Video frame with detected objects |
| Predictions | `ImaginedProcess` | JEPA rollout of pick action |
| Future states | `ImaginedState` | Predicted block position at t+5 |

**Use Cases:**
- Physics-based prediction
- Visual imagination for planning
- Action feasibility assessment

See: [CWM-G Schema Reference](./CWM_G.md)

### CWM-E: Emotional/Experiential World Model

CWM-E stores emotional context and persona reflection:

| Purpose | Node Types | Example |
|---------|------------|---------|
| Emotion tags | `EmotionState` | "curious" about novel object |
| Diary entries | `PersonaEntry` | "Successfully stacked 3 blocks" |
| Preferences | `Preference` | "Prefer cautious approach for fragile items" |

**Use Cases:**
- Persona-aware responses
- Emotional state tracking
- Learning from experience

See: [CWM-E Schema Reference](./CWM_E.md)

## Node Types Reference

### Quick Reference Table

| Node Type | CWM | UUID Prefix | Required Fields |
|-----------|-----|-------------|-----------------|
| `Fact` | A | `fact-` | uuid, subject, predicate, object, confidence |
| `Association` | A | `assoc-` | uuid, source_concept, target_concept, strength |
| `Abstraction` | A | `abs-` | uuid, name, description |
| `Rule` | A | `rule-` | uuid, condition, consequent |
| `PerceptionFrame` | G | `frame-` | uuid, timestamp, format |
| `ImaginedProcess` | G | `imgproc-` | uuid, timestamp, capability_id, horizon |
| `ImaginedState` | G | `imgstate-` | uuid, timestamp, step, confidence |
| `EmotionState` | E | `emotion-` | uuid, timestamp, emotion_type, intensity |
| `PersonaEntry` | E | `persona-` | uuid, timestamp, summary |
| `Preference` | E | `pref-` | uuid, context, preference, strength |

## Relationships

### Cross-CWM Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `SUPPORTS` | Fact | Process | Fact supports plan step |
| `CONTRADICTS` | Fact | Fact | Facts in conflict |
| `TRIGGERED_BY` | ImaginedProcess | PerceptionFrame | Perception triggered simulation |
| `PREDICTS` | ImaginedProcess | ImaginedState | Process predicts state |
| `REFLECTS_ON` | PersonaEntry | Process | Diary entry about process |
| `TAGGED_ON` | EmotionState | Entity/Process | Emotion associated with node |
| `INFLUENCED_BY` | Preference | EmotionState | Preference shaped by emotion |

### Provenance Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `DERIVED_FROM` | Fact | PerceptionFrame | Fact learned from perception |
| `INFERRED_FROM` | Fact | Fact | Fact inferred from other facts |
| `PROMOTED_FROM` | Fact | ImaginedState | Hypothesis promoted to fact |
| `GENERATED_BY` | EmotionState | PersonaEntry | Emotion from reflection |

## Lifecycle & Promotion

### Hypothesis → Canonical Knowledge

CWM nodes start as hypotheses and can be promoted to canonical facts:

```
┌──────────────┐     validation     ┌──────────────┐     approval     ┌──────────────┐
│  Hypothesis  │ ─────────────────► │   Proposed   │ ────────────────► │  Canonical   │
│ (confidence  │                    │ (validated,  │                   │   (stable,   │
│   < 0.5)     │                    │  reviewed)   │                   │  integrated) │
└──────────────┘                    └──────────────┘                   └──────────────┘
       ▲                                   │                                  │
       │                                   │                                  │
       └───────────────────────────────────┴──────────────────────────────────┘
                                     rejection/decay
```

**Status Field Values:**
- `hypothesis`: Low-confidence, needs validation
- `proposed`: Validated, awaiting integration
- `canonical`: Stable knowledge, used in planning
- `deprecated`: Superseded or invalidated

**Promotion Criteria:**
1. Confidence threshold (e.g., > 0.8)
2. Consistency check against existing facts
3. Source reliability assessment
4. Optional human review for critical facts

### Decay & Garbage Collection

- Hypotheses with confidence < 0.1 are pruned after 24h
- Deprecated facts are archived after 30 days
- Imagined states older than 7 days are summarized and pruned

## See Also

- [CWM-A Schema Reference](./CWM_A.md) - Abstract world model details
- [CWM-G Schema Reference](./CWM_G.md) - Generative world model details
- [CWM-E Schema Reference](./CWM_E.md) - Emotional world model details
- [HCG Data Layer](../HCG_DATA_LAYER.md) - Core ontology and queries
- [Ingestion Flows](./INGESTION.md) - How data enters the CWM
