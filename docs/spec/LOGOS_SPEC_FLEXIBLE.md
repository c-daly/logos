# Project LOGOS — Flexible Specification

This document supersedes the original full specification. It folds in every relevant requirement from the prior spec, records the work delivered during Phase 1, and codifies the flexible deployment philosophy that now guides the roadmap. Treat this file as the single source of truth for architecture, ontology, infrastructure, and milestone expectations. Phase-specific deliverables now live under `docs/phase1/`, `docs/phase2/`, etc., while archival references were moved into `docs/old/`.

---

## 1. Introduction and Vision

Project LOGOS is a foundational research initiative to build a non-linguistic cognitive architecture for autonomous agents. The system revolves around the Hybrid Cognitive Graph (HCG), a graph-based knowledge representation that blends symbolic reasoning with vector-based semantic search.

### 1.1 Core Philosophy
- **Non-linguistic cognition first**: Internal reasoning occurs in abstract causal graph structures, not natural language.
- **Language as interface**: Natural language is a transport layer handled by Apollo/Hermes, not Sophia’s substrate of thought.
- **Causal coherence**: All reasoning maintains explicit causal relationships and temporal ordering.
- **Validation by constraint**: Deterministic (SHACL) and probabilistic validation layers guard every mutation of the HCG.
- **Capability-first deployment**: The same APIs must work whether Talos is simulated, connected to a single manipulator, or orchestrating a fleet of drones.
- **Dual causal world models**: LOGOS fuses commonsense structure (HCG) with a grounded physics learner (e.g., JEPA-style joint embedding predictive architecture) so the agent reasons over both symbolic and embodied cause/effect.

### 1.2 System Goals
1. Deliver a working prototype of the non-linguistic cognitive architecture.
2. Demonstrate superior causal reasoning versus purely linguistic LLM agents.
3. Establish reusable patterns for HCG-centric agent development.
4. Provide an extensible platform for research teams to add capabilities or embodiments without rewriting Sophia or the HCG.
5. Act as a **causal co-processor** for multimodal LLMs—feeding them grounded context, validating outputs against the HCG, and augmenting their perception with world-model predictions.

### 1.3 Embodiment Flexibility
Sophia + LOGOS (Neo4j + Milvus) are the only mandatory components. All other subsystems (Talos, Apollo, Hermes, physical hardware, touchscreens, voice assistants, etc.) are optional adapters that speak well-defined contracts. Deployments may range from a CLI-only assistant to a multi-robot system; the spec and tooling must support the entire spectrum.

### 1.4 Phase Roadmap
1. **Phase 1 – Formalize HCG & Abstract Pipeline** (docs/phase1)  
   Bootstrap the HCG, SHACL guardrails, CLI prototype, and opt-in heavy tests.
2. **Phase 2 – Perception & Apollo UX** (docs/phase2)  
   Ship Sophia/Hermes services, Apollo browser + CLI, perception pipeline, diagnostics/persona, and Talos-optional workflows.
3. **Phase 3 – Learning & Embodiment Options** (docs/phase3, forthcoming)  
   Add episodic memory, probabilistic validation, and optional physical demos (manipulator, touchscreen, drone) plus multi-agent prep.
4. **Phase 4 – Operational Autonomy** (docs/phase4, forthcoming)  
   Focus on continuous learning with safety gates, observability/rollback tooling, and production deployment patterns.
5. **Phase 5 – Networked Agents / Swarm** (docs/phase5, forthcoming)  
   Coordinate multiple LOGOS instances, share HCG slices, and orchestrate Talos fleets or swarm-style deployments.

---

## 2. System Architecture Overview

### 2.1 Components
1. **Sophia** — Non-linguistic cognitive core (Orchestrator, CWM-A, CWM-G, Planner, Executor).
2. **Hermes** — Stateless language + embedding utilities (STT/TTS/NLP/embedding endpoints).
3. **Talos** — Capability bus / hardware abstraction layer (simulated or physical).
4. **Apollo** — User interaction surface (CLI, touchscreen, kiosk, voice, etc.).
5. **LOGOS meta-repo** — Formal spec, ontology, contracts, infra, tooling.

