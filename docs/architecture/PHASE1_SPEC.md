# Phase 1 Specification — HCG Foundation & Abstract Pipeline

Phase 1 establishes the core infrastructure for LOGOS: the Hierarchical Concept Graph (HCG) with Neo4j, ontology validation with SHACL, abstract planning capabilities, and an end-to-end demonstration of the Apollo → Sophia → Talos → HCG pipeline.

**Status**: ✅ COMPLETE (Verified 2025-11-19)

## Goals
1. **HCG Foundation** — Establish Neo4j as the persistent knowledge store with UUID-based entity management, constraint enforcement, and relationship traversal
2. **Ontology & Validation** — Define the core ontology in Cypher and implement SHACL-based validation to enforce data integrity
3. **Abstract Planning** — Demonstrate causal reasoning and temporal sequencing through a planning system that creates Process and State nodes
4. **End-to-End Pipeline** — Validate full system integration with a "pick and place" demonstration flowing through all components
5. **Infrastructure** — Provide Docker Compose definitions for reproducible development and CI environments

## Deliverables
- **Neo4j Database**
  - Constraint definitions for UUID uniqueness across node types
  - Index configurations for common query patterns
  - Docker image with n10s plugin for RDF/SHACL support
- **Core Ontology**
  - `ontology/core_ontology.cypher` — Entity, Concept, State, Process node schemas
  - `ontology/shacl_shapes.ttl` — SHACL constraints for validation
  - `ontology/test_data_pick_and_place.cypher` — Reference data for demos
- **Validation Service**
  - SHACL validation via n10s plugin or external service
  - Error detection for constraint violations
  - Validation hooks for data ingestion
- **Planning Infrastructure**
  - Process node creation with CAUSES relationships
  - State progression tracking with temporal ordering
  - Causal chain construction for multi-step operations
- **Test Suite**
  - `tests/integration/` — Comprehensive milestone tests (M1–M3)
  - `tests/e2e/test_phase1_end_to_end.py` — M4 end-to-end verification
  - CI workflows via `phase1-gate.yml`
  - Verification evidence in `logs/` directories
- **Documentation**
  - HCG data layer specification (`docs/hcg/`)
  - Infrastructure setup guides (`infra/README.md`)
  - Developer quickstart in main README

## Milestones

### P1-M1: Neo4j CRUD & Entity Management ✅

**Objective**: Establish Neo4j as the authoritative HCG store with proper entity management, constraints, and relationship support.

**Deliverables**:
- **Entity nodes**: Create, read, update, delete operations for `(:Entity)` nodes
- **Concept nodes**: Hierarchical concept definitions with `IS_A` relationships
- **State nodes**: Temporal state tracking for entities
- **Process nodes**: Action representations with parameters
- **UUID enforcement**: Unique identifiers with format `<type>_<uuid>` (e.g., `entity_abc123`)
- **Constraint definitions**: Uniqueness constraints on all node type IDs
- **Index creation**: Performance indexes for common query patterns
- **Relationship management**: `HAS_STATE`, `IS_A`, `LOCATED_AT`, `USES_TOOL`, etc.

**Success criteria**:
- All CRUD operations functional via Neo4j driver
- UUID constraints prevent duplicate entities
- Relationship traversal queries return expected results
- Entity-Concept associations established and queryable
- Test file: `tests/integration/ontology/test_neo4j_crud.py` — 47 tests passing

---

### P1-M2: SHACL Validation ✅

**Objective**: Implement schema validation using SHACL to ensure data integrity and catch constraint violations before they corrupt the graph.

**Deliverables**:
- **SHACL shapes loading**: Load `shacl_shapes.ttl` into Neo4j via n10s
- **Shape definitions**:
  - `EntityShape` — Required properties, ID format, allowed relationships
  - `StateShape` — Temporal constraints, entity linkage
  - `ProcessShape` — Parameter validation, input/output typing
  - `ConceptShape` — Hierarchy constraints, naming conventions
- **Validation service**: Endpoint or function to validate proposed data changes
- **Error detection**: Identify constraint violations with actionable error messages
- **Validation hooks**: Integration points for data ingestion pipelines

**Success criteria**:
- SHACL shapes load successfully into Neo4j
- Valid data passes validation without errors
- Invalid data (missing fields, wrong types, constraint violations) detected and rejected
- Error messages include specific violation details
- Test file: `tests/integration/ontology/test_shacl_validation.py` — SHACL integration verified

---

### P1-M3: Planning & Causal Reasoning ✅

**Objective**: Demonstrate abstract planning capabilities by generating multi-step action sequences with causal relationships.

**Deliverables**:
- **Planning scenarios**: Support for goal-directed action sequence generation
- **Causal relationships**: `CAUSES` edges linking Process nodes to resulting States
- **Temporal ordering**: `PRECEDES` relationships establishing action sequence
- **Grasp-Place sequences**: Multi-step manipulation plans (approach → grasp → move → place)
- **State transitions**: Track entity state changes through process execution
- **Process hierarchy**: Support for composite processes containing sub-processes
- **Precondition checking**: Validate required states before process execution

**Success criteria**:
- Planning generates valid 4-step pick-and-place sequences
- Causal chain verifiable: each Process CAUSES expected State
- Temporal ordering correct: PRECEDES relationships form valid sequence
- State nodes accurately reflect entity position/status changes
- Test file: `tests/integration/planning/test_planning_workflow.py` — Planning scenarios verified

