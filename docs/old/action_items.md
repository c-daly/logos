# Project LOGOS — Action Items and Task Breakdown

This document captures the actionable tasks for initializing and executing Phase 1 of Project LOGOS.

## 1. Repository and Project Infrastructure Setup

### 1.1 Finalize Repository Structure

- [x] **c-daly/logos** — Meta-repository (foundry)
  - [x] Create core ontology scaffold (`ontology/core_ontology.cypher`)
  - [x] Create SHACL shapes (`ontology/shacl_shapes.ttl`)
  - [x] Create Hermes API contract (`contracts/hermes.openapi.yaml`)
  - [x] Create HCG dev infrastructure (`infra/docker-compose.hcg.dev.yml`)
  - [x] Add full specification (`docs/spec/project_logos_full.md`)
  - [x] Add action items tracking (`docs/action_items.md`)
  - [x] Set up CI/CD for validation tests

- [ ] **c-daly/sophia** — Cognitive core repository
  - [ ] Initialize Python project structure
  - [ ] Set up dependency management (Poetry/pipenv)
  - [ ] Create skeleton modules: Orchestrator, CWM-A, CWM-G, Planner, Executor
  - [ ] Add unit test framework (pytest)
  - [ ] Create docker-compose for local development

- [ ] **c-daly/hermes** — Language utility repository
  - [ ] Initialize Python project structure
  - [ ] Implement FastAPI application skeleton
  - [ ] Implement `/stt` endpoint stub
  - [ ] Implement `/tts` endpoint stub
  - [ ] Implement `/simple_nlp` endpoint stub
  - [ ] Implement `/embed_text` endpoint stub
  - [ ] Add OpenAPI validation tests
  - [ ] Create Dockerfile

- [ ] **c-daly/talos** — Hardware abstraction repository
  - [ ] Initialize Python project structure
  - [ ] Define sensor/actuator interface abstractions
  - [ ] Implement simulated sensors (camera, depth, IMU)
  - [ ] Implement simulated actuators (motors, grippers)
  - [ ] Add mock hardware for Phase 1 testing

- [ ] **c-daly/apollo** — UI/client repository
  - [ ] Initialize Node.js/React project
  - [ ] Create basic dashboard layout
  - [ ] Add HCG visualization component (graph view)
  - [ ] Add command input interface
  - [ ] Add real-time state monitoring display

### 1.2 Project Board and Issue Tracking

**Note:** Infrastructure created. See `docs/QUICK_START_PROJECT_BOARD.md` for setup instructions.

- [ ] Create GitHub Project board for LOGOS (infrastructure ready in `.github/project_config.yml`)
- [ ] Set up milestone: "Phase 1 — HCG and Abstract Pipeline" (see `.github/PROJECT_BOARD_SETUP.md`)
- [ ] Create issues for all Phase 1 tasks (use `.github/scripts/generate_issues.py`)
- [x] Establish labeling system: `component:sophia`, `component:hermes`, `priority:high`, etc. (see `.github/labels.yml`)
- [x] Set up weekly progress tracking (see `.github/workflows/weekly-progress.yml`)

### 1.3 Database and Infrastructure Setup

- [x] Neo4j + Milvus development cluster (docker-compose)
- [ ] Initialize Neo4j with neosemantics plugin
- [ ] Load core ontology constraints into Neo4j
- [ ] Set up SHACL validation endpoint
- [ ] Configure Milvus collections for embeddings
- [ ] Create backup/restore scripts for development data
- [ ] Document infrastructure setup in logos README

## 2. Phase 1 Development — Three Workstreams

Reference: Section 7.1 of the full specification

### Workstream A: HCG Foundation and Validation

**Owner**: TBD  
**Duration**: Weeks 1-4  
**Dependencies**: Repository setup complete

**Tasks**:

- [ ] **A1: Extend core ontology** (Section 4.1, Appendix A)
  - [ ] Define all entity types for "pick and place" scenario
  - [ ] Define all relationship types (IS_A, HAS_STATE, CAUSES, PART_OF, etc.)
  - [ ] Add property schemas for entities (position, orientation, etc.)
  - [ ] Create Cypher scripts for test data population