### 2.2 Data Flow
```
User → Apollo → Sophia ↔ LOGOS HCG (Neo4j + Milvus)
                  ↓
              Hermes (STT/TTS/NLP/Embed)
                  ↓
              Talos (Simulators / Hardware)
```

### 2.3 Architecture Diagram
```
+-----------------+        +------------------+        +------------------+
|     Apollo      |<-API-> |      Sophia      |<-API-> |      Hermes      |
| (CLI/touch/VA)  |        |  (Planner/etc.)  |        | (STT/TTS/NLP)    |
+--------^--------+        +---------^--------+        +------------------+
         | \_______________________________________________/
         |              |
         | Commands / Plans + UX requests (direct Hermes calls)
         v                           v
+--------------------------------------------------------------+
|                         LOGOS HCG                            |
|    Neo4j + Milvus + SHACL: canonical state, plan, intent     |
+-------------------------^------------------------------------+
                          |
                          | Capabilities (sim or hardware)
                          v
                  +-----------------+
                  |      Talos      |
                  | (Capability Bus)|
                  +-----------------+
```

Sophia’s Orchestrator keeps the causal world models synchronized around this diagram. Every Talos capability invocation first runs through the grounded model (JEPA/simulator) to predict physics outcomes, then reconciles with the HCG to maintain commonsense consistency. Even if no Talos hardware is present, CWM-G may consume media streams (video frames, images, depth maps) coming from Apollo/Hermes clients to predict the next frame, label what is happening, or explain visual context into the graph. Optional CWM-E passes over the same memories/persona entries to attach affective signals (“confident”, “cautious”) that planners and Apollo can honor. The simulation hook in CWM-G (`simulate(capability, context)`) lets the agent “imagine” hypothetical outcomes before taking real action.

### 2.4 Deployment Modes

| Mode | Description | Required Components |
|------|-------------|---------------------|
| **Graph-only** | CLI/desk widget manipulating the HCG; no hardware. Causal world models still operate over stored data or streamed media (e.g., predict next video frame or explain an image). Talos is not required in this mode. | Apollo CLI, Sophia, LOGOS (Neo4j + Milvus) |
| **Perception-only** | Browser/mobile client streams video/images/audio to Hermes/Sophia. System predicts next frames, labels scenes, or explains events directly into the HCG with no Talos involvement. | Apollo/Hermes client, Sophia, LOGOS |
| **Simulated embodied** | Talos executes deterministic simulators (current Phase 1 setup). | Apollo CLI, Sophia, LOGOS, Talos simulators |
| **Physical embodied** | Talos connects to robots/drones/IoT devices. | Apollo (any UI), Sophia, LOGOS, Talos drivers |
| **Hybrid** | Mix of simulators and hardware, possibly multiple Apollo surfaces. | All of the above as needed |

Documentation, tooling, and acceptance tests must describe configuration via feature flags/env vars instead of hard-coded hardware references.

---

## 3. Component Specifications

### 3.1 LOGOS Meta-Repository
Serves as the canonical source for:
- Formal specification (this document) and design artifacts.
- Ontology definition (`ontology/core_ontology.cypher`).
- Validation constraints (`ontology/shacl_shapes.ttl`).
- API contracts (`contracts/*.openapi.yaml`).
- Development infrastructure (`infra/docker-compose.hcg.dev.yml`).
- Automation scripts (issue generation, validation, CI helpers).

### 3.2 Hybrid Cognitive Graph (HCG)
- **Graph database (Neo4j)** stores entities, concepts, states, processes, and relationships.
- **Vector store (Milvus)** holds embeddings for semantic retrieval.
- **Bidirectional sync** ensures graph nodes know their embeddings (`embedding_id`, `embedding_model`, `last_sync`).
- **Validation** occurs through SHACL (Level 1) and future probabilistic checks (Level 2).

### 3.3 Sophia — Cognitive Core
Subsystems:
1. **Orchestrator** — Coordinates perception, planning, and execution loops.
2. **CWM-A** — Abstract world model derived from the HCG.
3. **CWM-G** — Grounded model tied to Talos capabilities (sensors/actuators or simulation).
4. **Planner** — Generates action/process graphs over HCG state.
5. **Executor** — Applies plans and monitors results via Talos.

