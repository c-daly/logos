# Project LOGOS - Functional Epoch Organization

This document describes the functionality-based organization of Phase 1 tasks for Project LOGOS.

## Overview

Phase 1 is organized into four functional epochs (milestones), each focused on building a specific capability layer. Each epoch delivers a coherent set of functionalities that enable the next layer of capabilities.

## Functional Epoch Structure

### Epoch 1: Infrastructure & Knowledge Foundation

**Milestone:** M1 - HCG can store and retrieve entities

**Core Functionality:** Build the foundation for knowledge representation and storage

**Key Capabilities Delivered:**
- **Repository Infrastructure:** All component repositories initialized and configured
- **Knowledge Graph Storage:** Neo4j + Milvus operational with core ontology
- **Data Persistence:** CRUD operations for entities, concepts, states, and processes
- **Development Environment:** Docker-compose setup, dependency management, testing frameworks
- **Project Management:** Issue tracking, project board, labels, and workflows

**Functional Components:**
- Neo4j graph database for symbolic knowledge representation
- Milvus vector database for semantic embeddings
- Core HCG ontology (Entity, Concept, State, Process node types)
- Basic graph query utilities
- Repository scaffolding for Sophia, Hermes, Talos, Apollo

**Exit Criteria:**
- ✅ Can create and retrieve entities in the knowledge graph
- ✅ Neo4j and Milvus are communicating correctly
- ✅ Core ontology constraints are enforced
- ✅ All development environments are operational

**Task Categories:**
- Repository initialization (all components)
- Database infrastructure setup
- Core ontology creation
- Basic query utilities (A4)
- Project tracking infrastructure

**Task Count:** ~40 tasks

**Key Deliverables:** Knowledge storage layer operational

---

### Epoch 2: Language & Perception Services

**Milestone:** M2 - SHACL validation catches errors

**Core Functionality:** Add language processing, validation, and semantic capabilities

**Key Capabilities Delivered:**
- **Language Processing:** Speech-to-text, text-to-speech, NLP utilities
- **Semantic Embeddings:** Text embedding generation and storage
- **Knowledge Validation:** SHACL-based constraint validation for knowledge graph
- **Vector Integration:** Synchronized semantic embeddings with knowledge graph
- **API Services:** Stateless Hermes API for language and embedding utilities

**Functional Components:**
- Hermes STT endpoint (speech → text)
- Hermes TTS endpoint (text → speech)
- Hermes NLP endpoint (tokenization, POS, NER)
- Hermes embedding endpoint (text → vectors)
- SHACL validation layer (A2)
- Neo4j ↔ Milvus vector sync (A3)
- Extended ontology for pick-and-place domain (A1)

**Exit Criteria:**
- ✅ Invalid knowledge updates are rejected by SHACL validation
- ✅ Valid knowledge updates are accepted
- ✅ Text can be converted to embeddings and stored in Milvus
- ✅ Hermes API endpoints are functional
- ✅ Ontology supports pick-and-place scenario

**Task Categories:**
- SHACL validation implementation (A2)
- Vector database integration (A3)
- Ontology extension (A1)
- Hermes endpoint implementation (C1)
- Hermes deployment (C2)

**Task Count:** ~8 tasks

**Key Deliverables:** Language I/O and knowledge validation layers operational

---

### Epoch 3: Cognitive Core & Reasoning

**Milestone:** M3 - Sophia can plan simple actions

**Core Functionality:** Build the cognitive architecture for reasoning and planning

**Key Capabilities Delivered:**
- **World Modeling:** Abstract representation of environment state (CWM-A)
- **Causal Reasoning:** Graph-based planning using causal relationships
- **Control Flow:** Orchestrator managing cognitive subsystems
- **Action Planning:** Generate action sequences to achieve goals
- **Simulated Perception:** Talos simulated sensors and actuators
- **Human Interaction:** Apollo command interface