- [ ] **A2: Implement SHACL validation** (Section 4.3.1)
  - [ ] Extend SHACL shapes for all entity types
  - [ ] Add relationship cardinality constraints
  - [ ] Add property datatype constraints
  - [ ] Create SHACL validation test suite (valid and invalid cases)
  - [ ] Integrate SHACL validation into Neo4j workflow

- [ ] **A3: Vector integration** (Section 4.2)
  - [ ] Design embedding schema in Milvus
  - [ ] Implement sync mechanism between Neo4j and Milvus
  - [ ] Add embedding_id properties to graph nodes
  - [ ] Create embedding generation pipeline (using Hermes)

- [ ] **A4: HCG query utilities**
  - [ ] Write Cypher queries for common graph operations (find entity, traverse causality, etc.)
  - [ ] Create Python client library for HCG access
  - [ ] Add connection pooling and error handling
  - [ ] Write integration tests for HCG operations

### Workstream B: Sophia Cognitive Core Prototype

**Owner**: TBD  
**Duration**: Weeks 3-8  
**Dependencies**: A1-A2 complete, Hermes endpoints available

**Tasks**:

- [ ] **B1: Orchestrator implementation** (Section 3.3)
  - [ ] Design control flow state machine
  - [ ] Implement subsystem registration and lifecycle management
  - [ ] Add inter-subsystem message passing
  - [ ] Create Orchestrator integration tests

- [ ] **B2: CWM-A (Abstract World Model)** (Section 3.3)
  - [ ] Design abstract state representation structure
  - [ ] Implement state update mechanism (read from HCG)
  - [ ] Implement state query API for Planner
  - [ ] Add state change event emission
  - [ ] Write unit tests for CWM-A

- [ ] **B3: Planner (initial version)** (Section 3.3)
  - [ ] Implement graph traversal-based planning
  - [ ] Define goal representation in HCG
  - [ ] Implement backward chaining from goal to current state
  - [ ] Generate action sequences (plans)
  - [ ] Add plan validation against SHACL constraints
  - [ ] Write planning test cases (simple scenarios)

- [ ] **B4: Executor (stub)** (Section 3.3)
  - [ ] Define execution interface (receive plans)
  - [ ] Implement plan step iteration
  - [ ] Add success/failure callback mechanism
  - [ ] Stub out Talos integration (simulated execution)

- [ ] **B5: End-to-end integration**
  - [ ] Wire up Orchestrator → CWM-A → Planner → Executor flow
  - [ ] Implement simple command: "Pick up cup"
  - [ ] Verify HCG updates occur correctly
  - [ ] Verify SHACL validation gates malformed updates

### Workstream C: Hermes and Support Services

**Owner**: TBD  
**Duration**: Weeks 2-6  
**Dependencies**: Hermes repository initialized

**Tasks**:

- [ ] **C1: Implement Hermes endpoints** (Section 3.4, Table 2)
  - [ ] `/stt` — Integrate Whisper or similar STT model
  - [ ] `/tts` — Integrate Coqui TTS or similar
  - [ ] `/simple_nlp` — Integrate spaCy for tokenization, POS, NER
  - [ ] `/embed_text` — Integrate sentence-transformers or OpenAI embeddings
  - [ ] Add request validation and error handling
  - [ ] Write API integration tests

- [ ] **C2: Hermes deployment**
  - [ ] Create Dockerfile for Hermes
  - [ ] Add to docker-compose for local testing
  - [ ] Document API usage and examples
  - [ ] Set up health check endpoint

- [ ] **C3: Talos simulated interfaces**
  - [ ] Implement simulated sensor data generation
  - [ ] Implement simulated actuator command reception
  - [ ] Create "pick and place" scenario simulation
  - [ ] Add visualization of simulated environment (optional)

- [ ] **C4: Apollo command interface (basic)**
  - [ ] Create CLI tool for sending commands to Sophia
  - [ ] Add command history and logging
  - [ ] Display agent state and plan status
  - [ ] (Stretch) Add simple web UI

