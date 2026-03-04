# CLAUDE.md — logos (Foundry)

## What This Is

The Foundry: canonical source of truth for LOGOS specifications, ontology, shared libraries, and infrastructure.

All other repos depend on logos via the `logos-foundry` PyPI package.

## Dependencies

- **Neo4j** (7474/7687) — graph database for HCG
- **Milvus** (19530) — vector storage for embeddings
- **Redis** (6379) — pub/sub events, caching
- **Python** >=3.12, **Poetry** for dependency management

## Key Commands

```bash
# Install
poetry install --with dev,test

# Lint & format
poetry run ruff check --fix .
poetry run black .
poetry run mypy logos_config logos_hcg logos_observability

# Test
poetry run pytest tests/ -x -q                      # all tests
poetry run pytest tests/unit -x -q                   # unit only (no services)
poetry run pytest tests/integration -x -q            # needs Neo4j + Milvus

# Infrastructure
docker compose -f infra/docker-compose.hcg.dev.yml up -d
bash infra/load_ontology.sh                          # seed Neo4j with ontology

# SDK generation
bash scripts/generate-sdks.sh
```

---

## Package Catalog

The Foundry exports these packages (all at repo root, published via `logos-foundry`):

| Package | Purpose |
|---------|---------|
| `logos_config` | Shared config: `Neo4jConfig`, `MilvusConfig`, `RedisConfig`, `OtelConfig`, `ServiceConfig`, port allocation |
| `logos_hcg` | HCG client: `HCGClient`, models, queries, planner, seeder, Milvus sync |
| `logos_events` | Pub/sub: `EventBus` over Redis for inter-service event distribution |
| `logos_observability` | OpenTelemetry: `setup_telemetry`, `get_logger`, `get_tracer`, `get_meter` |
| `logos_persona` | Persona diary: `PersonaDiary`, `PersonaEntry`, FastAPI router |
| `logos_cwm_e` | Emotional CWM: `CWMEReflector`, `EmotionState`, FastAPI router |
| `logos_sophia` | Sophia API helpers: `create_sophia_api`, `SimulationService` |
| `logos_perception` | Media ingestion: `MediaIngestService`, `JEPARunner`, `JEPAConfig` |
| `logos_test_utils` | Test helpers: Neo4j/Milvus fixtures, container health, env loading |
| `logos_tools` | Infrastructure utilities: issue generation, project tracking |

**Not packaged** (directory exists but not in pyproject.toml):
- `logos_experiment` — experiment framework (`ExperimentRunner`, `StatefulAgent`, `PipelineStep`)

### Port Allocation (`logos_config.ports`)

Only API ports vary per repo. Infrastructure is shared on default ports.

| Repo | API Port |
|------|----------|
| hermes | 17000 |
| apollo | 27000 |
| logos | 37000 |
| sophia | 47000 |
| talos | 57000 |

Infrastructure: Neo4j 7474/7687, Milvus 19530/9091, Redis 6379.

---

## Architecture

```
logos/
├── contracts/           # OpenAPI specs (apollo, hermes, sophia)
├── ontology/            # Cypher schemas, SHACL shapes, validation
├── infra/               # Docker Compose, init scripts, OTEL config
├── logos_config/        # Shared configuration (ports, settings, env)
├── logos_hcg/           # HCG client library (Neo4j + Milvus)
├── logos_events/        # Redis pub/sub event bus
├── logos_observability/ # OpenTelemetry instrumentation
├── logos_persona/       # Persona diary system
├── logos_cwm_e/         # Emotional CWM reflection
├── logos_sophia/        # Sophia API helpers
├── logos_perception/    # Media ingestion, JEPA runner
├── logos_test_utils/    # Shared test fixtures and helpers
├── logos_tools/         # Issue generation, project tracking
├── logos_experiment/    # Experiment runner framework (not packaged)
├── planner_stub/        # Proof-of-concept planning service
├── sdk/                 # Generated Python SDKs (do not edit)
├── sdk-web/             # Generated TypeScript SDKs (do not edit)
├── scripts/             # Dev, test, SDK, deployment scripts
├── tests/               # unit/, integration/, e2e/, contracts/
├── docs/                # Architecture, specs, ADRs, plans, operations
└── examples/            # Demo scripts
```

## Contracts & Ontology

- **OpenAPI contracts** in `contracts/` define API surfaces for sophia, hermes, apollo
- **Cypher schemas** in `ontology/` define HCG node/edge types
- **SHACL shapes** in `ontology/shacl_shapes.ttl` for graph validation
- Contract changes here flow downstream — update logos first, then propagate

---

## CI Workflows

Reusable workflows in `.github/workflows/` (consumed by all downstream repos):
- `reusable-standard-ci.yml` — standard lint/test/build pipeline
- `reusable-pr-checks.yml` — issue linkage and branch naming checks
- `reusable-publish.yml` — package publishing

Additional workflows cover phase gates, SDK generation, publishing, triage, and validation. Check `.github/workflows/` for the full list.

---

## Conventions & Gotchas

- **Ruff** for linting, **black** for formatting (both enforced via pre-commit)
- `sdk/` and `sdk-web/` are auto-generated — never edit manually
- Tests needing Neo4j/Milvus go in `tests/integration/`, not `tests/unit/`
- `planner_stub/` is a PoC, not production code
- When bumping foundry version, run `scripts/bump-downstream.sh` to update all repos

---

## Docs

Detailed documentation in `docs/`:
- `architecture/` — system architecture, phase specs, ADRs
- `operations/` — testing, port reference, publishing, CI, demos
- `observability/` — OTEL infrastructure setup
- `plans/` — design docs and implementation plans
- `evidence/` — phase gate evidence

Key files: `GIT_PROJECT_STANDARDS.md`, `TESTING_STANDARDS.md`, `LOCAL_DEVELOPMENT.md`

## Issue Templates

| Template | Use For |
|----------|---------|
| `infrastructure-task.yml` | HCG, ontology, CI/CD, foundry tasks |
| `research-task.yml` | Research and investigation |
| `documentation-task.yml` | Documentation updates |
