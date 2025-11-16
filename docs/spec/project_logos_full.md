# Project LOGOS — Full Specification

## 1. Introduction and Vision

Project LOGOS is a foundational research initiative to build a non-linguistic cognitive architecture for autonomous agents. The system is designed around the Hybrid Causal Graph (HCG), a graph-based knowledge representation that integrates symbolic reasoning with vector-based semantic search.

### 1.1 Core Philosophy

- **Non-linguistic cognition first**: Internal reasoning occurs in abstract causal graph structures, not natural language
- **Language as interface**: Natural language is treated as an I/O modality, not the substrate of thought
- **Causal coherence**: All reasoning maintains explicit causal relationships and temporal ordering
- **Validation by constraint**: Multi-level validation ensures logical consistency and constraint satisfaction

### 1.2 System Goals

1. Develop a working prototype of non-linguistic cognitive architecture
2. Demonstrate superior causal reasoning compared to purely linguistic LLM-based systems
3. Establish reusable patterns for HCG-based agent development
4. Create an extensible platform for cognitive AI research

## 2. System Architecture Overview

### 2.1 Five-Component Architecture

The LOGOS ecosystem consists of five primary components:

1. **Sophia**: Non-linguistic cognitive core
2. **Hermes**: Stateless language and embedding utilities
3. **Talos**: Hardware abstraction layer
4. **Apollo**: User interface and command layer
5. **LOGOS (this repo)**: Foundry and source of truth

### 2.2 Data Flow

```
User → Apollo → Sophia ↔ HCG (Neo4j + Milvus)
                  ↓
              Hermes (STT/TTS/NLP/Embed)
                  ↓
              Talos (Sensors/Actuators)
```

## 3. Component Specifications

### 3.1 Overview and Core Principles

The LOGOS meta-repository serves as the canonical source of truth for:
- Formal specifications and design documents
- HCG ontology definition (core_ontology.cypher)
- Validation constraints (shacl_shapes.ttl)
- API contracts (OpenAPI specifications)
- Development infrastructure (docker-compose configurations)

**Principle**: All components must reference this repository for authoritative definitions.

### 3.2 Hybrid Causal Graph (HCG)

The HCG is the central knowledge representation, combining:
- **Graph database (Neo4j)**: Stores entities, concepts, states, processes, and their causal relationships
- **Vector store (Milvus)**: Stores embeddings for semantic similarity search
- **Bidirectional sync**: Graph nodes maintain references to their vector representations

### 3.3 Sophia — Cognitive Core

Sophia implements the non-linguistic reasoning engine with five subsystems:

1. **Orchestrator**: Manages overall control flow and subsystem coordination
2. **CWM-A (Continuous World Model - Abstract)**: Maintains current abstract state representation
3. **CWM-G (Continuous World Model - Grounded)**: Maintains grounded physical/sensor state
4. **Planner**: Generates action plans using causal reasoning over the HCG
5. **Executor**: Executes plans and monitors outcomes

**Key characteristic**: All internal processing occurs in graph-structured representations.

### 3.4 Hermes — Language & Embedding Utility

Hermes provides stateless linguistic services (Table 2):

| Endpoint | Function | Input | Output |
|----------|----------|-------|--------|
| `/stt` | Speech-to-text | Audio file | Transcribed text |
| `/tts` | Text-to-speech | Text string | Audio file |
| `/simple_nlp` | NLP preprocessing | Text | Tokens, POS, NER, etc. |
| `/embed_text` | Text embedding | Text string | Vector embedding |

**Design principle**: Hermes has no state and does not access the HCG. It serves as a pure utility for Sophia.

### 3.5 Talos and Apollo

- **Talos**: Abstracts sensor/actuator hardware. In Phase 1, provides simulated interfaces for testing.
- **Apollo**: Thin client UI providing command interface and visualization of agent state.

## 4. HCG Ontology and Data Model

### 4.1 Core Ontology

The HCG ontology defines four primary node types:

1. **Entity**: Concrete objects or agents in the world (e.g., "cup", "robot arm")
2. **Concept**: Abstract categories and types (e.g., "Container", "Manipulator")
3. **State**: Temporal snapshots of entity properties (e.g., "cup is on table at t=5")
4. **Process**: Causal transformations between states (e.g., "grasping action")

**Foundational relationships**:
- `(:Entity)-[:IS_A]->(:Concept)` — Type membership
- `(:Entity)-[:HAS_STATE]->(:State)` — Current state
- `(:Process)-[:CAUSES]->(:State)` — Causal relationship
- `(:Entity)-[:PART_OF]->(:Entity)` — Compositional hierarchy

See `ontology/core_ontology.cypher` for Cypher schema definition.

### 4.2 Vector Integration

