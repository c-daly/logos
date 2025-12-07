# Project LOGOS

[![CI](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A Non-Linguistic Cognitive Architecture for Autonomous Agents

LOGOS is a cognitive architecture that reasons in graph structures, not natural language. Language is just an interface—the system's internal processing uses causal graphs for planning, execution, and world modeling.

## Repositories

| Repo | Purpose | Status |
|------|---------|--------|
| **[logos](https://github.com/c-daly/logos)** (this) | Ontology, contracts, infrastructure, SDKs | Required |
| **[sophia](https://github.com/c-daly/sophia)** | Cognitive core - planning, execution, world models | Required |
| **[hermes](https://github.com/c-daly/hermes)** | Language processing, embeddings, LLM gateway | Optional |
| **[apollo](https://github.com/c-daly/apollo)** | CLI and web UI | Optional |
| **[talos](https://github.com/c-daly/talos)** | Hardware abstraction, simulators | Optional |

## Quick Start

```bash
# Clone all repos
mkdir -p ~/projects/LOGOS && cd ~/projects/LOGOS
for repo in logos hermes apollo sophia talos; do
  git clone https://github.com/c-daly/$repo.git
done

# Start infrastructure (Neo4j + Milvus)
cd logos
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Install and test
poetry install
poetry run pytest tests/unit/ -v
```

📖 **[Full Getting Started Guide](docs/guides/GETTING_STARTED.md)**

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/guides/GETTING_STARTED.md) | Clone repos, run everything, first test |
| [Architecture](docs/architecture/ARCHITECTURE.md) | How repos connect, data flow, APIs |
| [SDK Guide](docs/sdk/SDK_GUIDE.md) | Using and regenerating client SDKs |
| [Testing](docs/guides/TESTING.md) | Test categories, ports, running integration tests |
| [Infrastructure](docs/guides/INFRASTRUCTURE.md) | Neo4j, Milvus, observability setup |

### Reference

- [Phase Specifications](docs/architecture/) - Detailed architecture specs
- [API Contracts](contracts/) - OpenAPI specs for Sophia and Hermes
- [Ontology](ontology/) - Core HCG ontology and SHACL shapes

## What's in This Repo

```
logos/
├── contracts/           # OpenAPI specs (sophia.yaml, hermes.yaml)
├── ontology/            # Core ontology (Cypher) and SHACL shapes
├── infra/               # Docker Compose for Neo4j, Milvus, OTEL
├── sdk/python/          # Generated Python SDKs
├── sdk-web/             # Generated TypeScript SDKs
├── logos_config/        # Shared config utilities (ports, env)
├── logos_hcg/           # HCG client library
└── docs/                # Documentation
```

## Infrastructure

```bash
# Start Neo4j + Milvus
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Verify
docker compose -f infra/docker-compose.hcg.dev.yml ps

# Neo4j Browser: http://localhost:7474 (neo4j/neo4jtest)
# Milvus: localhost:19530
```

## Regenerating SDKs

When API contracts change:

```bash
./scripts/generate-sdks.sh
```

## Port Allocation

Each repo uses unique ports for test isolation:

| Repo | Prefix | Neo4j | Milvus |
|------|--------|-------|--------|
| hermes | 17xxx | 17474/17687 | 17530 |
| apollo | 27xxx | 27474/27687 | 27530 |
| logos | 37xxx | 37474/37687 | 37530 |
| sophia | 47xxx | 47474/47687 | 47530 |
| talos | 57xxx | 57474/57687 | 57530 |

## Roadmap

```
FOUNDATION                          INTELLIGENCE                        AUTONOMY
─────────────────────────────────────────────────────────────────────────────────────────────

Graph & Storage                     Perception                          Memory (3-tier)
  ✅ Neo4j graph database             ✅ JEPA visual encoder               ✅ Ephemeral (session)
  ✅ Milvus vector store              ✅ Image ingestion                   🔧 Short/mid-term (probationary)
  ✅ SHACL validation                 ✅ Video frame extraction            ◯ Long-term (accepted)
  ✅ HCG ontology                     ✅ Embedding generation              ◯ Reflection job
                                      ◯ Audio/speech perception           ◯ Promotion/pruning

Core Services                       Reasoning                           Persona
  ✅ Sophia planning API              ✅ Backward-chain planner            ✅ CWM-E schema
  ✅ Sophia execution API             ✅ World state modeling              ✅ Diary store
  ✅ Sophia simulation API            🔧 Counterfactual reasoning          ◯ Reflection entries
  ✅ Hermes STT/TTS                   ◯ Temporal reasoning                ◯ Identity modeling
  ✅ Hermes embeddings                ◯ Uncertainty handling              ◯ Voice/style
  ✅ Hermes LLM gateway

Interfaces                          Language                            Affect & Motivation
  ✅ Apollo CLI                       ✅ Text embeddings                   ◯ Emotional reasoning
  ✅ Apollo web dashboard             ✅ LLM integration                   ◯ Drive/goal prioritization
  ✅ Python SDK                       ◯ Grounded language                 ◯ Social cognition
  ✅ TypeScript SDK                   ◯ Dialogue management               ◯ Empathy modeling
  🔧 SDK documentation                ◯ Instruction following

Infrastructure                      Learning                            Embodiment
  ✅ Docker Compose stacks            ◯ Experience replay                 ✅ Talos simulation
  ✅ CI/CD pipelines                  ◯ Causal discovery                  ◯ Sensor integration
  ✅ Test isolation (ports)           ◯ Skill abstraction                 ◯ Motor control
  🔧 Documentation                    ◯ Transfer learning                 ◯ Real robot hardware
                                                                          ◯ Safety constraints

                                                                        Multi-Agent
                                   ✅ Done                                ◯ Agent communication
                                   🔧 In Progress                         ◯ Shared world model
                                   ◯ Planned                              ◯ Coordination protocols
                                                                          ◯ Collective learning
─────────────────────────────────────────────────────────────────────────────────────────────
```

Phase 1-2 architecture specs are preserved in [docs/architecture/](docs/architecture/) as historical reference.

## License

MIT - see [LICENSE](LICENSE)