Sophia maintains *multi-layer causal world models*. CWM-A captures commonsense structure—relationships, affordances, and temporal rules encoded in the HCG. CWM-G captures grounded physics or perceptual dynamics: predictions of how the environment changes when a capability fires or how the next observation (video frame, image, sensor reading) should look. CWM-G can be implemented using JEPA-style joint embedding predictive architectures, simulators, or other differentiable models. Plans are only accepted when they are validated against both models: the abstract layer ensures semantic correctness, and the grounded layer enforces physical plausibility (e.g., mass/inertia, reachability, safety) or perceptual consistency. A third optional layer, **CWM-E (emotional/social)**, reflects on stored memories/persona entries to infer confidence, trust, or other affective signals. CWM-E writes its conclusions back into the HCG (e.g., tagging processes or entities with emotional state) so planners and the Apollo language layer can adjust behavior and tone. Additional specialized models can be added later without changing the contracts.

**Imagination / Simulation**: CWM-G doubles as a short-horizon simulator. Sophia exposes a `simulate(capability, context)` call that rolls out JEPA-based predictions (or a Talos/Gazebo backend when available). This lets the agent “imagine” outcomes—e.g., testing whether a jump clears a barrier or whether a grasp succeeds—before updating the HCG. Imagined states are recorded with metadata so Apollo/Hermes can explain the reasoning.

All reasoning happens in graph structures; natural language never enters internal processing.

### 3.4 Hermes — Language & Embedding Utility
Hermes exposes stateless endpoints:

| Endpoint | Function | Input | Output |
|----------|----------|-------|--------|
| `/stt` | Speech-to-text | Audio | Transcript |
| `/tts` | Text-to-speech | Text | Audio |
| `/simple_nlp` | NLP preprocessing | Text | Tokens/POS/NER |
| `/embed_text` | Text embedding | Text | Vector |

It never writes to the HCG and can be swapped for alternative providers as long as contracts hold.

### 3.5 Talos & Apollo — Capability Surfaces
- **Talos** exposes a capability graph describing what actions are available (simulate pick/place, move drone waypoint, send notification, etc.). Implementations may be pure simulation (Phase 1), physical drivers, or hybrids. Deployments that do not require actuation may omit Talos entirely; Sophia will operate purely over HCG updates and perceptual inputs.
- **Apollo** represents any interaction surface calling the Goal/Plan/State APIs. Today this is a CLI with GitHub Action summaries; Phase 2 will add a browser-based interface alongside the CLI so both experiences can be demonstrated. Longer term this could extend to kiosk or voice UIs. Multiple Apollo clients can coexist. Apollo can also embed a multimodal LLM that calls Sophia as a causal co-processor—LLM outputs are validated against the HCG, and Sophia feeds back grounded context, predicted frames, or structured explanations. Every Apollo surface must expose diagnostics, visualizations, and explainability views so stakeholders can inspect graph changes, planner rationale, and Talos telemetry.

---

## 4. HCG Ontology and Data Model

### 4.1 Core Ontology
Node types:
1. **Entity** — Concrete objects/agents (e.g., "RobotArm01", "TaskBoard").
2. **Concept** — Abstract categories (e.g., "Manipulator", "Workspace").
3. **State** — Temporal snapshots of entity properties.
4. **Process** — Causal transformations between states.

Key relationships:
- `(:Entity)-[:IS_A]->(:Concept)`
- `(:Entity)-[:HAS_STATE]->(:State)`
- `(:Process)-[:CAUSES]->(:State)`
- `(:Entity)-[:PART_OF]->(:Entity)`

The ontology acts as the agent’s commonsense memory: Concepts encode affordances, safety rules, and symbolic constraints; Processes encode cause/effect templates (e.g., “grasp then move then release”). This knowledge is continuously refined by Sophia and grounds every plan before it reaches Talos.

### 4.2 Vector Integration
Nodes that participate in semantic search store:
- `embedding_id` (Milvus reference)
- `embedding_model`
- `last_sync`