Each graph node that requires semantic search maintains:
- `embedding_id`: Reference to vector in Milvus
- `embedding_model`: Model used for embedding generation
- `last_sync`: Timestamp of last vector sync

### 4.3 Validation Framework

#### 4.3.1 SHACL Shapes for Level 1 Validation

SHACL (Shapes Constraint Language) provides deterministic validation:
- Type constraints (e.g., `uuid` must be string)
- Cardinality constraints (e.g., each Entity has exactly one uuid)
- Relationship constraints (e.g., valid relationship types)

See `ontology/shacl_shapes.ttl` for SHACL definitions.

#### 4.3.2 Level 2 Validation (Probabilistic)

Future work: ML-based validation for semantic consistency.

## 5. Infrastructure and Deployment

### 5.1 Development Environment

Requirements:
- Docker and Docker Compose
- Neo4j 5.13+ with plugins: APOC, GDS, neosemantics
- Milvus 2.3+ standalone mode
- Python 3.10+ (for Sophia, Hermes)
- Node.js 18+ (for Apollo)

### 5.2 HCG Development Cluster

The `infra/docker-compose.hcg.dev.yml` provides:
- **Neo4j**: Graph database on ports 7474 (HTTP) and 7687 (Bolt)
- **Milvus**: Vector store on ports 19530 (gRPC) and 9091 (metrics)
- **Networking**: Shared bridge network `logos-hcg-dev-net`
- **Persistence**: Named volumes for data durability

To start:
```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```

### 5.3 Production Considerations

Phase 1 focuses on development infrastructure. Production deployment will address:
- High availability and replication
- Backup and disaster recovery
- Monitoring and observability
- Security and access control

## 6. API Contracts and Integration

### 6.1 Contract-First Development

All inter-component APIs are defined via OpenAPI specifications in `contracts/`:
- `hermes.openapi.yaml`: Hermes linguistic utilities
- (Future): `sophia.openapi.yaml`, `talos.openapi.yaml`, etc.

### 6.2 Versioning Strategy

- API versions follow semantic versioning
- Breaking changes require new major version
- All components must support at least N-1 version

## 7. Development Phases and Roadmap

### 7.1 Phase 1: Formalize HCG and Abstract Pipeline

**Duration**: 8-12 weeks

**Primary deliverables**:
1. HCG ontology scaffold (COMPLETE — see `ontology/core_ontology.cypher`)
2. SHACL validation rules (COMPLETE — see `ontology/shacl_shapes.ttl`)
3. Development infrastructure (COMPLETE — see `infra/docker-compose.hcg.dev.yml`)
4. Hermes API contract (COMPLETE — see `contracts/hermes.openapi.yaml`)
5. Sophia prototype with Orchestrator + CWM-A
6. Basic planning capability (graph traversal)
7. Integration test: "Pick and place" scenario in simulation

**Success criteria**:
- Agent can maintain abstract state in HCG
- Agent can generate simple plans using causal reasoning
- All components communicate via defined contracts
- SHACL validation catches malformed graph updates

### 7.2 Phase 2: Grounding and Execution

**Duration**: 12-16 weeks

**Primary deliverables**:
1. CWM-G implementation with sensor fusion
2. Talos integration with simulated hardware
3. Executor with real-time monitoring
4. Extended planning with uncertainty handling
5. Apollo dashboard for state visualization

**Success criteria**:
- Agent can ground abstract plans to physical actions
- Agent can execute multi-step plans in simulation
- Agent can recover from execution failures

### 7.3 Phase 3: Learning and Adaptation

**Duration**: 16-20 weeks

**Primary deliverables**:
1. Episodic memory in HCG
2. Plan learning from experience
3. Level 2 probabilistic validation
4. Multi-agent coordination primitives

**Success criteria**:
- Agent improves plan quality over time
- Agent can learn new skills from demonstration
- Agent can collaborate with other agents

## 8. Appendices

### Appendix A: Full Ontology Schema

(To be populated with complete Cypher schema including all relationship types, property constraints, and indexes)

### Appendix B: Testing Strategy

**Unit tests**: Each component has isolated unit tests
**Integration tests**: Cross-component tests using docker-compose environment
**Validation tests**: SHACL validation test suite
**Performance tests**: Load testing for HCG operations

### Appendix C: Security Considerations

- Authentication and authorization for HCG access
- Encryption for inter-component communication
- Input validation for all API endpoints
- Audit logging for all HCG mutations

### Appendix D: References and Prior Art

- Knowledge graphs and semantic web technologies
- Causal reasoning and inference
- Cognitive architectures (SOAR, ACT-R, etc.)
- Hybrid neural-symbolic systems

---

**Document Status**: Living specification — updated continuously throughout development
**Version**: 1.0
**Last Updated**: 2025-11-16
