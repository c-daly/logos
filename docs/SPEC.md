# LOGOS Specification

Single source of truth for the LOGOS cognitive architecture. Supersedes all prior phase-specific specs, architecture overviews, and ADRs.

**Last updated**: 2026-03-02

---

## 1. Vision and Philosophy

Project LOGOS is a research initiative to build a **non-linguistic cognitive architecture** for autonomous agents. The system reasons in graph structures, not natural language. Language is a transport layer handled by external services.

### Core Principles

1. **Non-linguistic cognition first.** Internal reasoning occurs in abstract causal graph structures. Natural language never enters internal processing.
2. **Language as interface.** Natural language is handled by Apollo (presentation) and Hermes (language services), not by Sophia's reasoning substrate.
3. **Causal coherence.** All reasoning maintains explicit causal relationships and temporal ordering.
4. **Validation by constraint.** Deterministic structural validation and future probabilistic validation layers guard every mutation of the Hybrid Cognitive Graph (HCG).
5. **Capability-first deployment.** The same APIs work whether Talos is simulated, connected to a single manipulator, or orchestrating a fleet of drones.
6. **Multi-layer causal world model.** LOGOS fuses commonsense structure (HCG), grounded imagination (JEPA-style predictive architecture), and reflective persona state so the agent reasons over symbolic, embodied, and experiential cause/effect.

### System Goals

1. Deliver a working prototype of the non-linguistic cognitive architecture.
2. Demonstrate superior causal reasoning versus purely linguistic LLM agents.
3. Establish reusable patterns for HCG-centric agent development.
4. Provide an extensible platform for research teams to add capabilities or embodiments without rewriting Sophia or the HCG.
5. Act as a **causal co-processor** for multimodal LLMs -- feeding them grounded context, validating outputs against the HCG, and augmenting their perception with world-model predictions.

---

## 2. Architecture

### 2.1 Components

| Component | Purpose | Required? |
|-----------|---------|-----------|
| **Sophia** | Cognitive core -- planning, execution, world models | Yes |
| **LOGOS (meta-repo)** | Ontology, contracts, infrastructure, SDKs | Yes |
| **Neo4j** | Graph database for the HCG | Yes |
| **Milvus** | Vector database for semantic search | Yes |
| **Hermes** | Language processing, embeddings, LLM gateway | Optional |
| **Apollo** | CLI and web UI | Optional |
| **Talos** | Hardware abstraction, simulators | Optional |

Sophia + LOGOS (Neo4j + Milvus) are the only mandatory components. All other subsystems are optional adapters that speak well-defined contracts.

### 2.2 Data Flow

```
User --> Apollo --> Sophia <--> HCG (Neo4j + Milvus)
          (UI)     (Brain)      (Knowledge)
                      |
                   Hermes (Language/Embeddings/LLM)
                      |
                   Talos (Hardware/Simulation)
```

1. User input arrives via Apollo (CLI, browser, kiosk, voice).
2. Apollo calls Sophia's API (plan, execute, simulate).
3. Sophia reads/writes the HCG (Neo4j + Milvus).
4. Sophia calls Hermes for language, embedding, and LLM tasks.
5. Sophia calls Talos to execute physical actions or simulate them.
6. Results flow back to Apollo for display.

### 2.3 Deployment Modes

| Mode | Description | Required Components |
|------|-------------|---------------------|
| **Graph-only** | CLI/desk widget manipulating the HCG. No hardware. CWM-G operates over stored data or streamed media. | Apollo CLI, Sophia, LOGOS (Neo4j + Milvus) |
| **Perception-only** | Browser/mobile streams video/images/audio. System predicts next frames, labels scenes, explains events into the HCG. No Talos. | Apollo/Hermes client, Sophia, LOGOS |
| **Simulated embodied** | Talos executes deterministic simulators. | Apollo CLI, Sophia, LOGOS, Talos simulators |
| **Physical embodied** | Talos connects to real robots/drones/IoT devices. | Apollo (any UI), Sophia, LOGOS, Talos drivers |
| **Hybrid** | Mix of simulators and hardware, possibly multiple Apollo surfaces. | All of the above as needed |

Documentation and acceptance tests describe configuration via feature flags/env vars, not hard-coded hardware references.

---

