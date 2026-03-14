# LOGOS Foundry Specification

**Last updated:** 2026-03-04

The Foundry (`logos` repo) is the shared foundation for the LOGOS ecosystem. It provides canonical API contracts, the core ontology, the Hybrid Causal Graph (HCG) client library, shared configuration, SDKs, observability, testing utilities, and infrastructure definitions. All downstream repos (sophia, hermes, apollo, talos) depend on the Foundry for contracts, data models, and shared tooling.

---

## Table of Contents

1. [Shared Libraries](#1-shared-libraries)
2. [API Contracts](#2-api-contracts)
3. [Ontology and Data Model](#3-ontology-and-data-model)
4. [HCG Data Model](#4-hcg-data-model)
5. [Validation](#5-validation)
6. [Infrastructure](#6-infrastructure)
7. [Port Allocation](#7-port-allocation)
8. [Testing](#8-testing)
9. [Configuration](#9-configuration)

---

## 1. Shared Libraries

The Foundry provides the following Python packages, all importable by downstream repos.

### logos_config

Centralized configuration for all LOGOS repos. Provides:

- **`env`** -- Environment variable resolution with priority: OS env > provided mapping > default. Loads `.env` files with caching.
- **`ports`** -- Canonical port allocation via `RepoPorts` dataclass and `get_repo_ports(repo)` lookup. Supports env var overrides.
- **`settings`** -- Pydantic `BaseSettings` models for Neo4j (`Neo4jConfig`), Milvus (`MilvusConfig`), Redis (`RedisConfig`), OpenTelemetry (`OtelConfig`), and generic services (`ServiceConfig`).
- **`health`** -- Unified `HealthResponse` and `DependencyStatus` schemas so all LOGOS services return consistent health-check responses.

```python
from logos_config import get_env_value, get_repo_ports, Neo4jConfig, RedisConfig
ports = get_repo_ports("sophia")  # RepoPorts(neo4j_http=7474, ..., api=47000)
```

### logos_hcg

Client library for the Hybrid Causal Graph. The primary way all repos interact with Neo4j and Milvus. Provides:

- **`HCGClient`** -- Connection-pooled Neo4j client with retry logic, type-safe CRUD for nodes and edges.
- **`HCGQueries`** -- Parameterized Cypher query templates (find by UUID, find by type, traverse type hierarchy, query edges).
- **`HCGMilvusSync`** -- Bidirectional sync between Neo4j nodes and Milvus vector embeddings (upsert, delete cascade, health checks).
- **`HCGSeeder`** -- Seeds the type hierarchy and edge type definitions into a fresh graph. Usable as a library or CLI (`logos-seed-hcg`).
- **`HCGPlanner`** -- Graph-based planner that creates Goal/Plan/PlanStep nodes in the HCG.
- **`Edge`** -- Reified edge model. All domain relationships are stored as edge nodes connected via `:FROM`/`:TO` structural relationships.
- **Node models** -- `Entity`, `Concept`, `State`, `Process`, `Capability`, `Fact`, `Association`, `Abstraction`, `Rule`, `Goal`, `Plan`, `PlanStep`, `Provenance`.

### logos_test_utils

Shared testing infrastructure. Provides:

- Container helpers (`is_container_running`, `wait_for_container_health`)
- Neo4j helpers (`get_neo4j_driver`, `run_cypher_query`, `wait_for_neo4j`, `load_cypher_file`)
- Milvus helpers (`get_milvus_config`, `is_milvus_running`, `wait_for_milvus`)
- Structured logging setup (`HumanFormatter`, `StructuredFormatter`, `setup_logging`)
- Environment and config resolution (`load_stack_env`, `resolve_service_config`)

Neo4j and Milvus imports are lazy-loaded to keep the dependency footprint small for consumers that only need logging/config.

### logos_observability

OpenTelemetry instrumentation for all LOGOS services. Provides `setup_telemetry()`, `setup_metrics()`, `get_tracer()`, `get_meter()`, `get_logger()`, and `TelemetryExporter`.

### logos_cwm_e

Causal World Model -- Emotional/Social layer. A reflection job that analyzes persona entries and generates `EmotionState` tags for processes and entities. Used by planners and client surfaces to adjust behavior and tone. Provides `CWMEReflector` and a FastAPI app via `create_cwm_e_api()`.

### logos_perception

Media ingestion and imagination subsystem. Provides:

- `MediaIngestService` -- Upload/stream media frames.
- `JEPARunner` -- Interface for k-step rollout simulations (imagined future states).
- Models: `MediaFrame`, `SimulationRequest`, `SimulationResult`, `ImaginedState`, `ImaginedProcess`.

### logos_persona

Persona diary module. Stores persona diary entries in the HCG for client surfaces to query when shaping interaction tone. Provides `PersonaDiary`, `PersonaEntry`, and `create_persona_api()`.

### logos_sophia

Sophia service API stubs. Provides `create_sophia_api()` (REST endpoints for `/plan`, `/state`, `/simulate`) and `SimulationService`. These are the Foundry-side API definitions; the full cognitive implementation lives in the sophia repo.

### logos_experiment

Experiment runner framework. Provides `ExperimentConfig`, `PipelineStep`, `AgentDefinition`, `StatefulAgent`, and `ExperimentRunner` for defining and executing arrange/act/assert experiment lifecycles with reproducible seeds.

### logos_tools

Utility scripts for project management -- issue generation, project tracking, and artifact validation.

### logos_events

Redis pub/sub event bus for inter-service communication. Provides:

- **`EventBus`** -- Wrapper around `redis-py` for publishing and subscribing to channels. Publishes events in a standard envelope format (`event_type`, `source`, `timestamp`, `payload`). Supports blocking listener loops with graceful shutdown.

```python
from logos_events import EventBus
from logos_config import RedisConfig

bus = EventBus(RedisConfig())
bus.publish("sophia.plan", {"event_type": "plan_created", "source": "sophia", "payload": {...}})
bus.subscribe("sophia.plan", callback=handle_event)
```

### sdk (Python)

Auto-generated Python SDKs from the OpenAPI contracts:

- `sdk/python/hermes/` -- `logos_hermes_sdk` package
- `sdk/python/sophia/` -- `logos_sophia_sdk` package

Generated via `scripts/generate-sdks.sh` using the OpenAPI Generator.

### sdk-web (TypeScript)

Auto-generated TypeScript SDKs from the OpenAPI contracts:

- `sdk-web/hermes/` -- TypeScript client for Hermes
- `sdk-web/sophia/` -- TypeScript client for Sophia

---

## 2. API Contracts

The Foundry owns the canonical OpenAPI specifications for inter-service communication. All repos implement against these contracts (contract-first development).

| Contract | File | Description |
|----------|------|-------------|
| Hermes | `contracts/hermes.openapi.yaml` | STT, TTS, NLP, embedding generation, LLM gateway. All endpoints are stateless. |
| Sophia | `contracts/sophia.openapi.yaml` | Planner, world-model queries, imagination simulation. Backed by the HCG. |
| Apollo | `contracts/apollo.openapi.yaml` | HCG query API for the thin UI client. Entity/state retrieval, health checks. |

SDKs (Python and TypeScript) are auto-generated from these contracts and live under `sdk/` and `sdk-web/`.

---

## 3. Ontology and Data Model

The core ontology is defined in `ontology/core_ontology.cypher` and bootstrapped into Neo4j. It uses a **flexible ontology** design: a flat vocabulary where all leaf types are direct descendants of a root node, and hierarchy is discovered at runtime through graph analysis.

### Bootstrap Structure

The ontology bootstrap creates:

- **Constraints:** Unique `uuid` on all `Node` labels.
- **Indexes:** On `type`, `name`, `relation`, and compound `(type, name)`.
- **Meta-types:** `type_definition` (the type of all types) and `edge_type` (the type of all edge types).
- **Bootstrap edge types:** `IS_A` (type inheritance) and `COMPONENT_OF` (structural composition).
- **Root node:** The single root of the type hierarchy.

### Node Structure

Every node in the graph carries:

| Property | Description |
|----------|-------------|
| `uuid` | Unique identifier (string) |
| `name` | Human-readable name |
| `is_type_definition` | `true` for type nodes, `false` for instances |
| `type` | Immediate type name |
| `ancestors` | List of type names forming the inheritance chain to root |

### Seeded Type Hierarchy

The `HCGSeeder` creates additional type-definition nodes under root:

- **Domain types:** `object`, `location`
- **Reserved types:** `reserved_agent`, `reserved_process`, `reserved_action`, `reserved_goal`, `reserved_plan`, `reserved_simulation`, `reserved_execution`, `reserved_state`, `reserved_media_sample`

### Edge Types

All domain relationships are registered as type-definition nodes with `type: "edge_type"`:

`IS_A`, `COMPONENT_OF`, `ENABLES`, `ACHIEVES`, `LOCATED_AT`, `EXECUTES`, `UPDATES`, `REQUIRES`, `CAUSES`, `PRODUCES`, `OBSERVES`, `HAS_STATE`, `PART_OF`, `HAS_STEP`, `GENERATES`, `CONTAINS`, `OCCUPIES`

---

## 4. HCG Data Model

The **Hybrid Causal Graph** is the core data structure of LOGOS. It combines a labeled property graph (Neo4j) with a vector store (Milvus) to support both structured reasoning and semantic retrieval.

### Neo4j: Structured Knowledge

All data lives under a single `Node` label. Type is determined by the `type` property and the `ancestors` inheritance chain, not by Neo4j labels.

**Reified edge model:** All domain relationships are stored as **edge nodes** connected to source and target via `:FROM` and `:TO` structural relationships. These are the only native Neo4j relationship types in the graph.

```
(source:Node)<-[:FROM]-(edge:Node {type: "edge", relation: "CAUSES"})-[:TO]->(target:Node)
```

Edge nodes carry: `uuid`, `name`, `type="edge"`, `relation`, `source`, `target`, `bidirectional`, `created_at`, `updated_at`.

### Core Node Types

| Type | Purpose | Key Properties |
|------|---------|----------------|
| Entity | Concrete instances in the world | `uuid`, `name`, `description`, spatial attrs (`width`, `height`, etc.), embedding metadata |
| Concept | Abstract categories/types | `uuid`, `name`, `description`, embedding metadata |
| State | Temporal snapshots of properties | `uuid`, `timestamp`, `position`, `orientation`, physical flags, embedding metadata |
| Process | Actions that trigger state changes | `uuid`, `name`, `start_time`, `duration_ms`, embedding metadata |
| Capability | Available actions an agent can perform | `uuid`, `name`, `executor_type` |
| Fact | Grounded assertions with confidence | `uuid`, `content`, `status`, `confidence` |
| Rule | Causal/definitional rules | `uuid`, `condition`, `consequence`, `rule_type` |
| Goal | Planning targets | `uuid`, `description`, `status` |
| Plan | Ordered sequences of steps | `uuid`, `goal_id`, `status` |
| PlanStep | Individual actions within a plan | `uuid`, `action`, `sequence` |

### Milvus: Semantic Retrieval

Milvus stores vector embeddings for graph nodes, enabling similarity search. Each node type maps to a Milvus collection:

| Node Type | Collection |
|-----------|------------|
| Entity | `hcg_entity_embeddings` |
| Concept | `hcg_concept_embeddings` |
| State | `hcg_state_embeddings` |
| Process | `hcg_process_embeddings` |
| Edge | `hcg_edge_embeddings` |
| TypeCentroid | `hcg_type_centroids` |

The `HCGMilvusSync` utility keeps Neo4j and Milvus in sync -- upserts, deletes, and consistency health checks. The default embedding dimension is 384 (configurable via `LOGOS_EMBEDDING_DIM`).

### How They Work Together

1. **Structured queries** (type hierarchy, causal chains, plan traversal) go through Neo4j via `HCGClient`/`HCGQueries`.
2. **Semantic queries** (find similar concepts, nearest-neighbor retrieval) go through Milvus.
3. **Sync** keeps both stores consistent: when a node is created/updated in Neo4j, its embedding is upserted to Milvus; when a node is deleted, its embedding is removed.

---

## 5. Validation

Structural validation in the HCG is enforced through the **graph's own type system and topology**, not through an external schema language.

### Type-Ancestry Constraints

- Every node has a `type` and `ancestors` list tracing its lineage to root.
- Type-definition nodes (`is_type_definition: true`) define the vocabulary. Instance nodes (`is_type_definition: false`) are typed against these definitions.
- `IS_A` edges encode inheritance. `COMPONENT_OF` edges encode structural composition.
- The seeder and client enforce that nodes reference valid types from the hierarchy.

### Edge Constraints

- Edge types are themselves type-definition nodes (with `type: "edge_type"`).
- Creating an edge requires both source and target to exist and the relation to be a registered edge type.
- The reified edge model means edge metadata (timestamps, provenance) is queryable like any other node.

### Ontology Validation Script

The `ontology/validate_ontology.py` script checks structural integrity of the loaded graph (e.g., orphaned nodes, missing type definitions, broken IS_A chains).

---

## 6. Infrastructure

The Foundry provides Docker Compose files for the shared infrastructure that all repos depend on.

### HCG Development Cluster

**File:** `infra/docker-compose.hcg.dev.yml`

Provisions:

| Service | Image | Purpose |
|---------|-------|---------|
| `logos-hcg-neo4j` | `neo4j:5.11.0` | Graph database for the HCG |
| `logos-hcg-milvus` | `milvusdb/milvus:v2.3.3` | Vector database for embeddings |

Both services run on a shared `logos-hcg-dev-net` bridge network with health checks.

### Per-Repo Test Stacks

Each downstream repo has a test compose file under `infra/{repo}/docker-compose.test.yml` (for hermes, sophia, apollo, talos). These are generated from templates and provision isolated Neo4j, Milvus, and Redis instances for CI.

### Observability Stack

**Repo:** [`c-daly/logos-otel`](https://github.com/c-daly/logos-otel) (cloned to `~/.claude/infra/otel/`)

Full observability stack: OTel collector, Prometheus, Loki, Tempo, Grafana, plus custom exporters for Claude Code and agent-swarm metrics. See the repo README for setup.

### Useful Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup-local-dev.sh` | One-shot local development setup |
| `scripts/start_services.sh` | Start the dev infrastructure |
| `scripts/start_test_services.sh` | Start test infrastructure |
| `scripts/test_unit.sh` | Run unit tests |
| `scripts/test_integration.sh` | Run integration tests |
| `scripts/test_e2e.sh` | Run end-to-end tests |
| `scripts/generate-sdks.sh` | Regenerate Python/TypeScript SDKs from contracts |
| `scripts/lint.sh` | Run ruff + formatting checks |

---

## 7. Port Allocation

All LOGOS repos share infrastructure (Neo4j, Milvus, Redis) on default ports. Each repo has a unique API port.

| Repo | API Port | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Metrics | Redis |
|------|----------|------------|------------|-------------|----------------|-------|
| hermes | 17000 | 7474 | 7687 | 19530 | 9091 | 6379 |
| apollo | 27000 | 7474 | 7687 | 19530 | 9091 | 6379 |
| logos | 37000 | 7474 | 7687 | 19530 | 9091 | 6379 |
| sophia | 47000 | 7474 | 7687 | 19530 | 9091 | 6379 |
| talos | 57000 | 7474 | 7687 | 19530 | 9091 | 6379 |

All ports are overridable via environment variables (`NEO4J_HTTP_PORT`, `NEO4J_BOLT_PORT`, `MILVUS_PORT`, `MILVUS_METRICS_PORT`, `REDIS_PORT`, `API_PORT`).

Use `logos_config.get_repo_ports("repo_name")` for programmatic access.

---

## 8. Testing

See `docs/TESTING.md` for full testing standards.

### Running Tests

```bash
# Unit tests
./scripts/test_unit.sh
# or
poetry run pytest tests/unit/

# Integration tests (requires running infra)
./scripts/test_integration.sh
# or
poetry run pytest tests/integration/

# End-to-end
./scripts/test_e2e.sh

# Linting
./scripts/lint.sh
# or
poetry run ruff check --fix . && poetry run ruff format .
```

### Test Utilities

The `logos_test_utils` package provides fixtures, container management, and database helpers. Integration tests that need Neo4j or Milvus should use the helpers from this package to wait for service readiness before running queries.

---

## 9. Configuration

### Environment Variables

`logos_config` resolves configuration with the following priority:

1. **OS environment variable** (highest priority)
2. **Provided env mapping** (e.g., from a loaded `.env` file)
3. **Default value** (lowest priority)

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_HOST` | `localhost` | Neo4j hostname |
| `NEO4J_HTTP_PORT` | `7474` | Neo4j HTTP API port |
| `NEO4J_BOLT_PORT` | `7687` | Neo4j Bolt protocol port |
| `NEO4J_PASSWORD` | `logosdev` | Neo4j password |
| `MILVUS_HOST` | `localhost` | Milvus hostname |
| `MILVUS_PORT` | `19530` | Milvus gRPC port |
| `MILVUS_COLLECTION_NAME` | `embeddings` | Default Milvus collection |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_PASSWORD` | *(none)* | Redis password (optional) |
| `LOGOS_EMBEDDING_DIM` | `384` | Vector embedding dimension |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OpenTelemetry collector endpoint |
| `API_PORT` | *(per repo)* | Service API port |

### Pydantic Settings Models

Each config class (`Neo4jConfig`, `MilvusConfig`, `RedisConfig`, `OtelConfig`, `ServiceConfig`) extends Pydantic `BaseSettings` with env-prefixed variable binding. Downstream repos can subclass these for repo-specific settings.

```python
from logos_config import Neo4jConfig, MilvusConfig, RedisConfig

neo4j = Neo4jConfig(password="logosdev")
print(neo4j.uri)       # bolt://localhost:7687
print(neo4j.http_url)  # http://localhost:7474

milvus = MilvusConfig()
print(milvus.port)     # 19530

redis = RedisConfig()
print(redis.url)   # redis://localhost:6379/0
```
