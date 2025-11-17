# Phase 1 Verification Checklist

This document defines the verification criteria and gating mechanism for Phase 1 of Project LOGOS. **Phase 2 work cannot begin until all verification criteria are met and all smoke tests pass.**

Reference: Section 7.1 of the specification (`docs/spec/project_logos_full.md`)

## Overview

Phase 1 ("Formalize HCG and Abstract Pipeline") has four key milestones over 8-12 weeks:
- **M1**: HCG can store and retrieve entities (Week 2)
- **M2**: SHACL validation catches errors (Week 4)
- **M3**: Sophia can plan simple actions (Week 6)
- **M4**: End-to-end pick-and-place demo (Week 8)

Each milestone must be verified through both manual demonstration and automated smoke tests before proceeding to Phase 2.

---

## M1: HCG Store and Retrieve Entities (Week 2)

### Objective
Demonstrate that the HCG (Neo4j + Milvus hybrid system) can store and retrieve entities with proper causal relationships.

### Verification Checklist

#### Infrastructure
- [ ] Neo4j development cluster is running (`docker-compose -f infra/docker-compose.hcg.dev.yml up -d`)
- [ ] Milvus development cluster is running
- [ ] Neo4j accessible on ports 7474 (HTTP) and 7687 (Bolt)
- [ ] Milvus accessible on ports 19530 and 9091
- [ ] Neo4j includes neosemantics (n10s) plugin for RDF/SHACL support

#### Ontology Loading
- [ ] `ontology/core_ontology.cypher` loads successfully into Neo4j without errors
- [ ] All UUID constraints are created (entity, concept, state, process)
- [ ] All indexes are created (entity name, state timestamp, process timestamp)
- [ ] Concept name uniqueness constraint is active

#### Entity Operations
- [ ] Can create Entity nodes with required UUID format (`entity-*`)
- [ ] Can create Concept nodes with required UUID format (`concept-*`)
- [ ] Can create State nodes with required UUID format (`state-*`)
- [ ] Can create Process nodes with required UUID format (`process-*`)
- [ ] Can establish IS_A relationships between Entity and Concept
- [ ] Can establish HAS_STATE relationships between Entity and State
- [ ] Can establish CAUSES relationships between Process and State
- [ ] Can establish PART_OF relationships between entities

#### Retrieval Operations
- [ ] Can query entities by UUID
- [ ] Can query entities by name
- [ ] Can query states by timestamp
- [ ] Can query processes by start_time
- [ ] Can traverse IS_A relationships to find entity types
- [ ] Can traverse HAS_STATE relationships to find current states
- [ ] Can traverse CAUSES relationships to trace causal chains

### Manual Demonstration Steps

1. **Start Infrastructure**
   ```bash
   cd infra
   docker-compose -f docker-compose.hcg.dev.yml up -d
   # Wait for Neo4j to be ready (check localhost:7474)
   ```

2. **Load Ontology**
   ```bash
   # Using cypher-shell or Neo4j Browser at localhost:7474
   cat ontology/core_ontology.cypher | docker exec -i <neo4j-container> cypher-shell -u neo4j -p <password>
   ```

3. **Create Test Entity**
   ```cypher
   // Create a test manipulator entity
   CREATE (e:Entity {uuid: 'entity-test-arm-001', name: 'TestArm', created_at: datetime()})
   CREATE (c:Concept {uuid: 'concept-manipulator', name: 'Manipulator'})
   CREATE (e)-[:IS_A]->(c)
   RETURN e, c;
   ```

4. **Retrieve Test Entity**
   ```cypher
   // Verify retrieval by UUID
   MATCH (e:Entity {uuid: 'entity-test-arm-001'})
   RETURN e;
   
   // Verify retrieval by name
   MATCH (e:Entity {name: 'TestArm'})
   RETURN e;
   
   // Verify concept relationship
   MATCH (e:Entity {name: 'TestArm'})-[:IS_A]->(c:Concept)
   RETURN e.name, c.name;
   ```

5. **Verify State Relationships**
   ```cypher
   // Create a state and link it
   CREATE (s:State {uuid: 'state-test-001', timestamp: datetime()})
   MATCH (e:Entity {uuid: 'entity-test-arm-001'})
   CREATE (e)-[:HAS_STATE]->(s)
   RETURN e, s;
   
   // Query state by entity
   MATCH (e:Entity {name: 'TestArm'})-[:HAS_STATE]->(s:State)
   RETURN s ORDER BY s.timestamp DESC LIMIT 1;
   ```

