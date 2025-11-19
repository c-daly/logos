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

### Phase 1 Readiness Delta (2025-11-19)

Recent discovery work identified a handful of documentation/UX gaps between the existing milestone gates and what we want to call a Phase 1 prototype. These are tracked with the `phase 1 closers` label:

- **#200** – Make the Neo4j SHACL smoke test/job opt-in but fully documented (how to enable via `RUN_NEO4J_SHACL` or workflow input).
- **#201** – Planner stub that exposes the API Sophia will ship; feeds the M4 script/CLI without relying on mocks hidden in tests.
- **#202** – Executor/Talos shim that updates the HCG deterministically so validation + retrieval demos stay consistent.
- **#203** – Apollo entrypoint (CLI/API) with the goal/plan/execute verbs the docs describe.
- **#204** – Milvus connectivity smoke to keep vector search healthy and documented for QA.
- **#205** – Stronger M4 assertions that reference the RobotArm UUID/name used in fixtures (no stale Manipulator text).
- **#206** – Cleanup/CI simplification so default test runs stay fast; heavy tests documented as opt-in.
- **#208** – Apollo CLI prototype wiring that exercises the entire goal → plan → execute loop end to end.

Until these issues close (and their doc updates merge), consider the Phase 1 gate “conditioned”—automation is green, but the UX/documentation surface still needs these finishing steps.

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

See: `tests/phase1/test_m1_neo4j_crud.py`

The automated test verifies:
- Neo4j connection and authentication
- Ontology script execution without errors
- Constraints and indexes created (entity UUID, concept UUID/name, state UUID, process UUID)
- Entity creation with UUID constraints and prefix validation (entity-*)
- Concept creation with UUID constraints and name uniqueness (concept-*)
- State creation with UUID constraints (state-*)
- Process creation with UUID constraints (process-*)
- Relationship creation (IS_A, HAS_STATE, CAUSES, PART_OF)
- Relationship traversal (type lookup via IS_A, current state via HAS_STATE, causal chains via CAUSES/PRECEDES, composition via PART_OF)
- Query operations (by UUID, by name, by timestamp)
- Constraint enforcement (UUID uniqueness, name uniqueness)