## 3. Hybrid Cognitive Graph (HCG)

The HCG is the system's memory and knowledge store, combining a graph database for structural knowledge with a vector database for semantic retrieval.

### 3.1 Graph Database: Neo4j

**Decision rationale (ADR-0001):** Neo4j was chosen over Amazon Neptune, PostgreSQL with recursive CTEs, and ArangoDB for its labeled property graph model, Cypher query language alignment with the HCG ontology, built-in uniqueness constraints, and neosemantics (n10s) plugin for validation integration. Requires version 5.13+ with APOC, GDS, and neosemantics plugins.

### 3.2 Vector Database: Milvus

**Decision rationale (ADR-0002):** Milvus was chosen over Pinecone, Weaviate, FAISS, and Neo4j native vector indexes for its mature ANN performance, multiple index types (FLAT, IVF, HNSW), Docker deployment, and strong Python SDK (pymilvus). Requires version 2.3+.

### 3.3 Bidirectional Sync

Graph nodes that participate in semantic search store:
- `embedding_id` (Milvus reference)
- `embedding_model`
- `last_sync`

Embedding operations are synchronous: create/update/delete of a node triggers an immediate embedding update via Hermes.

### 3.4 Embedding Strategy

**Decision rationale (ADR-0005):** Embeddings are generated statelessly via Hermes's `/embed_text` endpoint. Nodes are serialized to text descriptions (type, name, description, key relationships) before embedding. Default model is `all-MiniLM-L6-v2` (384d), configurable to `all-mpnet-base-v2`, multilingual models, or OpenAI embeddings. This approach keeps embedding generation simple and human-readable at the cost of some graph structure information loss.

---

## 4. Ontology and Data Model

### 4.1 Core Node Types

| Node Type | Purpose | Example |
|-----------|---------|---------|
| **Entity** | Concrete objects or agents | `RobotArm01`, `TaskBoard` |
| **Concept** | Abstract categories | `Manipulator`, `Workspace`, `Container` |
| **State** | Temporal snapshots of entity properties | Position, status at a given time |
| **Process** | Causal transformations between states | `Grasp`, `Move`, `Release` |

### 4.2 Core Relationships

```
(:Entity)-[:IS_A]->(:Concept)
(:Entity)-[:HAS_STATE]->(:State)
(:Entity)-[:LOCATED_AT]->(:Entity)
(:Entity)-[:PART_OF]->(:Entity)
(:Process)-[:CAUSES]->(:State)
(:Process)-[:PRECEDES]->(:Process)
(:Process)-[:USES_TOOL]->(:Entity)
(:Concept)-[:IS_A]->(:Concept)       // concept hierarchy
```

Concepts encode affordances, safety rules, and symbolic constraints. Processes encode cause/effect templates (e.g., "grasp then move then release"). This knowledge is continuously refined by Sophia and grounds every plan before it reaches Talos.

### 4.3 UUID Format

All entity identifiers follow `<type>_<uuid>`:
- `entity_abc123def456`
- `concept_abc123def456`
- `state_abc123def456`
- `process_abc123def456`

### 4.4 Ontology Files

- `ontology/core_ontology.cypher` -- Entity, Concept, State, Process node schemas
- `ontology/test_data_pick_and_place.cypher` -- Reference data for demos

### 4.5 Validation Framework

**Decision rationale (ADR-0003):** Structural validation uses a dual strategy -- pyshacl for fast, connectionless CI validation and Neo4j n10s for production integration. Chosen over JSON Schema (not graph-native), raw Cypher queries (database-dependent), and OWL (computationally expensive).

**Level 1 -- Structural validation (current):** Deterministic constraints enforce UUID formats, cardinalities, datatypes, and relationship validity. Defined in `ontology/shacl_shapes.ttl`. pyshacl runs on every push/PR; n10s validation runs on-demand or weekly.

**Level 2 -- Probabilistic validation (Phase 3+):** Learned validation to detect semantic drift, causal inconsistencies, and uncertainty. Will complement structural constraints with confidence-based reasoning derived from execution history and episodic learning.

**Level 3 -- Neural validation (future):** Neural network-based learned validation for complex pattern detection.

---

## 5. Sophia -- Cognitive Core

### 5.1 Subsystems