### Automated Smoke Tests

See: `tests/phase1/test_m1_hcg_store_retrieve.py`

The automated test verifies:
- Neo4j connection and authentication
- Ontology script execution without errors
- Entity creation with UUID constraints
- Relationship creation (IS_A, HAS_STATE, CAUSES, PART_OF)
- Query operations (by UUID, by name, by timestamp)
- Constraint enforcement (UUID uniqueness, format validation)

**Status**: ⏸️ Not yet implemented (CI test pending)

---

## M2: SHACL Validation Catches Errors (Week 4)

### Objective
Demonstrate that SHACL validation rules successfully catch malformed graph updates and enforce data quality.

### Verification Checklist

#### SHACL Infrastructure
- [ ] `ontology/shacl_shapes.ttl` is syntactically valid RDF/Turtle
- [ ] SHACL shapes file loads into Neo4j neosemantics
- [ ] Validation can be triggered programmatically
- [ ] Validation reports include constraint violations with details

#### Shape Coverage
- [ ] EntityShape validates Entity nodes
  - [ ] UUID format constraint (`entity-*` pattern)
  - [ ] UUID uniqueness
  - [ ] Optional name and description fields
- [ ] ConceptShape validates Concept nodes
  - [ ] UUID format constraint (`concept-*` pattern)
  - [ ] Required name field
  - [ ] Name uniqueness
- [ ] StateShape validates State nodes
  - [ ] UUID format constraint (`state-*` pattern)
  - [ ] Required timestamp field
  - [ ] Timestamp datatype validation
- [ ] ProcessShape validates Process nodes
  - [ ] UUID format constraint (`process-*` pattern)
  - [ ] Required start_time field
  - [ ] Optional duration_ms field

#### Error Detection
- [ ] Detects missing required fields (UUID, timestamp, etc.)
- [ ] Detects invalid UUID format (wrong prefix)
- [ ] Detects invalid data types (string vs datetime)
- [ ] Detects cardinality violations (multiple values for single-valued properties)
- [ ] Detects invalid relationship types

### Manual Demonstration Steps

1. **Load SHACL Shapes**
   ```bash
   # Using Python with rdflib and pyshacl
   python3 << 'EOF'
   from rdflib import Graph
   g = Graph()
   g.parse("ontology/shacl_shapes.ttl", format="turtle")
   print(f"Loaded {len(g)} SHACL triples")
   EOF
   ```

2. **Test Valid Data**
   ```cypher
   // This should pass validation
   CREATE (e:Entity {
     uuid: 'entity-valid-001',
     name: 'ValidEntity',
     created_at: datetime()
   })
   RETURN e;
   ```

3. **Test Invalid UUID Format**
   ```cypher
   // This should fail validation (wrong UUID prefix)
   CREATE (e:Entity {
     uuid: 'invalid-001',  // Should be 'entity-001'
     name: 'InvalidEntity'
   })
   RETURN e;
   ```

4. **Test Missing Required Field**
   ```cypher
   // This should fail validation (missing UUID)
   CREATE (e:Entity {
     name: 'NoUUID'
   })
   RETURN e;
   ```

5. **Run SHACL Validation**
   ```python
   from rdflib import Graph
   from pyshacl import validate
   
   # Load shapes
   shapes_graph = Graph()
   shapes_graph.parse("ontology/shacl_shapes.ttl", format="turtle")
   
   # Load data to validate
   data_graph = Graph()
   # ... populate data_graph from Neo4j or test fixture
   
   # Validate
   conforms, results_graph, results_text = validate(
       data_graph,
       shacl_graph=shapes_graph,
       inference='rdfs',
       abort_on_first=False
   )
   
   print(f"Validation {'PASSED' if conforms else 'FAILED'}")
   if not conforms:
       print(results_text)
   ```

### Automated Smoke Tests

See: `tests/phase1/test_m2_shacl_validation.py`

The automated test verifies:
- Valid fixture data passes SHACL validation
- Invalid fixtures fail with expected error messages:
  - Missing UUID
  - Wrong UUID format
  - Missing required timestamp
  - Invalid data types
  - Cardinality violations