**Functional Components:**
- Orchestrator (subsystem coordination) - B1
- CWM-A (Abstract World Model) - B2
- Planner (causal graph traversal) - B3
- Executor stub - B4
- Talos simulated interfaces - C3
- Apollo CLI - C4
- Research on causal reasoning, GNNs, multi-modal grounding
- Architecture documentation (ADRs)

**Exit Criteria:**
- ✅ Given a goal, Sophia generates a valid plan
- ✅ Plans contain necessary causal steps
- ✅ Plans validate against ontology constraints
- ✅ Simulated environment provides sensor data
- ✅ Commands can be issued via Apollo interface

**Task Categories:**
- Orchestrator implementation (B1)
- World model implementation (B2)
- Planning algorithm implementation (B3)
- Executor stub (B4)
- Simulated hardware (C3)
- User interface (C4)
- Research sprints (R1, R2, R3)
- Documentation (D1, D2, D3)

**Task Count:** ~18 tasks

**Key Deliverables:** Autonomous reasoning and planning capabilities operational

---

### Epoch 4: Integration & Demonstration

**Milestone:** M4 - End-to-end "pick and place"

**Core Functionality:** Integrate all systems and demonstrate autonomous capabilities

**Key Capabilities Delivered:**
- **End-to-End Pipeline:** User command → planning → execution → feedback
- **Autonomous Execution:** Complete pick-and-place task autonomously
- **State Management:** HCG updates during execution
- **Graceful Failure:** Error detection and recovery
- **Public Demonstration:** Video, documentation, open-source release
- **Community Engagement:** Blog posts, research outreach

**Functional Components:**
- Full integration: Orchestrator → CWM-A → Planner → Executor (B5)
- Command: "Pick up cup" works end-to-end
- HCG state updates verified
- SHACL validation during execution
- Demo video production
- Blog post on non-linguistic cognition
- Open-source preparation
- Research community engagement

**Exit Criteria:**
- ✅ "Pick up cup" command executes successfully
- ✅ System demonstrates causal reasoning (not LLM-based)
- ✅ HCG accurately reflects world state changes
- ✅ Validation prevents invalid state transitions
- ✅ Demo video published
- ✅ Codebase ready for public release

**Task Categories:**
- End-to-end integration (B5)
- System testing and validation (M4)
- Demo creation (O2)
- Documentation (D4)
- Open-source preparation (O3)
- Outreach (O1, O4)

**Task Count:** ~7 tasks

**Key Deliverables:** Fully integrated autonomous agent demonstrating non-linguistic cognition

---

## Functional Capability Stack

```
┌─────────────────────────────────────────────────────┐
│  Epoch 4: Integration & Demonstration               │
│  • End-to-end autonomous behavior                   │
│  • User interaction → execution → feedback          │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│  Epoch 3: Cognitive Core & Reasoning                │
│  • Planning & reasoning                             │
│  • World modeling & state management                │
│  • Orchestration & control flow                     │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│  Epoch 2: Language & Perception Services            │
│  • Language I/O (STT, TTS, NLP)                     │
│  • Semantic embeddings                              │
│  • Knowledge validation (SHACL)                     │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│  Epoch 1: Infrastructure & Knowledge Foundation     │
│  • Knowledge graph storage (Neo4j + Milvus)         │
│  • Core ontology & data structures                  │
│  • Development infrastructure                       │
└─────────────────────────────────────────────────────┘
```

---

## Workstream to Functional Epoch Mapping

### Workstream A: HCG Foundation and Validation
**Functional Distribution:**
- **Epoch 1:** A4 (Query utilities - infrastructure)
- **Epoch 2:** A1 (Ontology extension), A2 (SHACL validation), A3 (Vector integration)

**Rationale:** A4 provides basic infrastructure for querying. A1/A2/A3 add validation and semantic capabilities.