1. **Orchestrator** -- Coordinates perception, planning, and execution loops. Keeps CWM layers synchronized.
2. **CWM-A (Abstract)** -- Symbolic world model derived from the HCG. Source of truth for planning.
3. **CWM-G (Grounded)** -- Physics/perception model tied to sensors, actuators, or simulation. Anchors symbols to reality.
4. **CWM-E (Emotional)** -- Reflective model for confidence, trust, persona state. Provides sense of self.
5. **Planner** -- Generates action/process graphs over HCG state using HTN decomposition.
6. **Executor** -- Applies plans and monitors results via Talos.

### 5.2 Causal World Model (CWM)

All three CWM layers emit states wrapped in a **unified CWMState envelope**, ensuring all downstream consumers (Apollo, loggers, debuggers) process them uniformly.

#### CWMState Envelope

```json
{
  "state_id": "cwm_<model>_<uuid>",
  "model_type": "cwm-a | cwm-g | cwm-e",
  "timestamp": "ISO-8601",
  "status": "hypothetical | observed | validated | rejected",
  "confidence": 0.0-1.0,
  "source": "planner | jepa | perception | reflection | orchestrator",
  "links": [
    { "rel": "derived_from", "target_id": "uuid-of-parent-state" },
    { "rel": "predicts", "target_id": "uuid-of-future-state" }
  ],
  "tags": ["capability:perception", "surface:browser"],
  "data": { }
}
```

#### Status Lifecycle

| Status | Meaning |
|--------|---------|
| `hypothetical` | Generated by planner/simulator. Not yet verified. |
| `observed` | Directly perceived from sensors (CWM-G). |
| `validated` | Confirmed by structural validation or consensus. Promoted to CWM-A. |
| `rejected` | Falsified by observation or validation failure. |

Additional memory-tier statuses: `ephemeral`, `short_term`, `canonical`, `proposed`.

#### CWM-A (Abstract)

Symbolic entities, concepts, causal rules. Source of truth for planning. `data` payload contains normalized entity and relationship diffs (`entities`, `relations`, `violations`), plus structural validation status.

Key node types: `Entity`, `Concept`, `State`, `Process`.

#### CWM-G (Grounded)

Sensor data, predicted states, physics properties. Anchors symbols to reality. `data` payload carries JEPA rollout metadata (`imagined`, `horizon_steps`, `frames`, `embeddings`, `assumptions`).

Key node types: `PerceptionFrame`, `ImaginedState`, `ImaginedProcess`.

CWM-G doubles as a short-horizon simulator. Sophia exposes `simulate(capability, context)` that rolls out JEPA-based predictions (or a Talos/Gazebo backend when available). This lets the agent "imagine" outcomes before updating the HCG. Imagined states are recorded with metadata so Apollo/Hermes can explain the reasoning.

#### CWM-E (Emotional)

Diary entries, emotional tags, reflections. Provides sense of self. `data` payload records persona attributes (`sentiment`, `confidence_delta`, `caution_delta`, `narrative`).

Key node types: `PersonaEntry`, `EmotionState`.

PersonaEntry nodes have an optional `trigger` field (e.g., `"error"`, `"user_request"`, `"self_model"`, `"meta"`) for categorizing reflections. EmotionState nodes carry sentiment, confidence, and caution tags linked to processes and entities. Planners read the latest emotion nodes to adjust strategy; interaction surfaces use them to shape persona tone.

#### Ingestion and Promotion Flows

**Perception Loop (CWM-G to CWM-A):**
Raw data from Talos/Hermes is wrapped as CWMState (observed), encoded via JEPA to embeddings, matched against CWM-A Concepts in Milvus. High-confidence matches create/update States in CWM-A (validated).

**Imagination Loop (CWM-A to CWM-G to CWM-A):**
Planner proposes action (hypothetical) -> Sophia calls simulate() -> JEPA returns ImaginedState (hypothetical) -> structural validation checks constraints -> if valid, approve plan for execution.

**Reflection Loop (CWM-A/G to CWM-E):**
Significant events trigger reflection -> create PersonaEntry (CWM-E) linked to event -> update EmotionState (confidence, caution) -> influences future planner heuristics.

#### Storage Rules

