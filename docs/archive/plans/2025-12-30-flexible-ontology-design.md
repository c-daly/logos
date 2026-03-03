# Flexible Ontology Design

## Overview
Refactor LOGOS ontology from rigid schema-typed node labels to a flexible structure-typed approach. Single `Node` label. Type information via `type` property, `root_type` property, and `IS_A` edges. Minimal bootstrap.

## Bootstrap Types (Only These)

```
type_definition  ← Meta-type (self-referential)
  ├── edge_type  ← For relationship definitions (bootstrap: IS_A only)
  ├── thing      ← Root for concrete/physical
  └── concept    ← Root for abstract/mental (fact, rule, abstraction are concepts)
```

**CWM-A Mapping:**
- `fact`, `rule`, `abstraction` → subtypes of `concept`
- `association` → subtype of `edge_type`

Everything else is data created by Sophia. Test data will be recreated, not migrated.

## Core Ontology (`ontology/core_ontology.cypher`)

```cypher
// === Constraints ===
CREATE CONSTRAINT logos_node_uuid IF NOT EXISTS
FOR (n:Node) REQUIRE n.uuid IS UNIQUE;

// === Indexes ===
CREATE INDEX logos_node_type IF NOT EXISTS FOR (n:Node) ON (n.type);
CREATE INDEX logos_node_name IF NOT EXISTS FOR (n:Node) ON (n.name);
CREATE INDEX logos_node_is_type_def IF NOT EXISTS FOR (n:Node) ON (n.is_type_definition);
CREATE INDEX logos_node_type_name IF NOT EXISTS FOR (n:Node) ON (n.type, n.name);

// === Bootstrap: type_definition (self-referential) ===
MERGE (td:Node {uuid: "type-type_definition"})
SET td.name = "type_definition",
    td.is_type_definition = true,
    td.type = "type_definition",
    td.ancestors = []
MERGE (td)-[:IS_A]->(td);

// === Bootstrap: edge_type ===
MERGE (et:Node {uuid: "type-edge_type"})
SET et.name = "edge_type",
    et.is_type_definition = true,
    et.type = "edge_type",
    et.ancestors = []
WITH et
MATCH (td:Node {uuid: "type-type_definition"})
MERGE (et)-[:IS_A]->(td);

// === Bootstrap: thing ===
MERGE (th:Node {uuid: "type-thing"})
SET th.name = "thing",
    th.is_type_definition = true,
    th.type = "thing",
    th.ancestors = []
WITH th
MATCH (td:Node {uuid: "type-type_definition"})
MERGE (th)-[:IS_A]->(td);

// === Bootstrap: concept ===
MERGE (co:Node {uuid: "type-concept"})
SET co.name = "concept",
    co.is_type_definition = true,
    co.type = "concept",
    co.ancestors = []
WITH co
MATCH (td:Node {uuid: "type-type_definition"})
MERGE (co)-[:IS_A]->(td);

// === Bootstrap: IS_A edge type ===
MERGE (isa:Node {uuid: "87e0d3c8-1f86-5f0c-b1b2-5bfe5cef3b73"})
SET isa.name = "IS_A",
    isa.is_type_definition = true,
    isa.type = "IS_A",
    isa.ancestors = ["edge_type"]
WITH isa
MATCH (et:Node {uuid: "type-edge_type"})
MERGE (isa)-[:IS_A]->(et);
```

## SHACL Shapes (`ontology/shacl_shapes.ttl`)

```turtle
@prefix logos: <http://logos.ai/ontology#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:NodeShape a sh:NodeShape ;
    sh:targetClass logos:Node ;
    sh:property [
        sh:path logos:uuid ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
    ] ;
    sh:property [
        sh:path logos:type ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
    ] .
```

## Node Structure

```
uuid: str                # Required, unique identifier
name: str                # Required, human-readable name
is_type_definition: bool # Required, true for types, false for instances
type: str                # Required, immediate type name
ancestors: list[str]     # Required, inheritance chain from parent to bootstrap root
```

## Property Semantics

### `is_type_definition`
Boolean distinguishing type definitions from instances:
- `true`: This node defines a type (can have instances or subtypes)
- `false`: This node is an instance of a type

### `type`
The node's immediate type name:
- For type definitions: their own name (e.g., "robot_state")
- For instances: the type they're an instance of (e.g., "robot_state")

### `ancestors`
List of type names from immediate parent to bootstrap root:
- Computed by following IS_A chain until reaching type_definition
- Enables "is X a Y?" queries: `"state" IN n.ancestors`
- First element is immediate parent
- Empty for bootstrap types (thing, concept, edge_type)

## Ancestors Computation