### Workstream B: Sophia Cognitive Core Prototype
**Functional Distribution:**
- **Epoch 3:** B1 (Orchestrator), B2 (CWM-A), B3 (Planner), B4 (Executor stub)
- **Epoch 4:** B5 (End-to-end integration)

**Rationale:** B1-B4 build cognitive capabilities. B5 integrates everything for demonstration.

### Workstream C: Hermes and Support Services
**Functional Distribution:**
- **Epoch 2:** C1 (Hermes endpoints), C2 (Hermes deployment) - Language services
- **Epoch 3:** C3 (Talos simulation), C4 (Apollo CLI) - Needed for cognitive testing

**Rationale:** Language I/O comes before cognition. Interaction interfaces support cognitive testing.

---

## Functional Dependencies

```
Epoch 1 (Knowledge Foundation)
    │
    ├──→ Epoch 2 (Language & Validation)
    │        │
    │        └──→ Epoch 3 (Cognitive Core)
    │                  │
    └──────────────────┴──→ Epoch 4 (Integration)
```

**Critical Path:**
1. Knowledge storage must exist before validation
2. Validation must work before cognitive operations
3. Language services support cognitive interaction
4. All capabilities required for integration

---

## Milestone Timeline (Functional Progression)

```
Epoch 1  ┃ Infrastructure & Knowledge Foundation
         ┃ • Knowledge graph operational
         ┃ • Development infrastructure ready
         ┃ └─ M1: HCG Store & Retrieve ✓
         ┃
Epoch 2  ┃ Language & Perception Services
         ┃ • Language I/O functional
         ┃ • Validation layer operational
         ┃ • Semantic embeddings working
         ┃ └─ M2: SHACL Validation ✓
         ┃
Epoch 3  ┃ Cognitive Core & Reasoning
         ┃ • Planning operational
         ┃ • World modeling functional
         ┃ • Reasoning capabilities demonstrated
         ┃ └─ M3: Simple Planning ✓
         ┃
Epoch 4  ┃ Integration & Demonstration
         ┃ • All systems integrated
         ┃ • Autonomous behavior demonstrated
         ┃ • Public release ready
         ┃ └─ M4: Pick and Place ✓
```

---

## Issue Labeling Convention

Issues are labeled according to their functional epoch and component:

- **Milestone Labels:** M1, M2, M3, M4 (corresponding to epochs)
- **Component Labels:** `component:sophia`, `component:hermes`, `component:talos`, `component:apollo`, `component:infrastructure`
- **Workstream Labels:** `workstream:A` (HCG), `workstream:B` (Sophia), `workstream:C` (Services)
- **Phase Label:** All Phase 1 tasks have `phase:1`
- **Priority Labels:** `priority:high`, `priority:medium`, `priority:low`
- **Type Labels:** `type:feature`, `type:testing`, `type:documentation`, `type:research`, `type:outreach`

**Functional Categorization:**
- Epoch 1 issues: Infrastructure, data storage, ontology foundation
- Epoch 2 issues: Language services, validation, semantic capabilities
- Epoch 3 issues: Cognitive architecture, reasoning, planning
- Epoch 4 issues: Integration, demonstration, outreach

---

## Creating Issues by Functional Epoch

Use the provided script to generate issues organized by functional capability:

```bash
# Generate GitHub CLI commands
python3 .github/scripts/create_issues_by_epoch.py --format gh-cli --output create_issues.sh

# Review the commands (optional)
less create_issues.sh

# Execute to create all issues
chmod +x create_issues.sh
./create_issues.sh
```

**Note:** Before running the script, ensure that milestones M1, M2, M3, and M4 have been created in the GitHub repository.

### Creating Milestones

Create the four functional milestones using GitHub CLI:

```bash
# M1: HCG Store & Retrieve (Infrastructure & Knowledge Foundation)
gh milestone create "M1: HCG Store & Retrieve" \
  --repo c-daly/logos \
  --description "Knowledge graph operational. Neo4j + Milvus working, core ontology loaded, basic CRUD operations functional."

# M2: SHACL Validation (Language & Perception Services)
gh milestone create "M2: SHACL Validation" \
  --repo c-daly/logos \
  --description "Validation and language services operational. SHACL validation working, Hermes endpoints functional, embeddings integrated."

# M3: Simple Planning (Cognitive Core & Reasoning)
gh milestone create "M3: Simple Planning" \
  --repo c-daly/logos \
  --description "Cognitive capabilities demonstrated. Sophia can generate valid plans using causal reasoning over the knowledge graph."

# M4: Pick and Place (Integration & Demonstration)
gh milestone create "M4: Pick and Place" \
  --repo c-daly/logos \
  --description "End-to-end autonomous behavior. Full pipeline working from user command to execution with knowledge graph updates."
```

---

## Progress Tracking

Progress will be tracked at multiple levels:

1. **Functional Capability Reviews:** At the completion of each epoch milestone
2. **Weekly Progress Reports:** Automated GitHub Action runs every Monday
3. **Component Integration Tests:** As each functional layer is completed
4. **Cross-Epoch Dependencies:** Tracking when capabilities from one epoch enable the next

**Functional Progression Tracking:**
- Track capability delivery (storage → validation → reasoning → integration)
- Monitor inter-epoch dependencies
- Identify blockers in the capability stack
- Celebrate functional milestones

---

## Risk Management by Functional Epoch

### Epoch 1 Risks (Infrastructure)
- **Risk:** Neo4j + Milvus integration complexity
- **Mitigation:** Start with simple sync, iterate incrementally
- **Impact:** Delays M1, blocks all downstream work

### Epoch 2 Risks (Language & Validation)
- **Risk:** SHACL validation complexity or Hermes model availability
- **Mitigation:** Use proven libraries, implement stubs if needed
- **Impact:** Delays M2, blocks cognitive development

### Epoch 3 Risks (Cognitive Core)
- **Risk:** Planning algorithm more complex than expected
- **Mitigation:** Start simple (graph traversal), defer optimization
- **Impact:** Delays M3, affects integration timeline

### Epoch 4 Risks (Integration)
- **Risk:** Component integration issues
- **Mitigation:** Early integration testing, clear API contracts
- **Impact:** Delays M4 and Phase 1 completion

**Mitigation Strategy:** Each epoch delivers standalone functional value, enabling partial rollback if needed.

---

## Functional Benefits of This Organization

### Clear Capability Layers
Each epoch delivers a complete functional layer that can be tested independently:
- Epoch 1: Can we store knowledge?
- Epoch 2: Can we validate and understand language?
- Epoch 3: Can we reason and plan?
- Epoch 4: Can we act autonomously?

### Parallel Work Opportunities
- Within Epoch 2: Language services (C1, C2) and validation (A2) can proceed in parallel
- Within Epoch 3: Cognitive components (B1-B4) and interfaces (C3, C4) are somewhat independent
- Research (R1-R3) can run in parallel with implementation

### Incremental Value Delivery
Each milestone represents working functionality:
- M1: Functional knowledge base
- M2: Validated, language-aware knowledge base
- M3: Reasoning-capable system
- M4: Fully autonomous agent

### Testability
Each functional layer has clear acceptance criteria independent of other layers.

---

## References

- **Action Items Document:** `docs/action_items.md`
- **Full Specification:** `docs/spec/project_logos_full.md` (Section 7.1 - Phase 1 Plan)
- **Project Board Setup:** `.github/PROJECT_BOARD_SETUP.md`
- **Issue Generation Script:** `.github/scripts/create_issues_by_epoch.py`

---

**Last Updated:** 2025-11-16
**Status:** Active - Phase 1 Functional Epoch Organization
**Organization Type:** Functionality-Based (Infrastructure → Language → Cognition → Integration)