- Persist every record as `(:CWMState {state_id, model_type, ...})` with model-specific label (e.g., `:CWM_A_STATE`).
- Attach `(:CWMState)-[:DESCRIBES]->(:Process)` / `(:Entity)` edges using IDs in `links`.
- Mirror the envelope in Milvus documents so embeddings/similarities can be queried uniformly.

#### API/Logging Rules

- `/state` returns `{"states": [<CWMState>], "cursor": ...}`.
- `/plan` and `/simulate` responses append newly created CWMState records.
- Structured logging + OpenTelemetry spans include `state_id`, `model_type`, and `status`.

### 5.3 Planning

**Decision rationale (ADR-0004):** HTN (Hierarchical Task Network) planning was chosen over STRIPS/PDDL, Monte Carlo Tree Search, and LLM-prompted planning. HTN provides hierarchical decomposition that matches human reasoning, encodes domain knowledge from the HCG, produces explainable plans, and supports incremental refinement. Established algorithms include SHOP2 and PANDA.

**Architecture:**
```
HCG (Neo4j) -> Method Library (Cypher + Python) -> HTN Planner (recursive decomposition)
  -> Abstract Plan -> Executor (grounds to Talos capabilities)
```

Plans are validated against both CWM-A (semantic correctness) and CWM-G (physical plausibility). The planner reads CWM-E emotion nodes to adjust strategy (e.g., avoid risky capabilities when caution is high).

**Future extensions:** Hybrid HTN + LLM planning, learning from experience (episodic memory integration), probabilistic HTN, reactive replanning.

### 5.4 Imagination and Simulation

`/simulate` accepts `{ capability_id, context }` payloads. Context carries entity references, pointers to sensor frames, and optional Talos metadata. CWM-G (JEPA runner) performs k-step rollout and returns predicted states plus confidence. Results are stored as `(:ImaginedProcess)` / `(:ImaginedState)` nodes with `imagined:true`, linked to the triggering plan.

Both a CPU-friendly runner (for Talos-free deployments) and hooks to swap in Talos/Gazebo simulators are provided.

---

## 6. Hermes -- Language and Embedding Utility

Hermes is a stateless language service. It never writes to the HCG directly and can be swapped for alternative providers as long as contracts hold.

### 6.1 Endpoints

| Endpoint | Function | Input | Output |
|----------|----------|-------|--------|
| `/stt` | Speech-to-text | Audio | Transcript |
| `/tts` | Text-to-speech | Text | Audio |
| `/simple_nlp` | NLP preprocessing | Text | Tokens/POS/NER |
| `/embed_text` | Text embedding | Text | Vector + `embedding_id` |
| `/llm` | LLM chat completion proxy | Prompt | Completion |
| `/health` | Service health | -- | Milvus connectivity + model status |

### 6.2 LLM Gateway

**Decision rationale (ADR-0006, proposed):** Hermes exposes `/llm` with pluggable providers (OpenAI, Anthropic, local models) rather than Apollo calling LLMs directly. This preserves centralized telemetry, simplifies provider switching, and keeps Apollo thin. Hermes manages API keys, rate limits, and cost tracking.

### 6.3 Model Configuration

| Capability | Default Model | Config Var |
|------------|---------------|------------|
| Embeddings | `all-MiniLM-L6-v2` | `HERMES_EMBED_MODEL` |
| NLP | spaCy pipeline | `HERMES_NLP_MODEL` |
| STT | Whisper (small) | `HERMES_STT_MODEL` |
| TTS | Torchaudio/Coqui | env vars |
| LLM | Pluggable | env vars |

All models are configurable via environment variables. Remote API proxying is supported via API key env vars.

### 6.4 Graph Assist (Tentative -- Hermes/Sophia Integration)

A proposed `/graph-assist` endpoint where Sophia requests semantic assistance from Hermes for:
- **Entity resolution**: Disambiguating entities from context.
- **Knowledge extraction**: Parsing media metadata into graph nodes/edges.
- **Relationship inference**: Suggesting connections between unlinked entities.
- **Query assistance**: Natural language to Cypher translation.
- **Ontology extension**: Proposing new node types.

Preferred approach: Hermes returns validated Cypher queries that Sophia executes against Neo4j, with confidence scores and reasoning. Security mitigations include query sandboxing, read-only mode, audit logging, and schema pinning.

---

## 7. Talos -- Capability Bus