---

### P1-M4: End-to-End Pick and Place ✅

**Objective**: Demonstrate complete system integration executing a pick-and-place task through the Apollo → Sophia → Talos → HCG pipeline.

**Deliverables**:
- **Component integration**:
  - Neo4j database running and accessible
  - Milvus vector store running and accessible (optional for Phase 1)
  - HCG infrastructure accessible to all components
  - Ontology loading successful
  - Test data loading successful
- **End-to-end flow**:
  - Apollo command simulation (user intent capture)
  - Goal state creation in HCG
  - Sophia plan generation (4-step sequence)
  - Plan storage with temporal ordering
  - Talos execution simulation
  - HCG state updates during execution
  - State verification showing final location
- **Observable outcomes**:
  - Entity nodes in HCG (manipulator, objects, workspace)
  - Process nodes for each action
  - State nodes showing progression
  - CAUSES relationships (causal chain)
  - PRECEDES relationships (temporal ordering)
  - Final state shows object in target location
  - UUID constraints enforced throughout

**Success criteria**:
- Full pipeline executes without errors
- All components communicate successfully
- HCG contains complete execution trace
- Final state matches expected goal state
- Verification evidence captured and documented
- Test file: `tests/e2e/test_phase1_end_to_end.py` — 22 tests passing

---

## Implementation Notes

### Infrastructure
- **Neo4j**: Version 5.13.0+ with APOC and n10s plugins
  - Docker image: `neo4j:5.13.0-enterprise` or community edition
  - Ports: 7474 (HTTP), 7687 (Bolt)
  - Configuration: `NEO4J_AUTH=neo4j/password`
- **Milvus**: Version 2.3.3+ for vector storage (optional in Phase 1)
  - Used for embedding storage and similarity search
  - Ports: 19530 (gRPC), 9091 (metrics)
- **SHACL Service**: Either n10s built-in or external validator
  - n10s plugin provides native Neo4j integration
  - External service option for complex validation scenarios

### Ontology Structure
```
(:Entity {entity_id, name, type})
  -[:HAS_STATE]->(:State {state_id, timestamp, properties})
  -[:IS_A]->(:Concept {concept_id, name, description})
  -[:LOCATED_AT]->(:Entity)  // spatial relationships

(:Process {process_id, name, parameters})
  -[:CAUSES]->(:State)       // causal chain
  -[:PRECEDES]->(:Process)   // temporal ordering
  -[:USES_TOOL]->(:Entity)   // capability dependencies

(:Concept)
  -[:IS_A]->(:Concept)       // concept hierarchy
```

### UUID Format
All entity identifiers follow the pattern `<type>_<uuid>`:
- `entity_abc123def456` — Entity nodes
- `concept_abc123def456` — Concept nodes
- `state_abc123def456` — State nodes
- `process_abc123def456` — Process nodes

### Docker Compose
Infrastructure defined in `infra/docker-compose.hcg.dev.yml`:
```yaml
services:
  neo4j:
    image: neo4j:5.13.0
    ports: ["7474:7474", "7687:7687"]
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc", "n10s"]'
  
  milvus:
    image: milvusdb/milvus:v2.3.3
    ports: ["19530:19530"]
  
  shacl-validator:
    # Optional external SHACL service
```

### CI Workflow
The `phase1-gate.yml` workflow validates all Phase 1 criteria:
1. Start infrastructure (Neo4j, optionally Milvus)
2. Load ontology and SHACL shapes
3. Run M1 tests (CRUD operations)
4. Run M2 tests (SHACL validation)
5. Run M3 tests (Planning scenarios)
6. Run M4 tests (End-to-end integration)
7. Generate coverage and verification evidence

## Verification Checklist

All Phase 1 milestones have been verified. Evidence is stored in `logs/p1-m{1-4}-verification/` directories.

- [x] **P1-M1**: Neo4j CRUD operations functional, constraints enforced, 47 tests passing
- [x] **P1-M2**: SHACL shapes loaded, validation catches invalid data, error messages actionable
- [x] **P1-M3**: Planning generates causal chains, temporal ordering correct, state transitions tracked
- [x] **P1-M4**: End-to-end pipeline verified, 22 integration tests passing, evidence documented

### Verification Evidence
- Test results: `tests/integration/` and `tests/e2e/test_phase1_end_to_end.py` — All milestone tests green
- Milestone JSON: `milestones/M4_End_to_End_Pick_and_Place.json` — Detailed acceptance criteria and results
- CI logs: GitHub Actions workflow runs for `phase1-gate.yml`

## Status Tracking
- Issues labeled `phase:1` with milestone-specific labels
- Phase 1 verification complete as of 2025-11-19
- All Phase 1 artifacts archived for reference

## References
- **HCG Data Layer**: `docs/hcg/HCG_DATA_LAYER.md`
- **Infrastructure Setup**: `infra/README.md`
- **Ontology Files**: `ontology/README.md`
- **Phase 1 Tests**: `tests/integration/`, `tests/e2e/test_phase1_end_to_end.py`
- **Milestone Records**: `milestones/Phase_1_HCG_and_Abstract_Pipeline.json`

> This document serves as the authoritative Phase 1 specification, mirroring the format of Phase 2 and Phase 3 specs. Phase 1 is complete and provides the foundation for all subsequent phases.
