# Intake Summary: Ontology Refactor

## What
Refactor LOGOS ontology from 15 rigid schema-typed node labels to a flexible structure-typed approach with a single `Node` label, `type` property, `root_type` property, and `IS_A` edges forming a type hierarchy.

## Why
- Enable Sophia to create/modify node types AND edge types without code changes
- Align with TinyMind lessons (simpler, more flexible design)
- Make ontology self-describing and self-evolving
- Layered validation: SHACL for graph structure, JSON Schema for content

## Key Design Points

### 1. Type System
- **`type` property (required)**: Immediate type of the node
- **`IS_A` edge**: Links to parent type node, forming hierarchy
- **`root_type` property**: First ancestor whose parent is `type_definition` (computed at creation)
- **Type definitions are nodes**: `type: "type_definition"` with `json_schema` property

### 2. Type Hierarchy
```
type_definition  ← meta level
  ├── concept    ← root level (root_type candidates)
  │     └── philosophical_concept
  │           └── nihilism {type: "philosophical_concept", root_type: "concept"}
  ├── entity
  │     └── person
  │           └── philosopher {type: "person", root_type: "entity"}
  └── edge_type  ← for relationship definitions
```

### 3. Query Patterns
```cypher
// Fast - direct type
MATCH (n:Node {type: "philosophical_concept"})

// Fast - all of a root type
MATCH (n:Node {root_type: "concept"})

// Slow but complete - inheritance chain
MATCH (n)-[:IS_A*]->(t {name: "concept"})
```

### 4. Validation (Layered)
- **SHACL**: Graph structure (all nodes have `type`, `IS_A` edges valid, `root_type` consistent)
- **JSON Schema**: Content validation at Hermes boundary (properties match type's schema)

### 5. Sophia Capabilities
- Can add node types (create type_definition nodes)
- Can add edge types (create edge_type nodes)
- No code changes required for new types

## Node Structure Example
```cypher
// Root type definition
(concept:Node {
  id: "type-concept",
  type: "type_definition",
  name: "concept",
  json_schema: {...}
})-[:IS_A]->(type_def:Node {type: "type_definition", name: "type_definition"})

// Intermediate type
(phil:Node {
  id: "type-philosophical-concept",
  type: "concept",
  root_type: "concept",
  name: "philosophical_concept",
  json_schema: {...}
})-[:IS_A]->(concept)

// Instance
(n:Node {
  id: "node-123",
  type: "philosophical_concept",
  root_type: "concept",
  name: "nihilism",
  confidence: 0.95,
  temporal_grain: "eternal",
  grounding_type: "ungrounded",
  properties: {...}
})-[:IS_A]->(phil)
```

## Success Criteria
1. Single `Node` label replaces all 15 current node labels
2. Type definitions (node AND edge) stored as data nodes
3. SHACL validates graph structure
4. JSON Schema validates content at Hermes boundary
5. `type` required on all nodes
6. `root_type` computed on creation (traverse to type_definition parent)
7. Index on `type` and `root_type` for performance
8. Core fields from TinyMind: `temporal_grain`, `grounding_type`, `properties`
9. Tests updated (many will fail initially, expected)

## Constraints
- Must not break Talos motor control (strict schemas where needed)
- Use Poetry for dependency management
- Run `ruff`, `mypy`, `pytest` before pushing

## Current State

### LOGOS Node Types (15 to migrate as type_definitions)
abstraction, association, capability, concept, emotion_state, entity, fact, imagined_process, imagined_state, media_sample, perception_frame, persona_entry, process, rule, state

### LOGOS Relationships (36 to convert to edge_type definitions)
ABOUT, APPLIES_TO, ATTACHED_TO, CAN_PERFORM, CAUSES, CONFLICTS_WITH, CONNECTS, CONTRADICTS, DERIVED_FROM, EXECUTED_BY, EXTRACTED_FROM, FEEDS, GENERALIZES, GENERATED_BY, HAS_EMBEDDING, HAS_STATE, IMPLEMENTS, INFERRED_FROM, IS_A, LEARNED_FROM, LOCATED_AT, PART_OF, PRECEDES, PREDICTS, PRODUCES, PRODUCES_OUTPUT, RELATES_TO, REQUIRES, REQUIRES_INPUT, SUPERSEDES, SUPPORTS, TAGGED_ON, TRIGGERED_SIMULATION, TRIGGERS, UPLOADED_BY, USES_CAPABILITY

## Files to Modify
| File | Change |
|------|--------|
| `ontology/core_ontology.cypher` | Universal Node + type definitions + indexes |
| `ontology/shacl_shapes.ttl` | Update for new structure (type/root_type validation) |
| `tests/integration/ontology/*.py` | Update for new structure |
| Other repos | Update Cypher queries |

## Tracking
- Issue: logos#458
- Branch: `feature/logos458-flexible-ontology`