Talos exposes a capability graph describing available actions (simulate pick/place, move drone waypoint, send notification, etc.). Implementations may be pure simulation, physical drivers, or hybrids. Deployments that do not require actuation may omit Talos entirely.

Every Talos capability invocation first runs through CWM-G to predict physics outcomes, then reconciles with the HCG for commonsense consistency.

---

## 8. Apollo -- Presentation Layer

Apollo represents any interaction surface calling Sophia's Goal/Plan/State APIs. Multiple Apollo clients can coexist.

### 8.1 Surfaces

- **CLI**: Goal/plan/execute/state commands. Refactored in Phase 2 to consume shared SDK.
- **Browser app**: Vite + React + TypeScript. Chat panel (LLM-backed, persona-aware), graph viewer, diagnostics tabs, plan timelines.
- **Future**: Kiosk, voice UIs, touchscreen.

### 8.2 LLM Co-processor Pattern

Apollo can embed a multimodal LLM that calls Sophia as a causal co-processor. LLM outputs are validated against the HCG, and Sophia feeds back grounded context, predicted frames, or structured explanations.

### 8.3 Diagnostics and Explainability

Every Apollo surface must expose diagnostics, visualizations, and explainability views: graph inspectors, plan timelines, causal traces, capability telemetry.

---

## 9. Memory Architecture

### 9.1 Hierarchical Memory (Phase 3)

Sophia maintains knowledge across three tiers with distinct lifetimes and promotion policies. Information flows upward only when it demonstrates both **significance** (worth remembering) and **truth** (verified or high-confidence).

| Tier | Scope | Lifetime | Storage | CWMState status |
|------|-------|----------|---------|-----------------|
| **Ephemeral** | Single session | Session end | In-memory | `ephemeral` |
| **Short-term** | Multi-session | Configurable TTL (default 7 days) | Redis with TTL | `short_term` |
| **Long-term** | Permanent | Indefinite | Neo4j + Milvus | `canonical` / `proposed` |

### 9.2 Promotion Criteria

#### Ephemeral to Short-term

Triggers at session boundary or significant event:

| Criterion | Description |
|-----------|-------------|
| **User signal** | User explicitly marked something important |
| **Behavioral impact** | Changed how agent should act |
| **Recurrence** | Same pattern observed multiple times in session |
| **Novel fact** | New information not in HCG |
| **Unresolved question** | Open curiosity that warrants follow-up |

Automatic exclusions: individual chat messages, pending clarifications, intermediate reasoning steps, temporary UI state.

#### Short-term to Long-term

Triggers on reflection, validation pass, or explicit approval:

| Criterion | Description |
|-----------|-------------|
| **Confidence threshold** | Belief confidence > 0.8 after multiple observations |
| **Cross-session consistency** | Same pattern observed across multiple sessions |
| **Causal verification** | Hypothesis validated by outcome |
| **Source reliability** | Trusted source (user statement, verified system) |
| **Human approval** | Critical facts reviewed by operator |

Automatic exclusions: unverified hypotheses (confidence < 0.5), expired context, contradicted beliefs, trivia.

### 9.3 Demotion and Decay

- **Long-term to Short-term**: Deprecated facts, superseded knowledge, detected inconsistencies.
- **Short-term to Ephemeral**: Failed validation, user contradiction, low confidence after timeout.
- **Any tier to Garbage**: TTL expiration, explicit deletion, confidence < 0.1.

Key principle: facts don't earn permanence just by existing. They must demonstrate relevance through use, corroboration, or explicit validation.

### 9.4 Memory API (Phase 3)

- `POST /api/memory/{tier}` -- Create entry at specified tier
- `GET /api/memory/{tier}` -- Query entries (by type, time window, session, confidence)
- `DELETE /api/memory/{tier}/{id}` -- Explicit deletion
- `POST /api/memory/promote/{id}` -- Promote to next tier
- `POST /api/memory/demote/{id}` -- Demote with reason

---

## 10. Reflection and Persona

### 10.1 Event-driven Reflection (Phase 3)

Reflections are triggered by significant events, not periodic timers:

| Trigger | Description |
|---------|-------------|
| `error` | Plan execution failures, validation errors, capability failures |
| `user_request` | Explicit instructions to change behavior, tone, or approach |
| `correction` | User corrects agent's understanding or actions |
| `session_boundary` | Conversation start (load context) / end (consolidate learnings) |
| `milestone` | Goal completion, significant progress, new capability |

Reflection output includes emotional assessment (confidence, caution, sentiment) stored as EmotionState nodes.

### 10.2 Selective Diary Entries (Phase 3)

Replaces automatic per-turn observations with selective entries based on:
- **Impact**: Does this change how the agent should behave?
- **Reusability**: Will this context matter in future sessions?
- **Learning value**: Is there a lesson or pattern to extract?
- **User signal**: Did user explicitly indicate importance?

Target: reduce diary entry volume by >70% compared to naive per-turn logging while preserving all critical information.

### 10.3 Persona Storage

PersonaEntry nodes stored in the HCG with timestamp, summary, sentiment, trigger, and related process references. Apollo/Hermes query them to drive persona tone.

---

## 11. Episodic Learning (Phase 3)

### 11.1 Episode Structure

```
Episode {
  id, timestamp, goal, plan_id,
  actions: [{ capability, params, result, confidence }],
  outcome: { success, failure_reason, duration },
  context: { user, environment, constraints },
  reflections: [related PersonaEntry IDs],
  learned: { patterns, adjustments, recommendations }
}
```

### 11.2 Learning Flow

1. Plan execution completes (success or failure).
2. Create Episode record with full trace.
3. Link to related PersonaEntry reflections.
4. Index by goal type, capabilities, context.
5. Future plans query similar episodes.
6. Adjust confidence, strategy, capability selection.

### 11.3 Capability Confidence

Track per-capability success rates. Planner adjusts selection based on historical outcomes. Context-sensitive -- different strategies for different domains/users.

---

## 12. Graph Maintenance

### 12.1 Operations

| Operation | Description | Trigger |
|-----------|-------------|---------|
| **Pruning** | Remove low-confidence or stale edges | Scheduled / budget-driven |
| **Deduplication** | Merge nodes representing the same entity | On ingest / periodic scan |
| **Inference** | Create implicit relationships from patterns | Reflection / curiosity |
| **Consolidation** | Summarize dense subgraphs into higher-level nodes | Threshold-based |
| **Orphan cleanup** | Remove disconnected nodes with no value | Scheduled |
| **Confidence decay** | Reduce certainty of unverified old facts | Time-based |

### 12.2 Deduplication

Approach: embedding similarity + label fuzzy matching for candidate detection, Hermes verification, merge proposal via Cypher, conflict resolution (prefer newer data, higher confidence, or prompt user).

### 12.3 Pruning Safeguards

- Never prune user-created content without confirmation.
- Archive before delete (soft delete with recovery window).
- Pruning proposals reviewed if above threshold count.

---

## 13. Curiosity Budget (Phase 4+)

Sophia maintains a constrained resource allocation for self-directed exploration when not responding to user requests.

### 13.1 Triggers

| Trigger | Description |
|---------|-------------|
| Novel fact | Information that doesn't fit existing patterns |
| Apparent contradiction | Two beliefs that seem incompatible |
| Perplexing diary entry | Reflection with high uncertainty |
| Interesting pattern | Recurring structure suggesting underlying connection |
| Disconnected subgraphs | Nodes that seem related but lack explicit links |

### 13.2 Budget Mechanics

Budget is a scalar (0.0-1.0) with minimum threshold, recharge rate, and per-action spend cap. Increases when explorations are useful; decreases when they yield nothing. Resource limits: configurable API calls per hour (default 10), exploration time per session (default 5 min), single concurrent exploration, proposals only (no auto-commit).

### 13.3 Feedback Loop

Experience -> Reflection -> Curiosity -> Exploration -> New Knowledge -> Better Plans.

---

## 14. API Contracts and Integration

### 14.1 Contract-First Development

All public APIs reside in `contracts/` (e.g., `hermes.openapi.yaml`, `sophia.openapi.yaml`). Implementation follows contracts, not the reverse. CI validates contracts via swagger-cli.

### 14.2 Key APIs

#### Sophia (port 47000)

