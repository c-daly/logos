# HCG Data Layer

The Hybrid Cognitive Graph (HCG) is the central knowledge store for Project LOGOS.
It combines a Neo4j graph database for structured relationships with Milvus vector
storage for semantic search. This document describes the data model, capability
catalog, and query patterns.

## Table of Contents

- [Core Node Types](#core-node-types)
- [Capability Catalog](#capability-catalog)
- [Relationships](#relationships)
- [Query Patterns](#query-patterns)
- [Python API](#python-api)
- [SHACL Validation](#shacl-validation)

## Core Node Types

The HCG uses five primary node types:

| Node Type | UUID Prefix | Description |
|-----------|-------------|-------------|
| `Entity` | `entity-` | Concrete objects and agents in the world |
| `Concept` | `concept-` | Abstract categories and types |
| `State` | `state-` | Temporal snapshots of entity properties |
| `Process` | `process-` | Actions that cause state changes |
| `Capability` | `capability-` | Tools/processes for Sophia planning |

### Entity

Represents concrete instances - physical objects, robots, locations.

```cypher
CREATE (e:Entity {
    uuid: 'entity-gripper-01',
    name: 'Panda Gripper',
    description: 'Franka Emika parallel gripper',
    created_at: datetime(),
    max_grasp_width: 0.08,
    max_force: 70.0
})
```

### Concept

Represents abstract categories that entities can belong to.

```cypher
CREATE (c:Concept {
    uuid: 'concept-gripper',
    name: 'Gripper',
    description: 'Abstract concept of end-effector for grasping'
})
```

### State

Captures temporal snapshots of entity properties.

```cypher
CREATE (s:State {
    uuid: 'state-gripper-01-t1',
    timestamp: datetime(),
    is_closed: false,
    grasp_width: 0.08
})
```

### Process

Represents actions that transform states.

```cypher
CREATE (p:Process {
    uuid: 'process-grasp-001',
    name: 'Grasp Red Block',
    start_time: datetime(),
    duration_ms: 2500
})
```

## Capability Catalog

The capability catalog (logos#284) enables Sophia's planner to discover and use
available tools. Each capability describes what it does, how it's executed, and
its performance characteristics.

### Capability Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `uuid` | string | ✓ | Unique ID, must start with `capability-` |
| `name` | string | ✓ | Unique capability name |
| `executor_type` | enum | ✓ | `human`, `talos`, `service`, or `llm` |
| `description` | string | | What the capability does |
| `capability_tags` | list | | Tags for discovery (e.g., `['manipulation', 'pick']`) |
| `version` | string | | Semantic version |
| `deprecated` | boolean | | Whether capability is deprecated |

**Performance Metrics:**

| Property | Type | Description |
|----------|------|-------------|
| `estimated_duration_ms` | integer | Typical execution time |
| `estimated_cost` | decimal | Relative cost for planning |
| `success_rate` | decimal | Historical success rate (0.0-1.0) |
| `invocation_count` | integer | Usage statistics |

**Integration Properties (executor-specific):**

| Property | Executor Type | Description |
|----------|---------------|-------------|
| `service_endpoint` | service | URL for API calls |
| `action_name` | talos | ROS action name |
| `instruction_template` | human | Template for human instructions |
| `prompt_template` | llm | Template for LLM prompts |

### Executor Types

| Type | Description | Use Case |
|------|-------------|----------|
| `human` | Instructions for human operators | "Mail a letter" workflow |
| `talos` | Robotic actions via Talos | Pick-and-place, navigation |
| `service` | External API/service calls | Weather lookup, database query |
| `llm` | Language model reasoning | Summarization, analysis |

### Creating a Capability

```cypher
// Create a pick capability for Talos
CREATE (cap:Capability {
    uuid: 'capability-talos-pick',
    name: 'TalosPick',
    executor_type: 'talos',
    description: 'Pick up an object using the robotic gripper',
    capability_tags: ['manipulation', 'pick', 'grasping'],
    action_name: '/talos/pick_object',
    estimated_duration_ms: 5000,
    estimated_cost: 1.0,
    success_rate: 0.95,
    invocation_count: 0,
    version: '1.0.0',
    deprecated: false,
    created_at: datetime(),
    updated_at: datetime()
})

// Link to action concept it implements
MATCH (cap:Capability {uuid: 'capability-talos-pick'})
MATCH (concept:Concept {name: 'GraspAction'})
CREATE (cap)-[:IMPLEMENTS]->(concept)

// Define required inputs
MATCH (cap:Capability {uuid: 'capability-talos-pick'})
MATCH (input:Concept {name: 'EntityRefInput'})
CREATE (cap)-[:REQUIRES_INPUT]->(input)

// Define outputs
MATCH (cap:Capability {uuid: 'capability-talos-pick'})
MATCH (output:Concept {name: 'StateOutput'})
CREATE (cap)-[:PRODUCES_OUTPUT]->(output)
```

### Human Workflow Capability

```cypher
CREATE (cap:Capability {
    uuid: 'capability-human-mail-letter',
    name: 'MailLetter',
    executor_type: 'human',
    description: 'Mail a physical letter via postal service',
    capability_tags: ['communication', 'physical', 'mail'],
    instruction_template: 'Please mail the letter to {{recipient}} at {{address}}. Use {{postage_type}} postage.',
    estimated_duration_ms: 86400000,  // 24 hours
    estimated_cost: 5.0,
    version: '1.0.0'
})
```

### Service Integration Capability

```cypher
CREATE (cap:Capability {
    uuid: 'capability-service-weather',
    name: 'GetWeather',
    executor_type: 'service',
    description: 'Retrieve current weather for a location',
    capability_tags: ['information', 'weather', 'external'],
    service_endpoint: 'https://api.weather.example/v1/current',
    estimated_duration_ms: 500,
    estimated_cost: 0.1,
    version: '1.0.0'
})
```

## Relationships

### Core Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `IS_A` | Entity | Concept | Type membership |
| `HAS_STATE` | Entity | State | Current/historical state |
| `CAUSES` | Process | State | Causal effect |
| `PART_OF` | Entity | Entity | Compositional hierarchy |
| `REQUIRES` | Process | State | Precondition |

### Capability Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `IMPLEMENTS` | Capability | Concept | Action concept implemented |
| `REQUIRES_INPUT` | Capability | Concept | Input type required |
| `PRODUCES_OUTPUT` | Capability | Concept | Output type produced |
| `EXECUTED_BY` | Capability | Entity | Entity that can execute |
| `USES_CAPABILITY` | Process | Capability | Plan step uses capability |

## Query Patterns

### Find Capabilities by Tag

```cypher
// Find all manipulation capabilities
MATCH (cap:Capability)
WHERE 'manipulation' IN cap.capability_tags
  AND (cap.deprecated IS NULL OR cap.deprecated = false)
RETURN cap
ORDER BY cap.success_rate DESC
```

### Find Capabilities for Planning

```cypher
// Find capabilities that implement GraspAction, sorted by reliability
MATCH (cap:Capability)-[:IMPLEMENTS]->(c:Concept {name: 'GraspAction'})
WHERE cap.deprecated IS NULL OR cap.deprecated = false
RETURN cap
ORDER BY cap.success_rate DESC, cap.estimated_cost ASC
```

### Get Capability with Full Context

```cypher
MATCH (cap:Capability {name: 'TalosPick'})
OPTIONAL MATCH (cap)-[:IMPLEMENTS]->(impl:Concept)
OPTIONAL MATCH (cap)-[:REQUIRES_INPUT]->(input:Concept)
OPTIONAL MATCH (cap)-[:PRODUCES_OUTPUT]->(output:Concept)
OPTIONAL MATCH (cap)-[:EXECUTED_BY]->(executor:Entity)
RETURN cap,
       collect(DISTINCT impl) as implements,
       collect(DISTINCT input) as required_inputs,
       collect(DISTINCT output) as produced_outputs,
       collect(DISTINCT executor) as executors
```

### Record Capability Usage

```cypher
// Update statistics after successful invocation
MATCH (cap:Capability {uuid: $uuid})
SET cap.invocation_count = COALESCE(cap.invocation_count, 0) + 1,
    cap.success_rate = (cap.success_rate * cap.invocation_count + 1) / (cap.invocation_count + 1),
    cap.updated_at = datetime()
RETURN cap
```

### Link Process to Capability

```cypher
// When a plan step uses a capability
MATCH (p:Process {uuid: 'process-grasp-001'})
MATCH (cap:Capability {uuid: 'capability-talos-pick'})
CREATE (p)-[:USES_CAPABILITY]->(cap)
```

## Python API

The `logos_hcg` package provides type-safe models and queries.

### Models

```python
from logos_hcg import Capability, ExecutorType

# Create a capability
cap = Capability(
    uuid='capability-example',
    name='ExampleCapability',
    executor_type=ExecutorType.SERVICE,
    description='An example capability',
    capability_tags=['example', 'demo'],
    estimated_duration_ms=1000,
)
```

### Queries

```python
from logos_hcg import HCGClient, HCGQueries

client = HCGClient()

# Find capabilities by tag
query = HCGQueries.find_capabilities_by_tag()
result = client.run(query, {'tag': 'manipulation'})

# Find capabilities implementing an action
query = HCGQueries.find_capabilities_implementing_concept()
result = client.run(query, {'concept_uuid': 'concept-grasp'})

# Create a capability
query = HCGQueries.create_capability()
result = client.run(query, {
    'uuid': 'capability-new',
    'name': 'NewCapability',
    'executor_type': 'service',
    'description': 'A new capability',
    'capability_tags': ['new'],
    'version': '1.0.0',
    'estimated_duration_ms': 500,
    'estimated_cost': 0.5,
})

# Record invocation
query = HCGQueries.record_capability_invocation()
result = client.run(query, {'uuid': 'capability-new', 'success': True})
```

## SHACL Validation

Capabilities are validated using SHACL shapes defined in `ontology/shacl_shapes.ttl`.

### Required Validation

- `uuid` must be present and start with `capability-`
- `name` must be present and unique
- `executor_type` must be one of: `human`, `talos`, `service`, `llm`

### Optional Validation

- `success_rate` must be between 0.0 and 1.0
- `estimated_duration_ms` must be non-negative
- `estimated_cost` must be non-negative
- `invocation_count` must be non-negative

### Running Validation

```bash
cd ontology
python validate_ontology.py
```

## See Also

- [Core Ontology](../ontology/README.md)
- [SHACL Shapes](../ontology/shacl_shapes.ttl)
- [Pick-and-Place Domain](../ontology/README_PICK_AND_PLACE.md)
