# CWM-A: Abstract World Model

CWM-A stores symbolic knowledge for commonsense reasoning, declarative facts,
and abstract associations. It enables Sophia to reason about the world using
structured knowledge rather than learned dynamics.

## Table of Contents

- [Overview](#overview)
- [Node Types](#node-types)
- [Relationships](#relationships)
- [Properties Reference](#properties-reference)
- [Query Patterns](#query-patterns)
- [Examples](#examples)

## Overview

CWM-A provides the symbolic backbone for planning:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CWM-A                                   │
├─────────────────────────────────────────────────────────────────┤
│  Facts            Associations         Rules                    │
│  ┌──────┐         ┌──────────┐        ┌──────────┐             │
│  │ Fact │◄───────►│  Assoc   │◄──────►│   Rule   │             │
│  └──┬───┘         └────┬─────┘        └────┬─────┘             │
│     │                  │                   │                    │
│     ▼                  ▼                   ▼                    │
│  ┌──────────────────────────────────────────────┐              │
│  │              Abstraction                      │              │
│  │         (higher-order concepts)               │              │
│  └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases

1. **Human Workflow Planning**: "To mail a letter, I need stamps and a mailbox"
2. **Commonsense Inference**: "Fragile objects require careful handling"
3. **Goal Decomposition**: "Clean room = vacuum + dust + organize"
4. **Constraint Reasoning**: "Heavy objects require both hands"

## Node Types

### Fact

Represents a declarative statement about the world.

```cypher
CREATE (f:Fact {
    uuid: 'fact-mailbox-accepts-letters',
    subject: 'mailbox',
    predicate: 'accepts',
    object: 'stamped_letter',
    confidence: 0.95,
    status: 'canonical',
    source: 'commonsense-kb',
    source_type: 'knowledge_base',
    valid_from: datetime(),
    valid_until: null,
    created_at: datetime(),
    updated_at: datetime()
})
```

**Status Values:**
- `hypothesis`: Unverified, low confidence
- `proposed`: Validated, pending integration
- `canonical`: Stable, used in planning
- `deprecated`: Superseded or invalidated

### Association

Represents a weighted link between concepts.

```cypher
CREATE (a:Association {
    uuid: 'assoc-coffee-morning',
    source_concept: 'coffee',
    target_concept: 'morning',
    relationship_type: 'temporal_co-occurrence',
    strength: 0.85,
    bidirectional: false,
    context: 'daily_routine',
    source: 'observation',
    created_at: datetime()
})
```

### Abstraction

Represents a higher-order concept or generalization.

```cypher
CREATE (abs:Abstraction {
    uuid: 'abs-grasping-requirements',
    name: 'GraspingRequirements',
    description: 'Conditions required for successful object grasping',
    level: 2,  // abstraction hierarchy level
    domain: 'manipulation',
    created_at: datetime()
})
```

### Rule

Represents a conditional inference rule.

```cypher
CREATE (r:Rule {
    uuid: 'rule-fragile-handling',
    name: 'FragileObjectHandling',
    condition: 'object.property.fragile = true',
    consequent: 'action.parameter.force <= 5.0',
    rule_type: 'constraint',
    priority: 10,
    confidence: 0.99,
    domain: 'manipulation',
    created_at: datetime()
})
```

**Rule Types:**
- `constraint`: Must be satisfied
- `preference`: Should be satisfied if possible
- `inference`: Derives new facts
- `default`: Applied unless overridden

## Relationships

### Fact Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `ABOUT` | Concept/Entity | Fact concerns this node |
| `SUPPORTS` | Process/Plan | Fact supports this action |
| `CONTRADICTS` | Fact | Facts in conflict |
| `SUPERSEDES` | Fact | Newer fact replaces older |
| `DERIVED_FROM` | Fact/PerceptionFrame | Provenance |
| `INFERRED_FROM` | Fact+ | Derived via inference |

### Association Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `CONNECTS` | Concept (x2) | The two concepts linked |
| `CONTEXT` | Concept | Context for association |
| `LEARNED_FROM` | Process | How association was learned |

### Abstraction Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `GENERALIZES` | Concept+ | Lower-level concepts |
| `PART_OF` | Abstraction | Hierarchy |
| `APPLIES_TO` | Domain | Where abstraction is valid |

### Rule Relationships

| Relationship | Target | Description |
|--------------|--------|-------------|
| `APPLIES_TO` | Concept/Entity | Rule scope |
| `TRIGGERS` | Rule | Chained rules |
| `CONFLICTS_WITH` | Rule | Mutually exclusive rules |

## Properties Reference

### Fact Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `fact-` |
| `subject` | string | ✓ | Subject of the statement |
| `predicate` | string | ✓ | Relationship/property |
| `object` | string | ✓ | Object/value |
| `confidence` | decimal | ✓ | 0.0-1.0 |
| `status` | enum | ✓ | hypothesis/proposed/canonical/deprecated |
| `source` | string | | Where fact came from |
| `source_type` | enum | | knowledge_base/observation/inference/human |
| `valid_from` | datetime | | Temporal validity start |
| `valid_until` | datetime | | Temporal validity end |
| `domain` | string | | Knowledge domain |
| `created_at` | datetime | | Creation timestamp |
| `updated_at` | datetime | | Last modification |

### Association Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `assoc-` |
| `source_concept` | string | ✓ | Origin concept |
| `target_concept` | string | ✓ | Target concept |
| `relationship_type` | string | | Type of association |
| `strength` | decimal | ✓ | 0.0-1.0 |
| `bidirectional` | boolean | | Is relationship symmetric |
| `context` | string | | Context where valid |
| `source` | string | | How learned |
| `decay_rate` | decimal | | Strength decay per day |

### Abstraction Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `abs-` |
| `name` | string | ✓ | Unique name |
| `description` | string | | Human description |
| `level` | integer | | Hierarchy level (0=concrete) |
| `domain` | string | | Knowledge domain |

### Rule Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, prefix `rule-` |
| `name` | string | ✓ | Rule name |
| `condition` | string | ✓ | Condition expression |
| `consequent` | string | ✓ | Consequent expression |
| `rule_type` | enum | ✓ | constraint/preference/inference/default |
| `priority` | integer | | Higher = more important |
| `confidence` | decimal | | Rule reliability |
| `domain` | string | | Applicable domain |

## Query Patterns

### Find Facts for Planning

```cypher
// Find facts that support a goal
MATCH (f:Fact)-[:ABOUT]->(c:Concept {name: $goal_concept})
WHERE f.status = 'canonical'
  AND f.confidence >= 0.8
RETURN f
ORDER BY f.confidence DESC
```

### Find Related Concepts via Association

```cypher
// Find concepts associated with a given concept
MATCH (a:Association)
WHERE a.source_concept = $concept OR a.target_concept = $concept
RETURN a
ORDER BY a.strength DESC
LIMIT 10
```

### Find Applicable Rules

```cypher
// Find rules that apply to an entity type
MATCH (r:Rule)-[:APPLIES_TO]->(c:Concept {name: $entity_type})
WHERE r.rule_type IN ['constraint', 'preference']
RETURN r
ORDER BY r.priority DESC
```

### Traverse Abstraction Hierarchy

```cypher
// Find all abstractions for a concept
MATCH path = (c:Concept {name: $concept})<-[:GENERALIZES*]-(abs:Abstraction)
RETURN path
```

## Examples

### Human Workflow: Mail a Letter

```cypher
// Facts about mailing
CREATE (f1:Fact {
    uuid: 'fact-letter-needs-stamp',
    subject: 'letter',
    predicate: 'requires',
    object: 'postage_stamp',
    confidence: 0.99,
    status: 'canonical',
    source: 'commonsense-kb'
})

CREATE (f2:Fact {
    uuid: 'fact-mailbox-location',
    subject: 'mailbox',
    predicate: 'located_at',
    object: 'street_corner',
    confidence: 0.9,
    status: 'canonical'
})

CREATE (f3:Fact {
    uuid: 'fact-post-office-hours',
    subject: 'post_office',
    predicate: 'open_during',
    object: '9am-5pm_weekdays',
    confidence: 0.95,
    status: 'canonical'
})

// Rule for mailing
CREATE (r:Rule {
    uuid: 'rule-mail-requires-postage',
    name: 'MailRequiresPostage',
    condition: 'goal.type = "mail_letter"',
    consequent: 'require(postage_stamp)',
    rule_type: 'constraint',
    priority: 10
})
```

### Manipulation Domain: Grasping

```cypher
// Abstraction for grasping
CREATE (abs:Abstraction {
    uuid: 'abs-grasp-preconditions',
    name: 'GraspPreconditions',
    description: 'Conditions for successful grasping',
    level: 1,
    domain: 'manipulation'
})

// Rules under this abstraction
CREATE (r1:Rule {
    uuid: 'rule-clear-approach',
    name: 'ClearApproachPath',
    condition: 'action.type = "grasp"',
    consequent: 'check(approach_path.clear)',
    rule_type: 'constraint'
})-[:PART_OF]->(abs)

CREATE (r2:Rule {
    uuid: 'rule-gripper-width',
    name: 'GripperWidthConstraint',
    condition: 'action.type = "grasp"',
    consequent: 'gripper.width > object.width',
    rule_type: 'constraint'
})-[:PART_OF]->(abs)
```

## See Also

- [CWM State Overview](./CWM_STATE.md) - High-level CWM architecture
- [CWM-G Schema](./CWM_G.md) - Generative world model
- [CWM-E Schema](./CWM_E.md) - Emotional world model
- [Ingestion Flows](./INGESTION.md) - How data enters CWM-A