| Endpoint | Purpose |
|----------|---------|
| `POST /plan` | Generate a plan for a goal |
| `POST /execute` | Execute a plan step |
| `POST /simulate` | Predict outcomes without acting |
| `POST /ingest` | Add media/knowledge to the HCG |
| `GET /state` | Current cognitive state (CWMState envelope) |
| `GET /history` | Execution history with optional CWM-E entries |
| `GET /health` | Service health |

#### Hermes (port 17000)

| Endpoint | Purpose |
|----------|---------|
| `POST /stt` | Speech to text |
| `POST /tts` | Text to speech |
| `POST /embed_text` | Generate text embeddings |
| `POST /simple_nlp` | NLP preprocessing |
| `POST /llm` | LLM chat completion proxy |
| `GET /health` | Service health |

### 14.3 Port Allocation

| Repo | API Port |
|------|----------|
| Hermes | 17000 |
| Apollo | 27000 |
| LOGOS | 37000 |
| Sophia | 47000 |
| Talos | 57000 |

Infrastructure (Neo4j, Milvus) runs on default ports (7474/7687, 19530) shared across all repos.

### 14.4 Versioning

Semantic versioning (MAJOR.MINOR.PATCH). Breaking changes require a new major version. Components must support at least N-1. Contracts reference the Git tag/release that introduced them.

---

## 15. Infrastructure

### 15.1 Development Stack

- Docker + Docker Compose
- Neo4j 5.13+ with APOC, GDS, neosemantics plugins
- Milvus 2.3+ (standalone)
- Python 3.11+ (services/tooling)
- Node.js 18+ (Apollo/site tooling)

### 15.2 HCG Development Cluster

`infra/docker-compose.hcg.dev.yml` provisions:
- **Neo4j** on ports 7474 (HTTP) / 7687 (Bolt)
- **Milvus** on ports 19530 (gRPC) / 9091 (metrics)
- Shared bridge network `logos-hcg-dev-net`
- Persistent volumes for data, logs, plugins

```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```

### 15.3 Service Stacks

- **Sophia**: Python 3.11, FastAPI, Neo4j driver, structural validation helpers.
- **Hermes**: Python 3.11, FastAPI, SentenceTransformers, spaCy, Whisper, pymilvus.
- **Apollo browser**: Vite + React + TypeScript, Tailwind.

### 15.4 Production Considerations

- High availability / replication
- Backup and disaster recovery
- Monitoring, tracing, and alerting (OpenTelemetry)
- Access control, audit logging, secret management
- Token-based authentication with read/write scope middleware

---

## 16. Phase Roadmap and Status

| Phase | Goal | Status |
|-------|------|--------|
| **Phase 1** | Formalize HCG and abstract pipeline | COMPLETE |
| **Phase 2** | Perception, services, Apollo UX | In progress |
| **Phase 3** | Learning and memory systems | Planned |
| **Phase 4** | Operational autonomy and advanced reflection | Future |
| **Phase 5** | Networked agents / swarm | Future |

### 16.1 Phase 1 -- HCG Foundation (COMPLETE)

Verified 2025-11-19. Established the core infrastructure:

**Milestones (all verified):**
- **P1-M1: Neo4j CRUD and Entity Management.** CRUD operations for Entity, Concept, State, Process nodes. UUID constraints, indexes, relationship management. 47 tests passing.
- **P1-M2: Structural Validation.** Type-ancestry validation shapes loaded into Neo4j, validation catches invalid data with actionable error messages. Dual validation (pyshacl CI + n10s production).
- **P1-M3: Planning and Causal Reasoning.** Multi-step planning with causal (CAUSES) and temporal (PRECEDES) relationships. Precondition checking, state transitions, process hierarchy.
- **P1-M4: End-to-End Pick and Place.** Full Apollo -> Sophia -> Talos -> HCG pipeline executing a pick-and-place task. 22 integration tests passing.

**Key artifacts:** `infra/docker-compose.hcg.dev.yml`, `ontology/core_ontology.cypher`, `ontology/shacl_shapes.ttl`, `scripts/e2e_prototype.sh`, CI workflows with opt-in heavy tests (`RUN_NEO4J_SHACL=1`, `RUN_M4_E2E=1`).

### 16.2 Phase 2 -- Perception and Apollo UX (In Progress)

Extends Phase 1 into a Talos-optional, perception-driven assistant with dual interfaces and LLM co-processor.