### 4.3 Validation Framework
- **Level 1 (SHACL)** — Deterministic constraints defined in `ontology/shacl_shapes.ttl` enforce UUID formats, cardinalities, datatypes, and relationship validity. pySHACL is the default runner; Neo4j+n10s SHACL is available as an opt-in heavy test/job.
- **Level 2 (Future)** — Probabilistic/learned validation to detect semantic drift or causal inconsistencies.

---

## 5. Infrastructure and Deployment

### 5.1 Development Environment Requirements
- Docker + Docker Compose
- Neo4j 5.13+ with APOC, GDS, neosemantics plugins
- Milvus 2.3+ (standalone)
- Python 3.10+ (tooling/tests)
- Node.js 18+ (Apollo/site tooling)

### 5.2 HCG Development Cluster
`infra/docker-compose.hcg.dev.yml` provisions:
- **Neo4j** on ports 7474 (HTTP) / 7687 (Bolt)
- **Milvus** on ports 19530 (gRPC) / 9091 (metrics)
- Shared bridge network `logos-hcg-dev-net`
- Persistent volumes for data, logs, plugins

Startup:
```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```
Then load ontology + SHACL via helper scripts in `infra/`.

### 5.3 Production Considerations (Phase 2+)
Future deployment work must address:
- High availability / replication
- Backup & disaster recovery
- Monitoring, tracing, and alerting
- Access control, audit logging, and secret management

---

## 6. API Contracts and Integration

### 6.1 Contract-First Development
- All public APIs reside in `contracts/` (e.g., `hermes.openapi.yaml`).
- Sophia, Talos, and Apollo will publish OpenAPI/JSON Schema contracts before implementation.
- CI validates contracts via swagger-cli.

### 6.2 Versioning Strategy
- Semantic versioning (MAJOR.MINOR.PATCH).
- Breaking changes → new major version; components must support at least N-1.
- Contracts reference the Git tag/release that introduced them.

---

## 7. Phases and Roadmap

| Phase | Goal | Key Deliverables | Status |
|-------|------|------------------|--------|
| **Phase 1** | Formalize HCG + abstract pipeline | Ontology + SHACL, pySHACL + Neo4j validation, Apollo CLI prototype, Talos simulation shim, opt-in heavy tests | ✅ (wrapping `phase 1 closers`) |
| **Phase 2** | Close the loop with richer planning/execution | Planner/executor improvements, Talos capability registry, Hermes integration, Milvus smoke test in CI, Apollo UX variants | 🔜 |
| **Phase 3** | Optional embodiment + learning | Touchscreen/voice Apollo client, optional physical demos, probabilistic validation, cross-repo integration | Future |