```python
def compute_ancestors(node, graph) -> list[str]:
    """
    Follow IS_A chain from node to bootstrap root.

    For type definitions: starts from their IS_A target
    For instances: starts from their type

    Examples:
    - robot_state IS_A state IS_A concept
      ancestors = ["state", "concept"]

    - panda_idle IS_A robot_state
      ancestors = ["robot_state", "state", "concept"]

    - concept IS_A type_definition
      ancestors = []  (bootstrap type)
    """
    ancestors = []
    current = node.follow_is_a()

    while current and current.name != "type_definition":
        ancestors.append(current.name)
        current = current.follow_is_a()

    return ancestors
```

## Examples

**Bootstrap type** `concept IS_A type_definition`:
```
uuid: "type-concept"
name: "concept"
is_type_definition: true
type: "concept"
ancestors: []
```

**Type definition** `state IS_A concept`:
```
uuid: "type-state"
name: "state"
is_type_definition: true
type: "state"
ancestors: ["concept"]
```

**Type definition** `robot_state IS_A state`:
```
uuid: "type-robot_state"
name: "robot_state"
is_type_definition: true
type: "robot_state"
ancestors: ["state", "concept"]
```

**Instance** `panda_idle IS_A robot_state`:
```
uuid: "instance-panda_idle"
name: "panda_idle"
is_type_definition: false
type: "robot_state"
ancestors: ["robot_state", "state", "concept"]
```

## Query Patterns

```cypher
-- All type definitions
MATCH (n:Node {is_type_definition: true})

-- All instances of robot_state (direct)
MATCH (n:Node {type: "robot_state", is_type_definition: false})

-- All states (direct type or ancestor)
MATCH (n:Node) WHERE n.type = "state" OR "state" IN n.ancestors

-- Is panda_idle a concept?
MATCH (n:Node {name: "panda_idle"}) RETURN "concept" IN n.ancestors
```

## Files to Update

### Ontology Core
| File | Action |
|------|--------|
| `ontology/core_ontology.cypher` | Replace with bootstrap |
| `ontology/shacl_shapes.ttl` | Simplify to NodeShape |
| `ontology/validate_ontology.py` | Update validation |

### Tests
| File | Action |
|------|--------|
| `tests/integration/ontology/test_neo4j_crud.py` | Update for Node label |
| `tests/integration/ontology/test_shacl_validation.py` | Update shapes |
| `tests/integration/ontology/test_shacl_pyshacl.py` | Update shapes |
| `tests/integration/ontology/test_shacl_neo4j_validation.py` | Update |
| `tests/test_ontology_extension.py` | Update |
| `tests/infra/test_shacl_validation_service.py` | Update |
| `tests/e2e/test_phase1_end_to_end.py` | Update queries |

### Code with Neo4j Queries
| File | Action |
|------|--------|
| `logos_cwm_e/reflection.py` | Update MATCH queries |
| `logos_hcg/queries.py` | Update all queries |
| `logos_hcg/load_hcg.py` | Update CREATE/MERGE |
| `logos_hcg/demo_planner.py` | Update queries |
| `logos_persona/diary.py` | Update queries |
| `infra/shacl_validation_service.py` | Update |

### Scripts
| File | Action |
|------|--------|
| `scripts/e2e_prototype.sh` | Update |
| `scripts/run_m4_demo.sh` | Update |

## Query Migration Pattern

```cypher
-- Before
MATCH (c:Concept {name: "dog"})

-- After
MATCH (c:Node {type: "concept", name: "dog"})

-- Or for all concepts (including subtypes):
MATCH (c:Node {root_type: "concept"})
```

## Test Data

Test data will be **recreated**, not migrated. Existing test data files will be replaced with minimal fixtures that demonstrate the flexible type system.

## Documentation Updates (69 files reference types)

| Category | Files | Notes |
|----------|-------|-------|
| `docs/architecture/` | 14 | Specs, ADRs need review |
| `sdk-web/sophia/` | 9 | Auto-generated |
| `sdk/python/` | 8 | Auto-generated |
| `docs/hcg/` | 6 | CWM docs need update |
| `ontology/` | 6 | Core ontology docs |
| `docs/operations/` | 4 | Demo walkthroughs |
| `logs/` | 6 | Verification logs (historical) |
| `infra/` | 3 | SHACL service docs |
| Package READMEs | 4 | logos_hcg, cwm_e, persona, perception |
| Other | 9 | Standards, guides, etc. |

**Priority:** ontology/, docs/hcg/, docs/architecture/ first. SDK docs auto-generate.

## Out of Scope (separate PRs)
- Other repos (sophia, hermes, talos, apollo)
- JSON Schema validation in Hermes
- Complex domain type hierarchies (Sophia creates these)
