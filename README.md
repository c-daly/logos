# Project LOGOS

[![CI](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A Non-Linguistic Cognitive Architecture for Autonomous Agents

LOGOS is a cognitive architecture that reasons in graph structures, not natural language. Language is just an interface—the system's internal processing uses causal graphs for planning, execution, and world modeling.

## Documentation

**[Wiki](https://github.com/c-daly/logos/wiki)** - Full documentation

| Page | Description |
|------|-------------|
| [Getting Started](https://github.com/c-daly/logos/wiki/Getting-Started) | Setup, installation, first run |
| [Architecture](https://github.com/c-daly/logos/wiki/Architecture) | System overview, data flow |
| [Specification](https://github.com/c-daly/logos/wiki/Specification) | Unified spec with status markers |
| [HCG & Ontology](https://github.com/c-daly/logos/wiki/HCG-Ontology) | Graph model, Neo4j, Milvus |
| [CWM Layers](https://github.com/c-daly/logos/wiki/CWM-Layers) | Abstract, Grounded, Emotional |
| [Testing Standards](https://github.com/c-daly/logos/wiki/Testing-Standards) | Test conventions |
| [Git Workflow](https://github.com/c-daly/logos/wiki/Git-Workflow) | Branching, commits, PRs |
| [Templates](https://github.com/c-daly/logos/wiki/Templates) | Issue and PR templates |

## Repositories

| Repo | Purpose | Port |
|------|---------|------|
| **[logos](https://github.com/c-daly/logos)** (this) | Foundry - ontology, contracts, SDKs, shared tooling | 38000 |
| **[sophia](https://github.com/c-daly/sophia)** | Cognitive core - planning, execution, world models | 48000 |
| **[hermes](https://github.com/c-daly/hermes)** | Language processing - embeddings, NLP, STT/TTS | 18000 |
| **[talos](https://github.com/c-daly/talos)** | Hardware abstraction - simulators, capabilities | 58000 |
| **[apollo](https://github.com/c-daly/apollo)** | User interface - CLI, web dashboard | 28000 |

## Quick Start

```bash
# Clone all repos
mkdir -p ~/projects/LOGOS && cd ~/projects/LOGOS
for repo in logos sophia hermes talos apollo; do
  git clone https://github.com/c-daly/$repo.git
done

# Start infrastructure (Neo4j + Milvus)
cd logos
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Install and test
poetry install
poetry run pytest tests/unit/ -v
```

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
├── docs/architecture/   # ADRs and historical specs
└── .github/             # Issue templates, labels, CI workflows
```

## Infrastructure

```bash
# Start Neo4j + Milvus
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Neo4j Browser: http://localhost:7474 (neo4j/neo4jtest)
# Milvus: localhost:19530
```

## Regenerating SDKs

When API contracts change:

```bash
./scripts/generate-sdks.sh
```

## License

MIT - see [LICENSE](LICENSE)