## 3. Research and Outreach Tasks

### 3.1 Research Sprints

- [ ] **R1: Survey of causal reasoning methods**
  - Literature review: causal inference, counterfactual reasoning
  - Evaluate applicability to HCG-based planning
  - Document findings in `docs/research/causal_reasoning.md`

- [ ] **R2: Graph neural network integration**
  - Investigate GNN architectures for graph-based reasoning
  - Prototype GNN-based node classification on HCG
  - Assess performance vs. symbolic methods

- [x] **R3: Multi-modal grounding**
  - Research sensor fusion techniques
  - Design architecture for vision + proprioception integration
  - Plan for Phase 2 implementation
  - Document findings in `docs/research/multi_modal_grounding.md`

### 3.2 Outreach and Collaboration

- [ ] **O1: Publish blog post** — "Non-linguistic Cognition: Why Graphs Matter"
  - Explain LOGOS vision and HCG approach
  - Contrast with LLM-only architectures
  - Share on relevant communities (HN, Reddit r/MachineLearning, etc.)

- [ ] **O2: Create demo video**
  - Record "pick and place" scenario execution
  - Show HCG visualization during planning
  - Narrate design decisions and architecture

- [ ] **O3: Open-source release**
  - Prepare all repositories for public release
  - Write contributor guidelines
  - Add LICENSE files (MIT/Apache 2.0)
  - Announce on social media and GitHub

- [ ] **O4: Engage with research community**
  - Reach out to cognitive architecture researchers
  - Submit to workshops: NeurIPS, ICRA, AAAI
  - Seek feedback from domain experts

## 4. Testing and Validation Milestones

- [ ] **M1: HCG can store and retrieve entities** (End of Week 2)
  - Neo4j + Milvus operational
  - Core ontology loaded
  - Basic CRUD operations working

- [ ] **M2: SHACL validation catches errors** (End of Week 4)
  - Invalid graph updates rejected
  - Valid graph updates accepted
  - Test suite passes

- [ ] **M3: Sophia can plan simple actions** (End of Week 6)
  - Given goal "cup is on table", generate plan
  - Plan includes necessary causal steps
  - Plan validates against ontology

- [ ] **M4: End-to-end "pick and place"** (End of Week 8)
  - User command → Sophia planning → simulated execution
  - HCG updates reflect state changes
  - Execution succeeds or fails gracefully

## 5. Documentation and Knowledge Management

- [ ] **D1: Architecture Decision Records (ADRs)**
  - Set up ADR template in `docs/adr/`
  - Document: "Why Neo4j for HCG", "Why SHACL for validation", etc.

- [ ] **D2: Developer onboarding guide**
  - Write `docs/CONTRIBUTING.md`
  - Create setup tutorial for new developers
  - Record common troubleshooting steps

- [ ] **D3: API documentation**
  - Auto-generate docs from OpenAPI specs
  - Add usage examples for all endpoints
  - Publish to GitHub Pages

- [ ] **D4: Weekly progress reports**
  - Maintain changelog in each repository
  - Post weekly updates to project board
  - Hold weekly sync meetings (document notes)

## 6. Risk Management

### Identified Risks

1. **Technical Risk**: Neo4j + Milvus integration complexity
   - Mitigation: Start with simple sync, iterate
   - Fallback: Decouple stores initially, sync later

2. **Scope Risk**: Phase 1 timeline too aggressive
   - Mitigation: Prioritize core features, defer nice-to-haves
   - Checkpoint: Review progress at Week 4

3. **Dependency Risk**: Hermes model availability/licensing
   - Mitigation: Use permissive open-source models (Whisper, Coqui)
   - Fallback: Implement stubs if models unavailable

4. **Knowledge Risk**: Team unfamiliarity with graph databases
   - Mitigation: Allocate learning time, share resources
   - Support: Schedule pair programming sessions

---

**Document Status**: Living task tracker — updated weekly
**Next Review**: Weekly on Mondays
**Last Updated**: 2025-11-16
