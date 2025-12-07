# LOGOS Architecture

## System Overview

LOGOS is a non-linguistic cognitive architecture. The system reasons in graph structures, not natural language. Language is just an interface handled by Hermes.

```
User → Apollo → Sophia ↔ HCG (Neo4j + Milvus)
        (UI)    (Brain)     (Knowledge)
                   ↓
               Hermes (Language/Embeddings)
                   ↓
               Talos (Hardware/Simulation)
```

## Components

| Component | Purpose | Required? |
|-----------|---------|-----------|
| **Sophia** | Cognitive core - planning, execution, world models | Yes |
| **LOGOS (this repo)** | Ontology, contracts, infrastructure, SDKs | Yes |
| **Neo4j** | Graph database for the Hybrid Cognitive Graph | Yes |
| **Milvus** | Vector database for semantic search | Yes |
| **Hermes** | Language processing, embeddings, LLM gateway | Optional |
| **Apollo** | CLI and web UI | Optional |
| **Talos** | Hardware abstraction, simulators | Optional |

## Data Flow

1. **User input** arrives via Apollo (CLI or web)
2. **Apollo** calls Sophia's API (plan, execute, simulate)
3. **Sophia** reads/writes the HCG (Neo4j + Milvus)
4. **Sophia** calls Hermes for language/embedding tasks
5. **Sophia** calls Talos to execute physical actions (or simulate them)
6. **Results** flow back up to Apollo for display

## The Hybrid Cognitive Graph (HCG)

The HCG is the system's memory and knowledge store:

- **Neo4j**: Stores entities, concepts, states, processes, and their relationships
- **Milvus**: Stores vector embeddings for semantic similarity search
- **SHACL**: Validates graph structure against constraints

Nodes in Neo4j reference their embeddings in Milvus via `embedding_id`.

## Sophia's World Models

Sophia maintains multiple layers of understanding:

| Model | Purpose |
|-------|---------|
| **CWM-A** (Abstract) | Symbolic knowledge from the HCG - concepts, relationships, rules |
| **CWM-G** (Grounded) | Physics/perception - predicts what happens when actions execute |
| **CWM-E** (Emotional) | Confidence, trust, persona state |

Plans are validated against both CWM-A (semantically correct) and CWM-G (physically plausible).

## Deployment Modes

| Mode | What's Running |
|------|----------------|
| **Graph-only** | Apollo CLI + Sophia + Neo4j/Milvus (no hardware) |
| **Perception-only** | + Hermes for language/vision processing |
| **Simulated** | + Talos simulators for pick-and-place, etc. |
| **Physical** | + Talos drivers for real robots/sensors |

## API Contracts

OpenAPI specs live in `logos/contracts/`:
- `sophia.openapi.yaml` - Sophia's REST API
- `hermes.openapi.yaml` - Hermes's REST API

SDKs are generated from these contracts. See [SDK Guide](SDK_GUIDE.md).

## Key APIs

### Sophia (port 8000)

| Endpoint | Purpose |
|----------|---------|
| `POST /plan` | Generate a plan for a goal |
| `POST /execute` | Execute a plan step |
| `POST /simulate` | Predict outcomes without acting |
| `POST /ingest` | Add media/knowledge to the HCG |
| `GET /state` | Current cognitive state |
| `GET /health` | Service health |

### Hermes (port 8080)

| Endpoint | Purpose |
|----------|---------|
| `POST /stt` | Speech to text |
| `POST /tts` | Text to speech |
| `POST /embed` | Generate text embeddings |
| `POST /llm` | LLM chat completion proxy |
| `GET /health` | Service health |

## Phase Roadmap

1. **Phase 1** ✅ - HCG foundation, ontology, CLI prototype
2. **Phase 2** ✅ - Services, Apollo UI, perception pipeline
3. **Phase 3** 📋 - Learning, episodic memory, optional physical demos
4. **Phase 4** - Continuous learning, production deployment
5. **Phase 5** - Multi-agent coordination, swarm

Detailed specs: `docs/architecture/PHASE{1,2,3}_SPEC.md`