**Status**: ✅ Implemented - [![M1 Gate](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml) (26 tests passing)

---

## M2: SHACL Validation Catches Errors (Week 4)

### Objective
Demonstrate that SHACL validation rules successfully catch malformed graph updates and enforce data quality.

> Note: CI uses pyshacl for shape checks by default. Live Neo4j+n10s validation is opt-in; set `RUN_NEO4J_SHACL=1` and run `tests/phase1/test_shacl_neo4j_validation.py`, or enable a dedicated Neo4j validation job.

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

#### Option 1: SHACL Validation via Neo4j neosemantics (n10s) - **RECOMMENDED**

This approach validates data directly in Neo4j using the n10s plugin, which is closer to production usage.

1. **Start Neo4j with n10s plugin**
   ```bash
   cd infra
   docker-compose -f docker-compose.hcg.dev.yml up -d
   # Wait for Neo4j to be ready (check localhost:7474)
   ```

2. **Load SHACL Shapes into Neo4j**
   ```bash
   # Load core ontology first
   cat ontology/core_ontology.cypher | \
     docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev
   
   # Load SHACL shapes via n10s
   python ontology/load_and_validate_shacl.py \
     --uri bolt://localhost:7687 \
     --user neo4j \
     --password logosdev \
     --shapes ontology/shacl_shapes.ttl \
     --skip-validation
   ```

3. **Test with Valid Data**
   ```bash
   # Run validation against valid test fixtures
   python ontology/load_and_validate_shacl.py \
     --uri bolt://localhost:7687 \
     --user neo4j \
     --password logosdev \
     --shapes ontology/shacl_shapes.ttl \
     --test-data tests/phase1/fixtures/valid_entities.ttl \
     --clear
   
   # Expected output: ✓ VALIDATION PASSED
   ```

4. **Test with Invalid Data**
   ```bash
   # Run validation against invalid test fixtures
   python ontology/load_and_validate_shacl.py \
     --uri bolt://localhost:7687 \
     --user neo4j \
     --password logosdev \
     --shapes ontology/shacl_shapes.ttl \
     --test-data tests/phase1/fixtures/invalid_entities.ttl \
     --clear
   
   # Expected output: ✗ VALIDATION FAILED with detailed violation reports
   ```

5. **View Validation Results in Neo4j Browser**
   - Open http://localhost:7474 in browser
   - Login with neo4j/logosdev
   - Run queries to inspect loaded shapes and data:
     ```cypher
     // View loaded SHACL shapes
     MATCH (n) WHERE n.uri CONTAINS 'shacl' RETURN n LIMIT 10;
     
     // View validation violations (if any)
     CALL n10s.validation.shacl.validate() 
     YIELD focusNode, propertyShape, severity, resultMessage
     RETURN focusNode, propertyShape, severity, resultMessage;
     ```

#### Option 2: Standalone SHACL Validation with pyshacl

This approach validates RDF data files directly without Neo4j (useful for quick checks).

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

2. **Run SHACL Validation**
   ```python
   from rdflib import Graph
   from pyshacl import validate
   
   # Load shapes
   shapes_graph = Graph()
   shapes_graph.parse("ontology/shacl_shapes.ttl", format="turtle")
   
   # Load data to validate
   data_graph = Graph()
   data_graph.parse("tests/phase1/fixtures/valid_entities.ttl", format="turtle")
   
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

#### Standalone pyshacl Tests

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

**Status**: ✅ Implemented - [![M2 Gate](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml) (20 tests passing)

#### Neo4j n10s Integration Tests

See: `.github/workflows/shacl-neo4j-validation.yml`

The CI workflow verifies:
- Neo4j starts successfully with n10s plugin
- n10s graph configuration initializes correctly
- SHACL shapes load into Neo4j via n10s
- Valid test data passes SHACL validation in Neo4j
- Invalid test data correctly fails SHACL validation in Neo4j
- Validation reports provide detailed violation information

**Status**: ✅ Implemented - [![SHACL Neo4j Validation](https://github.com/c-daly/logos/actions/workflows/shacl-neo4j-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/shacl-neo4j-validation.yml)

**Script**: `ontology/load_and_validate_shacl.py`

The validation script provides:
- Automated n10s initialization in Neo4j
- SHACL shape loading from TTL files
- Test data loading and validation
- Detailed violation reporting
- Exit codes for CI integration (0 = pass, 1 = fail)

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

**Status**: ✅ Implemented - [![M3 Gate](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml) (11 tests passing)

---

## M4: End-to-End Pick-and-Place Demo (Week 8)

### Objective
Demonstrate the complete system integration: Apollo → Sophia → Talos → HCG, executing a pick-and-place task.

> Note: The full M4 end-to-end test is opt-in. Set `RUN_M4_E2E=1` (or run the workflow with `skip_e2e=false`) to execute the slow flow; by default CI skips it.

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

#### Option 1: Automated E2E Script (Recommended)

The easiest way to run the end-to-end demo is using the provided script:

1. **Start HCG Infrastructure**
   ```bash
   cd infra
   docker compose -f docker-compose.hcg.dev.yml up -d
   # Wait for Neo4j to be ready (check localhost:7474)
   ```

2. **Run the E2E Script**
   ```bash
   ./scripts/e2e_prototype.sh
   ```

   The script will automatically:
   - Verify infrastructure is running
   - Load core ontology and SHACL shapes
   - Load pick-and-place test data
   - Simulate Apollo command (goal state creation)
   - Simulate Sophia plan generation (4-step plan)
   - Simulate Talos execution (state updates)
   - Verify state changes in HCG
   - Capture logs and create summary report

3. **Review Results**
   ```bash
   # View summary report
   cat logs/e2e/summary.txt
   
   # View detailed logs
   ls -la logs/e2e/
   ```

   Expected output:
   ```
   LOGOS Prototype End-to-End Test Summary
   ========================================
   1. ✓ Infrastructure started
   2. ✓ Ontology and SHACL loaded
   3. ✓ Test data loaded
   4. ✓ Apollo command simulated
   5. ✓ Sophia plan generated (4 steps)
   6. ✓ Talos execution simulated
   7. ✓ State changes verified
   8. ✓ Logs captured
   
   Result: SUCCESS
   ```

#### Option 2: Manual Step-by-Step Demo

For detailed control or debugging, follow these manual steps:

1. **Start All Services**
   ```bash
   # Start HCG infrastructure
   docker-compose -f infra/docker-compose.hcg.dev.yml up -d
   
   # (Optional) Start Hermes (in c-daly/hermes repo)
   cd ../hermes && docker-compose up -d
   
   # (Optional) Start Talos in simulation mode (in c-daly/talos repo)
   cd ../talos && python -m talos.simulator
   
   # (Optional) Start Sophia (in c-daly/sophia repo)
   cd ../sophia && python -m sophia.orchestrator
   
   # (Optional) Start Apollo UI (in c-daly/apollo repo)
   cd ../apollo && npm start
   ```

2. **Load Initial State**
   ```bash
   # Load pick-and-place ontology and test data
   cat ontology/core_ontology.cypher | docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev
   cat ontology/test_data_pick_and_place.cypher | docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev
   ```

3. **Execute Demo via Apollo (or manual queries)**
   
   If using Apollo UI:
   - Open Apollo UI in browser (localhost:3000 or configured port)
   - Enter command: "Pick up the red block and place it in the bin"
   - Observe plan generation in UI
   - Observe execution progress
   - Observe state updates in real-time
   - Confirm success message
   
   If testing manually with Cypher queries:
   ```cypher
   // Create goal state
   CREATE (g:State {
       uuid: 'state-goal-' + randomUUID(),
       name: 'GoalState_RedBlockInBin',
       timestamp: datetime(),
       description: 'Red block should be in the target bin',
       is_goal: true
   }) RETURN g.uuid, g.name;
   
   // Create plan processes
   CREATE (p1:Process {uuid: 'process-plan-1', name: 'MoveToPreGrasp', start_time: datetime()})
   CREATE (p2:Process {uuid: 'process-plan-2', name: 'GraspRedBlock', start_time: datetime()})
   CREATE (p3:Process {uuid: 'process-plan-3', name: 'MoveToPlace', start_time: datetime()})
   CREATE (p4:Process {uuid: 'process-plan-4', name: 'ReleaseBlock', start_time: datetime()})
   CREATE (p1)-[:PRECEDES]->(p2)
   CREATE (p2)-[:PRECEDES]->(p3)
   CREATE (p3)-[:PRECEDES]->(p4)
   RETURN p1.name, p2.name, p3.name, p4.name;
   ```

4. **Verify HCG Updates**
   ```cypher
   // Check final state of red block
   MATCH (e:Entity)-[:HAS_STATE]->(s:State)
   WHERE e.name CONTAINS 'RedBlock'
   RETURN e.name, s.name, s.description, s.timestamp
   ORDER BY s.timestamp DESC LIMIT 3;
   
   // Verify location update (if LOCATED_AT relationship exists)
   MATCH (e:Entity)-[:LOCATED_AT]->(t:Entity)
   WHERE e.name CONTAINS 'RedBlock'
   RETURN e.name, t.name;
   
   // Trace execution history
   MATCH (p:Process)-[:PRECEDES*0..]->(next:Process)
   WHERE p.name CONTAINS 'Move' OR p.name CONTAINS 'Grasp' OR p.name CONTAINS 'Release'
   RETURN p.name, p.description LIMIT 10;
   ```

5. **Verify SHACL Compliance**
   ```python
   # Export HCG state and validate against SHACL
   # All state updates should conform to shapes
   # (This can be automated in future iterations)
   ```

#### Troubleshooting

**Neo4j not starting:**
```bash
# Check container logs
docker logs logos-hcg-neo4j

# Restart containers
cd infra && docker compose -f docker-compose.hcg.dev.yml restart
```

**Ontology already loaded errors:**
- This is expected if you run the script multiple times
- Constraints and indexes can only be created once
- The script handles this gracefully

**No test data found:**
```bash
# Manually verify test data
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "MATCH (e:Entity) RETURN e.name, e.uuid LIMIT 10;"
```

**E2E script permission denied:**
```bash
chmod +x scripts/e2e_prototype.sh
```

### Automated Smoke Tests

See: `tests/phase1/test_m4_end_to_end.py`

The automated test verifies:
- Infrastructure startup (Neo4j + Milvus containers)
- Ontology and constraint loading
- Pick-and-place test data loading
- Simulated Apollo command (goal state creation)
  - **Expected Outcome**: Goal state created with specific UUID and properties (is_goal=true, description contains target)
- Simulated Sophia plan generation (process nodes with temporal ordering)
  - **Expected Outcome**: 4-step plan created (MoveToPreGrasp → Grasp → MoveToPlace → Release)
  - **Expected Outcome**: All processes have valid UUIDs and are connected by PRECEDES relationships
  - **Expected Outcome**: Process chain length = 3 (connecting 4 processes)
- Simulated Talos execution (state updates in HCG)
  - **Expected Outcome**: Block state changes from is_grasped=false to is_grasped=true during grasp
  - **Expected Outcome**: Block state changes to is_grasped=false after release
  - **Expected Outcome**: Block entity has LOCATED_AT relationship to TargetBin01
  - **Expected Outcome**: Gripper state changes from is_closed=false to is_closed=true during grasp
  - **Expected Outcome**: Processes have CAUSES relationships to resulting states
- State verification queries
  - **Expected Outcome**: Specific entities exist with known UUIDs (entity-robot-arm-01, entity-block-red-01, entity-bin-01)
  - **Expected Outcome**: Robot arm entity has name 'RobotArm01' (not generic 'Manipulator')
  - **Expected Outcome**: Gripper is PART_OF robot arm
  - **Expected Outcome**: Block has initial state with position coordinates and is_grasped=false
  - **Expected Outcome**: Final state shows block at target position (0.5, 0.3, 0.8) in bin
- E2E script execution (optional, marked as slow test)

#### Test Resilience
All M4 tests use MERGE with UUID guards to ensure:
- Tests can be run multiple times without creating duplicate data
- Idempotent operations allow CI re-runs without database cleanup
- Specific UUIDs prevent conflicts between test runs

#### Expected Data Assertions
The M4 tests assert specific expected state after each workflow step:

**After Goal Creation:**
- State node exists with UUID 'state-goal-test-m4-redblock'
- State has property is_goal=true
- State description contains "red block in bin"

**After Plan Generation:**
- Four Process nodes exist with specific UUIDs
- Processes are named: TestMoveToPreGrasp, TestGraspRedBlock, TestMoveToPlace, TestReleaseBlock
- PRECEDES relationships form complete chain (length=3)
- Each process has descriptive name and start_time

**After Execution (Grasp Step):**
- RedBlock01 entity (entity-block-red-01) has new state
- State has is_grasped=true
- Gripper01 entity (entity-gripper-01) has closed state
- GraspRedBlock process has CAUSES relationships to both states

**After Execution (Release Step):**
- RedBlock01 has final state with is_grasped=false
- Final state has position (0.5, 0.3, 0.8)
- RedBlock01 has LOCATED_AT relationship to TargetBin01
- ReleaseBlock process has CAUSES relationships to final states

**Entity Verification:**
- RobotArm01 exists with UUID entity-robot-arm-01
- Gripper01 exists with UUID entity-gripper-01 and is PART_OF RobotArm01
- RedBlock01 exists with UUID entity-block-red-01
- TargetBin01 exists with UUID entity-bin-01
- TargetBin01 is LOCATED_AT WorkTable01

**E2E Script**: `scripts/e2e_prototype.sh`

The script provides:
- Automated infrastructure verification
- Complete workflow simulation (Apollo → Sophia → Talos → HCG)
- State change verification
- Log capture and summary reporting
- Exit codes for CI integration (0 = pass, 1 = fail)

**Status**: ✅ Implemented - [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml)

**CI Integration**:
- E2E tests run on every push to main/develop
- Optional skip flag for quick validation (`skip_e2e=true`)
- Weekly scheduled runs on Mondays
- Logs and artifacts uploaded for debugging

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
- [x] M1: [![M1 Gate](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml) `test_m1_neo4j_crud.py` passes (26 tests)
- [x] M2: [![M2 Gate](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml) `test_m2_shacl_validation.py` passes
- [x] M3: [![M3 Gate](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml) `test_m3_planning.py` passes
- [x] M4: [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml) `test_m4_end_to_end.py` passes + E2E script
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

The gate is enforced through individual milestone workflows that produce badges:

1. **Milestone-Specific CI Workflows**
   - **M1 (HCG Store/Retrieve)**: `.github/workflows/m1-neo4j-crud.yml` - [![M1 Gate](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml)
   - **M2 (SHACL Validation)**: `.github/workflows/m2-shacl-validation.yml` - [![M2 Gate](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml)
   - **M3 (Planning)**: `.github/workflows/m3-planning.yml` - [![M3 Gate](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml)
   - **M4 (End-to-End Demo)**: `.github/workflows/m4-end-to-end.yml` - [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml)
   - Each workflow runs automated tests for its milestone
   - Workflows run on every push, PR, and weekly schedule
   - Badge shows real-time pass/fail status for each milestone

2. **GitHub Branch Protection**
   - Main branch requires passing CI before merge
   - All milestone badges must be green before Phase 2 begins
   - Phase 1 milestone must be closed before Phase 2 milestone opens

3. **Project Board**
   - Phase 2 issues are hidden until all gates pass
   - Automation moves completed Phase 1 issues to "Done"
   - Milestone badge status visible in README and docs

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

**Overall Status**: 🟢 **Automated Tests Passing** | ⏸️ **Manual/UX Readiness Pending**

**Last Updated**: 2025-11-19

**Milestone Badge Status**:
- **M1** (HCG Store/Retrieve): [![M1 Gate](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml) - 26 tests passing
- **M2** (SHACL Validation): [![M2 Gate](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml) - 20 tests passing
- **M3** (Planning): [![M3 Gate](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml) - 11 tests passing
- **M4** (End-to-End Demo): [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml) - Integration tests + E2E script

**Next Steps**:
1. Run M4 end-to-end script to verify prototype integration
2. Complete M4 manual demonstration
3. Test with real Apollo/Sophia/Talos components (optional for Phase 1)
4. Close the remaining `phase 1 closers` tickets (#200, #201, #202, #203, #204, #205, #206, #208) and land the doc/CLI improvements they track

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