- Validation reports are parseable and informative

**Status**: ⏸️ Not yet implemented (CI test pending)

---

## M3: Sophia Can Plan Simple Actions (Week 6)

### Objective
Demonstrate that Sophia's planning component can generate simple action sequences using causal reasoning over the HCG.

### Verification Checklist

#### Planning Infrastructure
- [ ] Sophia repository exists and is accessible
- [ ] Planning module is implemented (even if minimal)
- [ ] Planning module can connect to Neo4j HCG
- [ ] Planning module can query causal relationships

#### Planning Capabilities
- [ ] Can identify goal states in HCG
- [ ] Can identify current states in HCG
- [ ] Can traverse CAUSES relationships backward from goals
- [ ] Can identify required preconditions via REQUIRES relationships
- [ ] Can generate ordered sequence of processes to reach goal
- [ ] Can represent plan as list of process nodes with causal dependencies

#### Pick-and-Place Planning
- [ ] Can plan "pick object" action
  - [ ] Identifies preconditions (gripper open, arm at pre-grasp position)
  - [ ] Identifies causal process (GraspAction)
  - [ ] Identifies resulting state (object grasped)
- [ ] Can plan "place object" action
  - [ ] Identifies preconditions (object grasped, arm at place position)
  - [ ] Identifies causal process (ReleaseAction)
  - [ ] Identifies resulting state (object released, located at target)
- [ ] Can plan multi-step sequence
  - [ ] Move to pre-grasp → Grasp → Move to place → Release

### Manual Demonstration Steps

1. **Load Pick-and-Place Test Data**
   ```bash
   cat ontology/test_data_pick_and_place.cypher | docker exec -i <neo4j-container> cypher-shell -u neo4j -p <password>
   ```

2. **Query Available Processes**
   ```cypher
   // Find all process concepts
   MATCH (c:Concept)
   WHERE c.name ENDS WITH 'Action'
   RETURN c.name;
   
   // Expected: GraspAction, ReleaseAction, MoveAction, PlaceAction
   ```

3. **Trace Causal Chain**
   ```cypher
   // Find what causes a grasped state
   MATCH (p:Process)-[:CAUSES]->(s:State)
   WHERE s.name CONTAINS 'Grasped'
   RETURN p.name, s.name;
   ```

4. **Identify Preconditions**
   ```cypher
   // Find what a grasp action requires
   MATCH (p:Process {name: 'GraspRedBlock'})-[:REQUIRES]->(s:State)
   RETURN p.name, s.name;
   ```

5. **Generate Simple Plan (Pseudocode for Sophia)**
   ```python
   # This would be implemented in Sophia
   def plan_pick_and_place(object_entity, target_location):
       # 1. Query current state
       current_state = query_entity_state(object_entity)
       
       # 2. Define goal state
       goal_state = create_goal_state(object_entity, target_location)
       
       # 3. Backward search from goal
       processes = []
       state = goal_state
       while state != current_state:
           # Find process that causes this state
           process = query_causes(state)
           processes.insert(0, process)
           
           # Find required preconditions
           preconditions = query_requires(process)
           state = preconditions[0]
       
       return processes
   ```

### Automated Smoke Tests

See: `tests/phase1/test_m3_planning.py`

The automated test verifies:
- Causal graph traversal (CAUSES relationships)
- Precondition identification (REQUIRES relationships)
- Goal state reachability
- Plan generation for simple scenarios:
  - Single-step plan (grasp object)
  - Multi-step plan (pick and place)
- Plan validation (correct ordering, all preconditions met)

**Status**: ⏸️ Not yet implemented (CI test pending)

---

## M4: End-to-End Pick-and-Place Demo (Week 8)

### Objective
Demonstrate the complete system integration: Apollo → Sophia → Talos → HCG, executing a pick-and-place task.

### Verification Checklist

#### Component Integration
- [ ] Apollo UI is running and accessible
- [ ] Sophia cognitive core is running
- [ ] Talos hardware abstraction is running (simulated mode)
- [ ] Hermes language services are running
- [ ] All components can communicate via defined APIs
- [ ] HCG is shared and accessible to all components