### 7.1 Phase 1 — Completed Milestone
- **Infrastructure**: `infra/docker-compose.hcg.dev.yml`, helper scripts, opt-in heavy Dockerfile (`Dockerfile.shacl-validation`).
- **Data/Validation**: `core_ontology.cypher`, `shacl_shapes.ttl`, pySHACL tests (`tests/phase1/test_shacl_pyshacl.py`), optional Neo4j validation job with `RUN_NEO4J_SHACL=1`.
- **Testing**: M1–M4 CI workflows + badges; heavy tests gated via env vars (`RUN_M4_E2E=1` or GitHub workflow inputs).
- **Prototype**: Apollo CLI goal → plan → execute loop with deterministic Talos shim; `scripts/e2e_prototype.sh` for scripted demo.
- **Documentation**: README updates, `PHASE1_VERIFY.md` checklist, `PHASE1_PROTOTYPE_EXPECTATIONS.md`, new flexible spec, and knowledge-base docs.
- **Open polish (`phase 1 closers` #200–#208)**: Neo4j SHACL job docs, planner/executor shims, Milvus smoke, Apollo CLI enhancements, doc cleanup.
- **Success criteria (met)**: HCG stores/retrieves entities, SHACL catches malformed updates, planner/executor run simulated tasks end to end, and all contracts/tests live alongside documentation.

### 7.2 Phase 2 — Updated Intent
Focus on improving reasoning/execution while staying hardware-optional:
- Harden planner/executor APIs so any Talos capability (simulated or physical) can run plans.
- Stand up Talos capability registry + discovery endpoint.
- Integrate Hermes embeddings + Milvus into default CI (smoke tests verifying vector linkage).
- Expand Apollo clients: polish the CLI and ship a browser-based interface that consumes the same APIs, with shared explainability panels.
- Begin logging/tracing + observability for Sophia’s decision loop.
- Demonstrate a Talos-free perception workflow (e.g., browser streaming video to Hermes → Sophia explains state changes in the HCG) as a first-class scenario.
- Prototype the “multimodal LLM + LOGOS” pattern: Apollo hosts an LLM that consults Sophia for grounded context before responding and submits candidate actions back for validation.
- Deliver extensive diagnostics, visualization, and explainability tooling (graph inspectors, plan timelines, causal traces, capability telemetry) available from both CLI and browser experiences.
- **Success criteria (target)**: Sophia plans against live Talos capability lists, executor reports telemetry into the HCG, embeddings/Milvus health checks run in CI, and at least one alternative Apollo surface demonstrates the loop.

### 7.3 Phase 3 — Learning & Optional Embodiment
- Introduce episodic memory in the HCG, plan learning from execution history.
- Layer Level 2 probabilistic validation.
- Demo at least one alternative embodiment (e.g., desk touchscreen, drone) without contract changes.
- Explore multi-agent coordination primitives across Talos capabilities.
- **Success criteria (target)**: Agent improves plan quality using experience, probabilistic validation augments SHACL, and heterogeneous Talos capabilities coordinate without contract changes.

---

## 8. Verification & Demonstration

1. **Automated gates**: `m1-neo4j-crud`, `m2-shacl-validation`, `m3-planning`, `m4-end-to-end` workflows run on push/PR/schedule.
2. **Opt-in jobs**: Heavy tests require env flags (`RUN_NEO4J_SHACL`, `RUN_M4_E2E`) or workflow inputs (`skip_e2e=false`). Default CI stays fast.
3. **Manual demo checklist**: `docs/PHASE1_VERIFY.md` tracks infrastructure bootstrap, validation evidence, Apollo CLI runthrough, and log artifacts.
4. **Stakeholder runbook**:
   - Start infra via compose.
   - Run fast tests: `pytest tests/phase1 -m "not slow"`.
   - Drive Apollo CLI (`send`, `plans`, `execute`, `state`).
   - Optionally enable heavy flows and show GitHub badges/logs.

---

## 9. Documentation & Governance Requirements
- Every doc must refer to “available Talos capabilities” / “configured Apollo client” rather than specific robots or displays.
- README and onboarding material link to this spec and highlight embodiment flexibility.
- Issue templates and automation must avoid hardware assumptions; they should reference APIs, capabilities, and validation gates.
- Gate overrides (if ever required) follow `docs/PHASE1_OVERRIDES.md` and must be logged before Phase 2 work begins.

---

## 10. Next Actions
1. Close remaining `phase 1 closers` issues and update `PHASE1_VERIFY.md` to remove the readiness delta.
2. Run and archive the opt-in Neo4j SHACL + M4 end-to-end tests at least once before tagging `phase1-complete`.
3. Update Phase 2 issue generation scripts to the capability-first language and create the Milvus smoke workflow (#204).
4. Continue refreshing this spec as new phases start; this file is the canonical reference.

---

## 11. Appendices

### Appendix A — Ontology Schema
(Provide the complete Cypher schema: nodes, relationships, constraints, indexes; see `ontology/core_ontology.cypher`).

### Appendix B — Testing Strategy
- Unit tests per component.
- Integration tests via docker-compose.
- Validation suites (pySHACL + Neo4j SHACL).
- Performance tests (load, query latency) for HCG operations.

### Appendix C — Security Considerations
- Authentication/authorization for HCG endpoints.
- Encryption for inter-service communication.
- Input validation and schema enforcement for all APIs.
- Audit logging for every HCG mutation.

### Appendix D — References & Prior Art
- Knowledge graphs & semantic web literature.
- Causal reasoning & inference systems.
- Cognitive architectures (SOAR, ACT-R, etc.).
- Hybrid neural-symbolic research projects.

**Document Status**: Living specification — updated continuously.

**Last Updated**: 2025-11-19
