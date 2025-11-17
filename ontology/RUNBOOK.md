# LOGOS HCG Ontology - Loading and Verification Runbook

This runbook provides step-by-step instructions for loading, verifying, and working with the LOGOS Hybrid Causal Graph (HCG) ontology in Neo4j.

## Prerequisites

- Docker and Docker Compose installed
- Repository cloned to local machine
- Ports 7474 (Neo4j HTTP), 7687 (Neo4j Bolt), 19530 (Milvus), and 9091 (Milvus metrics) available

## Table of Contents

1. [Infrastructure Setup](#infrastructure-setup)
2. [Loading the Core Ontology](#loading-the-core-ontology)
3. [Loading Test Data](#loading-test-data)
4. [Verification Procedures](#verification-procedures)
5. [Common Queries](#common-queries)
6. [Troubleshooting](#troubleshooting)
7. [Data Reset Procedures](#data-reset-procedures)

## Infrastructure Setup

### 1. Start the HCG Development Cluster

From the repository root:

```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```

Expected output:
```
[+] Running 3/3
 ✔ Network logos-hcg-dev-net  Created
 ✔ Container logos-hcg-neo4j  Started
 ✔ Container logos-hcg-milvus Started
```

### 2. Wait for Services to Initialize

Neo4j typically takes 10-30 seconds to start on first launch. Check status:

```bash
docker compose -f infra/docker-compose.hcg.dev.yml ps
```

Both services should show status `Up`.

### 3. Verify Neo4j Connectivity

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "RETURN 'Connected!' AS status;"
```

Expected output:
```
+-------------+
| status      |
+-------------+
| "Connected!"|
+-------------+
```

If you get a connection error, wait a few more seconds and retry.

## Loading the Core Ontology

The core ontology defines node types (Entity, Concept, State, Process), constraints, indexes, and foundational concepts for the pick-and-place domain.

### Load Constraints and Concepts

From the repository root:

```bash
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/core_ontology.cypher
```

Expected output (abbreviated):
```
Added 4 constraints
Added 3 indexes
Created 14 nodes
Created 3 relationships
```

### Verify Constraints

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "SHOW CONSTRAINTS;"
```

You should see at least these constraints:
- `logos_entity_uuid` - Uniqueness constraint on Entity.uuid
- `logos_concept_uuid` - Uniqueness constraint on Concept.uuid
- `logos_concept_name` - Uniqueness constraint on Concept.name
- `logos_state_uuid` - Uniqueness constraint on State.uuid
- `logos_process_uuid` - Uniqueness constraint on Process.uuid

### Verify Indexes

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "SHOW INDEXES;"
```

You should see indexes for:
- `logos_entity_name` - Index on Entity.name
- `logos_state_timestamp` - Index on State.timestamp
- `logos_process_timestamp` - Index on Process.start_time

### Verify Concepts Loaded

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (c:Concept) RETURN c.name ORDER BY c.name;"
```

Expected concepts include:
- Container
- FreeState
- GraspAction
- GraspableObject
- GraspedState
- Gripper
- Joint
- Location
- Manipulator
- MoveAction
- PlaceAction
- PositionedState
- ReleaseAction
- RigidBody
- Surface
- Workspace

## Loading Test Data

The test data creates a complete pick-and-place scenario with robot entities, workspace components, objects, states, and processes.

### Load Pick-and-Place Scenario

```bash
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/test_data_pick_and_place.cypher
```

Expected output:
```
Created ~40 nodes
Created ~60 relationships
Set ~200 properties
```

### Verify Entities Loaded

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (e:Entity) RETURN e.name, labels(e) AS labels ORDER BY e.name;"
```

You should see entities including:
- RobotArm01
- Gripper01
- Joint01-Base, Joint02-Shoulder, Joint03-Elbow
- WorkTable01
- TargetBin01
- RedBlock01, BlueBlock01
- GreenCylinder01

### Verify States and Processes

Count nodes by type:

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count ORDER BY type;"
```

Expected counts (approximate):
- Concept: ~16
- Entity: ~9
- State: ~15
- Process: ~4

## Verification Procedures

### 1. Check Node Type Distribution

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (n) RETURN DISTINCT labels(n) AS nodeTypes, count(n) AS count;"
```

### 2. Verify Relationship Types

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationshipType, count(r) AS count ORDER BY relationshipType;"
```

Expected relationship types:
- IS_A (type membership)
- HAS_STATE (entity-state links)
- CAUSES (process-state causality)
- PART_OF (compositional hierarchy)
- LOCATED_AT (spatial relationships)
- PRECEDES (temporal ordering)
- REQUIRES (preconditions)

### 3. Validate UUID Patterns

Check that all UUIDs follow the required patterns:

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (e:Entity) WHERE NOT e.uuid STARTS WITH 'entity-' RETURN count(e) AS invalid_entity_uuids;"
```

Should return 0 for all node types (Entity, Concept, State, Process).

### 4. Check Causal Chain Integrity

Verify that processes have proper causal relationships:

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (p:Process) WHERE NOT EXISTS((p)-[:CAUSES]->()) RETURN p.name AS processWithoutCausedState;"
```

Should return no rows (all processes should cause at least one state).

### 5. Verify Temporal Ordering

Check that state transitions have proper temporal ordering:

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (s1:State)-[:PRECEDES]->(s2:State) WHERE s1.timestamp > s2.timestamp RETURN s1.name, s2.name, s1.timestamp, s2.timestamp;"
```

Should return no rows (preceding states should have earlier timestamps).

## Common Queries

### Find All Graspable Objects

```cypher
MATCH (e:Entity)-[:IS_A]->(c:Concept {name: 'GraspableObject'})
RETURN e.name AS object, e.uuid AS uuid, e.mass AS mass;
```

From command line:

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (e:Entity)-[:IS_A]->(c:Concept {name: 'GraspableObject'}) RETURN e.name AS object, e.uuid AS uuid, e.mass AS mass;"
```

### Get Current State of an Entity

```cypher
MATCH (e:Entity {name: 'RedBlock01'})-[:HAS_STATE]->(s:State)
RETURN s
ORDER BY s.timestamp DESC
LIMIT 1;
```

### Trace Causal Chain from a Process

```cypher
MATCH path = (p:Process {name: 'GraspRedBlock'})-[:CAUSES*1..5]->(s:State)
RETURN path;
```

### Find Required Preconditions for a Process

```cypher
MATCH (p:Process {name: 'GraspRedBlock'})-[:REQUIRES]->(s:State)
RETURN p.name AS process, s.name AS requiredState, s.timestamp AS stateTime;
```

### Get Compositional Hierarchy

```cypher
MATCH path = (part:Entity)-[:PART_OF*1..3]->(whole:Entity)
WHERE part.name STARTS WITH 'Joint'
RETURN path;
```

### Find All States in Temporal Order

```cypher
MATCH (s:State)
RETURN s.name AS state, s.timestamp AS time
ORDER BY s.timestamp;
```

### Visualize Pick-and-Place Process Flow

```cypher
MATCH path = (e:Entity {name: 'RedBlock01'})-[:HAS_STATE]->(s:State)
OPTIONAL MATCH (s)-[:PRECEDES*]->(nextState:State)
RETURN path;
```

## Troubleshooting

### Issue: "Database not available"

**Cause**: Neo4j is still initializing.

**Solution**: Wait 10-30 seconds and retry. Check logs:

```bash
docker logs logos-hcg-neo4j
```

### Issue: Constraints Already Exist

**Cause**: Ontology has been loaded previously.

**Solution**: This is expected behavior if you've loaded the ontology before. The `CREATE CONSTRAINT IF NOT EXISTS` syntax prevents errors. The existing constraints will be preserved.

### Issue: "Duplicate node" or "Node already exists"

**Cause**: Test data has been loaded previously.

**Solution**: The `MERGE` statements in the test data script are idempotent - they will match existing nodes rather than creating duplicates. To start fresh, see [Data Reset Procedures](#data-reset-procedures).

### Issue: Queries Return Empty Results

**Cause**: 
1. Data not loaded yet
2. Incorrect node labels or property names

**Solution**:
1. Verify data was loaded (see verification procedures above)
2. Check that you're using correct labels: `Entity`, `Concept`, `State`, `Process` (capitalized)
3. Check property names match the schema (e.g., `uuid` not `id`)

### Issue: Performance is Slow

**Cause**: Docker resource constraints.

**Solution**: Increase Docker resources:
- Memory: At least 4GB
- CPU: 2+ cores

Check resource usage:

```bash
docker stats logos-hcg-neo4j logos-hcg-milvus
```

## Data Reset Procedures

### Soft Reset: Clear All Nodes and Relationships

**Warning**: This deletes all graph data but preserves constraints and indexes.

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (n) DETACH DELETE n;"
```

After soft reset, reload the ontology and test data.

### Hard Reset: Complete Database Reset

**Warning**: This deletes all data, constraints, and indexes.

```bash
# Stop containers
docker compose -f infra/docker-compose.hcg.dev.yml down

# Remove volumes (deletes all data)
docker compose -f infra/docker-compose.hcg.dev.yml down -v

# Start fresh
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Wait for Neo4j to initialize
sleep 15

# Reload ontology
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/core_ontology.cypher

# Reload test data
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/test_data_pick_and_place.cypher
```

### Selective Reset: Remove Only Test Data

**Warning**: This removes entities and states but preserves concepts and constraints.

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (n) WHERE n:Entity OR n:State OR n:Process DETACH DELETE n;"
```

After selective reset, you can reload just the test data:

```bash
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/test_data_pick_and_place.cypher
```

## Next Steps

### Integrate with Sophia

Once the ontology is loaded, Sophia can connect to the HCG:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "logosdev")
)

# Example: Query for graspable objects
with driver.session() as session:
    result = session.run(
        "MATCH (e:Entity)-[:IS_A]->(:Concept {name: 'GraspableObject'}) "
        "RETURN e.name AS name, e.uuid AS uuid"
    )
    for record in result:
        print(f"{record['name']}: {record['uuid']}")
```

### Add Custom Entities

Follow the UUID patterns and use MERGE for idempotency:

```cypher
MERGE (e:Entity {uuid: 'entity-custom-block-01'})
ON CREATE SET
    e.name = 'CustomBlock',
    e.description = 'Custom test block',
    e.width = 0.06,
    e.height = 0.06,
    e.depth = 0.06,
    e.mass = 0.2,
    e.created_at = datetime();

MERGE (e)-[:IS_A]->(:Concept {uuid: 'concept-graspable'});
```

### Vector Embeddings Integration

Future phases will integrate Milvus for semantic search. Placeholder for embedding properties (Section 4.2 of spec):

```cypher
// Example: Add embedding reference to a concept
MATCH (c:Concept {uuid: 'concept-graspable'})
SET c.embedding_id = 'milvus-vector-id-12345',
    c.embedding_model = 'sentence-transformers/all-MiniLM-L6-v2',
    c.last_sync = datetime();
```

## Reference Documentation

- **Full Specification**: `docs/spec/project_logos_full.md`
- **Pick-and-Place Domain Guide**: `ontology/README_PICK_AND_PLACE.md`
- **Infrastructure Guide**: `infra/README.md`
- **SHACL Validation Shapes**: `ontology/shacl_shapes.ttl`

## Validation

Run the Python validation script to check ontology file syntax:

```bash
python ontology/validate_ontology.py
```

Run the integration tests:

```bash
python tests/test_ontology_extension.py
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the specification in `docs/spec/project_logos_full.md`
3. Check GitHub issues at https://github.com/c-daly/logos/issues