#### End-to-End Flow
- [ ] User issues command via Apollo: "Pick up the red block and place it in the bin"
- [ ] Apollo sends command to Sophia via API
- [ ] Sophia uses Hermes to parse natural language command
- [ ] Sophia queries HCG for current state
- [ ] Sophia generates plan using M3 planning capability
- [ ] Sophia stores plan in HCG
- [ ] Sophia executes plan via Talos simulated actuators
- [ ] Talos updates HCG with state changes during execution
- [ ] Sophia monitors execution and handles completion
- [ ] Apollo displays updated state and success confirmation

#### Observable Outcomes
- [ ] HCG contains entities for manipulator, objects, workspace
- [ ] HCG contains process nodes for each action in plan
- [ ] HCG contains state nodes showing progression
- [ ] CAUSES relationships link processes to resulting states
- [ ] PRECEDES relationships show temporal ordering
- [ ] Final state shows object in target location
- [ ] All state transitions are validated by SHACL

### Manual Demonstration Steps

1. **Start All Services**
   ```bash
   # Start HCG infrastructure
   docker-compose -f infra/docker-compose.hcg.dev.yml up -d
   
   # Start Hermes (in c-daly/hermes repo)
   cd ../hermes && docker-compose up -d
   
   # Start Talos in simulation mode (in c-daly/talos repo)
   cd ../talos && python -m talos.simulator
   
   # Start Sophia (in c-daly/sophia repo)
   cd ../sophia && python -m sophia.orchestrator
   
   # Start Apollo UI (in c-daly/apollo repo)
   cd ../apollo && npm start
   ```

2. **Load Initial State**
   ```bash
   # Load pick-and-place ontology and test data
   cat ontology/core_ontology.cypher | docker exec -i <neo4j-container> cypher-shell -u neo4j -p <password>
   cat ontology/test_data_pick_and_place.cypher | docker exec -i <neo4j-container> cypher-shell -u neo4j -p <password>
   ```

3. **Execute Demo via Apollo**
   - Open Apollo UI in browser (localhost:3000 or configured port)
   - Enter command: "Pick up the red block and place it in the bin"
   - Observe plan generation in UI
   - Observe execution progress
   - Observe state updates in real-time
   - Confirm success message

4. **Verify HCG Updates**
   ```cypher
   // Check final state of red block
   MATCH (e:Entity {name: 'RedBlock01'})-[:HAS_STATE]->(s:State)
   RETURN s ORDER BY s.timestamp DESC LIMIT 1;
   
   // Verify location update
   MATCH (e:Entity {name: 'RedBlock01'})-[:LOCATED_AT]->(t:Entity)
   RETURN t.name;  // Should return 'TargetBin01'
   
   // Trace execution history
   MATCH path = (p:Process)-[:CAUSES*1..5]->(s:State)
   WHERE p.name CONTAINS 'RedBlock'
   RETURN path;
   ```

5. **Verify SHACL Compliance**
   ```python
   # Export HCG state and validate against SHACL
   # All state updates should conform to shapes
   ```

### Automated Smoke Tests

See: `tests/phase1/test_m4_end_to_end.py`

The automated test verifies:
- Component startup and health checks
- API connectivity between components
- Command processing flow
- Plan generation and storage in HCG
- Simulated execution
- State updates in HCG
- SHACL validation throughout execution
- Final state correctness

**Status**: ⏸️ Not yet implemented (integration test pending)

---

## Phase 2 Gate Rules

### Gate Criteria

Phase 2 work **MUST NOT** begin until ALL of the following criteria are met:

#### 1. Milestone Completion
- [ ] M1 verification checklist 100% complete
- [ ] M2 verification checklist 100% complete
- [ ] M3 verification checklist 100% complete
- [ ] M4 verification checklist 100% complete

#### 2. Automated Tests Passing
- [ ] `test_m1_hcg_store_retrieve.py` passes (CI)
- [ ] `test_m2_shacl_validation.py` passes (CI)
- [ ] `test_m3_planning.py` passes (CI)
- [ ] All existing tests continue to pass
- [ ] No security vulnerabilities in changed code (CodeQL clean)

#### 3. Manual Demonstrations
- [ ] M1 manual demo successfully completed and documented
- [ ] M2 manual demo successfully completed and documented
- [ ] M3 manual demo successfully completed and documented
- [ ] M4 manual demo successfully completed and documented

#### 4. Documentation
- [ ] All verification checklists signed off
- [ ] Demo recordings or screenshots captured
- [ ] Known issues documented with mitigation plans
- [ ] Phase 1 retrospective completed

