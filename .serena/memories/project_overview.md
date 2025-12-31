# Logos Project Overview

## Purpose
Logos is the **foundry** for the LOGOS cognitive architecture—home to canonical contracts, shared ontology, reusable SDKs, and ecosystem-wide standards. It is the **upstream source of truth** for contracts, ontology, and standards that ripple to all downstream repos (sophia, hermes, talos, apollo).

## Tech Stack
- **Language:** Python 3.11+
- **Package Manager:** Poetry
- **Framework:** FastAPI + Pydantic v2
- **Database:** Neo4j (graph), Milvus (vector)
- **Linting:** Ruff (replaces flake8, isort, black)
- **Type Checking:** Mypy
- **Testing:** Pytest
- **CI:** GitHub Actions (reusable workflows)
- **Observability:** OpenTelemetry

## Key Packages
| Package | Purpose |
|---------|---------|
| `logos_hcg` | Hybrid Causal Graph client library |
| `logos_config` | Shared configuration utilities (env, ports, settings) |
| `logos_sophia` | Sophia SDK stubs |
| `logos_perception` | Perception utilities |
| `logos_cwm_e` | CWM-E (Episodic memory) |
| `logos_persona` | Persona management |
| `logos_observability` | Telemetry/tracing helpers |
| `logos_test_utils` | Shared test utilities |
| `logos_tools` | CLI tools for issue generation |

## Key Directories
- `contracts/` – OpenAPI specifications
- `ontology/` – Cypher schemas and SHACL shapes
- `docs/standards/` – Ecosystem-wide standards
- `.github/workflows/` – Reusable CI workflows
- `infra/` – Infrastructure configuration

## Port Allocation
Logos uses +30000 offset: Neo4j HTTP 37474, Bolt 37687, Milvus 37530, API 37000