**Milestones:**
- **P2-M1: Services Online.** Sophia/Hermes FastAPI services with `/plan`, `/state`, `/simulate`, `/embed_text`, `/simple_nlp`, `/stt`, `/tts`. Docker Compose alongside Neo4j/Milvus.
- **P2-M2: Apollo Dual Surface.** CLI refactored to shared SDK. Browser app MVP with chat, plan viewer, graph explorer, diagnostics.
- **P2-M3: Perception and Imagination.** CWM-G handles Talos-free media streams. `/simulate` returns imagined states recorded in Neo4j. Milvus smoke tests in CI.
- **P2-M4: Diagnostics and Persona.** CWM-E reflection infrastructure. EmotionState nodes produced. Observability stack, log export, demo capture.

Phase 2 also establishes: unified CWMState contract across all APIs, basic PersonaEntry and EmotionState data models, rule-based emotion classifier (evolving toward learned models), and the multimodal LLM + LOGOS co-processor pattern.

### 16.3 Phase 3 -- Learning and Memory Systems (Planned)

Transforms LOGOS from a reactive system into one that learns from experience and develops a persistent personality.

**Milestones:**
- **P3-M1: Hierarchical Memory Infrastructure.** Three-tier memory (ephemeral/short-term/long-term) with Redis, promotion/demotion policies, session management.
- **P3-M2: Event-driven Reflection.** Intelligent reflection triggers, LLM-powered introspection, EmotionState generation from significant events.
- **P3-M3: Selective Diary Entries.** Impact-based diary creation, >70% volume reduction, short-term memory as working context.
- **P3-M4: Episodic Memory and Learning.** Episode storage and indexing, plan quality improvement from history, probabilistic validation (Level 2), capability confidence tracking.

Estimated timeline: 8-12 weeks after Phase 2 completion.

### 16.4 Phase 4 -- Operational Autonomy (Future)

- Meta-reflection: aggregate analysis across diary entries for systemic pattern detection.
- Personality evolution tracking.
- Curiosity-driven exploration with resource budgets.
- Continuous learning with safety gates, rollback, A/B testing, human-in-the-loop validation.
- Deep planner integration with reflection-driven strategy adjustment.

### 16.5 Phase 5 -- Networked Agents / Swarm (Future)

- Coordinate multiple LOGOS instances.
- Share HCG slices between agents.
- Orchestrate Talos fleets or swarm-style deployments.
- Selective knowledge transfer between instances.

---

## 17. Verification and Testing

### 17.1 Automated Gates

CI workflows validate milestones on push/PR/schedule:
- `m1-neo4j-crud`, `m2-shacl-validation`, `m3-planning`, `m4-end-to-end` (Phase 1)
- `phase2-sophia-service`, `phase2-hermes-service`, `phase2-apollo-web`, `phase2-perception` (Phase 2)

### 17.2 Opt-in Heavy Tests

Tests requiring infrastructure are gated via env flags (`RUN_NEO4J_SHACL`, `RUN_M4_E2E`) or workflow inputs. Default CI stays fast.

### 17.3 Test Strategy

- Unit tests per component.
- Integration tests via docker-compose.
- Structural validation suites (pyshacl + n10s).
- Performance tests (load, query latency) for HCG operations.
- Evidence stored in `logs/p{N}-m{N}-verification/` directories.

### 17.4 Stakeholder Demo

1. Start infra via compose.
2. Run fast tests: `pytest tests/integration -m "not slow"`.
3. Drive Apollo CLI (`send`, `plans`, `execute`, `state`).
4. Optionally enable heavy flows and review CI badges/logs.

---

## 18. Security

- Authentication/authorization for all service endpoints (token-based with read/write scopes).
- Encryption for inter-service communication.
- Input validation and schema enforcement for all APIs.
- Audit logging for every HCG mutation.
- No secrets in logs or PII exposure. Sanitize inputs.
- Query sandboxing for Hermes-generated Cypher (Graph Assist).

---

## 19. Governance

- Every document refers to "available Talos capabilities" / "configured Apollo client" rather than specific hardware.
- Issue templates avoid hardware assumptions; reference APIs, capabilities, and validation gates.
- This file is the canonical specification. Phase-specific detail lives under `docs/phase{N}/`. Archival material under `docs/old/`.