### Gate Enforcement

The gate is enforced through:

1. **GitHub Branch Protection**
   - Phase 2 branches cannot be created until gate criteria are met
   - Main branch requires passing CI before merge
   - Phase 1 milestone must be closed before Phase 2 milestone opens

2. **CI/CD Pipeline**
   - `.github/workflows/phase1-gate.yml` workflow checks gate status
   - Workflow runs on attempts to create Phase 2 issues or branches
   - Workflow fails if any gate criterion is not met
   - Status badge displays gate status: 🔴 Blocked / 🟡 In Progress / 🟢 Passed

3. **Project Board**
   - Phase 2 issues are hidden until gate passes
   - Automation moves completed Phase 1 issues to "Done"
   - Gate status is visible on project board dashboard

### Override Procedure

In exceptional circumstances, the gate can be overridden with proper justification:

1. **Who Can Override**
   - Project lead (c-daly)
   - Technical steering committee (if established)

2. **Override Process**
   - Create GitHub issue titled "Phase 2 Gate Override Request"
   - Document which criteria are not met
   - Provide technical justification for override
   - Explain mitigation plan for incomplete criteria
   - Get approval via issue comment from authorized person
   - Add `gate-override-approved` label to issue
   - Update CI workflow to check for override label

3. **Override Conditions**
   - External dependency blocking progress (e.g., hardware delivery)
   - Critical bug discovered requiring Phase 2 architecture
   - Research finding invalidating Phase 1 approach
   - Timeline pressure with acceptable risk mitigation

4. **Override Tracking**
   - All overrides are logged in `docs/PHASE1_OVERRIDES.md`
   - Override criteria must still be completed in parallel with Phase 2
   - Gate status badge shows 🟡 Conditional Pass during override

### Current Gate Status

**Status**: 🔴 **BLOCKED** - Gate criteria not yet met

**Last Updated**: 2025-11-17

**Completion Summary**:
- M1: ⏸️ Infrastructure ready, automated tests needed
- M2: ⏸️ SHACL shapes ready, validation tests needed
- M3: ⏸️ Test data ready, planning tests needed
- M4: ⏸️ Not started, requires Sophia/Talos/Apollo integration

**Next Steps**:
1. Implement M1 automated smoke tests
2. Implement M2 SHACL validation tests
3. Implement M3 planning tests
4. Complete manual demonstrations for M1-M3
5. Integrate components for M4 demo

---

## Testing Strategy

### Smoke Test Philosophy

Phase 1 smoke tests are designed to be:
- **Fast**: Run in < 5 minutes total
- **Reliable**: Deterministic, no flaky tests
- **Isolated**: Each milestone test is independent
- **Comprehensive**: Cover critical paths, not edge cases
- **Informative**: Clear failure messages pointing to root cause

### Test Organization

```
tests/
├── phase1/
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── valid_entities.ttl
│   │   ├── invalid_entities.ttl
│   │   ├── valid_processes.ttl
│   │   └── plan_scenarios.json
│   ├── test_m1_hcg_store_retrieve.py
│   ├── test_m2_shacl_validation.py
│   ├── test_m3_planning.py
│   └── test_m4_end_to_end.py
└── ...
```

### CI Integration

Smoke tests run on:
- Every push to `main` or `develop` branches
- Every pull request
- Nightly builds
- On-demand via `workflow_dispatch`

Smoke tests block:
- Merging to `main` branch
- Creating Phase 2 milestones
- Creating Phase 2 issues
- Creating Phase 2 branches

---

## References

- **Specification**: `docs/spec/project_logos_full.md`, Section 7.1
- **Ontology**: `ontology/core_ontology.cypher`
- **SHACL Shapes**: `ontology/shacl_shapes.ttl`
- **Test Data**: `ontology/test_data_pick_and_place.cypher`
- **Infrastructure**: `infra/docker-compose.hcg.dev.yml`
- **Milestones**: `milestones/Phase_1_HCG_and_Abstract_Pipeline.json`

---

## Changelog

- **2025-11-17**: Initial verification document created
- **TBD**: M1 manual demo completed
- **TBD**: M2 manual demo completed
- **TBD**: M3 manual demo completed
- **TBD**: M4 manual demo completed
- **TBD**: Gate passed, Phase 2 authorized
