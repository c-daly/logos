# LOGOS Testing Documentation

This document defines the testing standards, strategy, and best practices for all repositories in the Project LOGOS ecosystem.

**Last Updated:** November 2025

---

## Core Philosophy

1. **Consistency**: All repositories use the same tooling (Pytest, Poetry) and CI workflows.
2. **Reliability**: Tests must be deterministic. Flaky tests should be fixed, not ignored.
3. **Completeness**: Integration tests running in CI are mandatory for services with external dependencies (Milvus, Neo4j).

---

## Tooling Stack

All Python repositories must use:

| Tool | Purpose |
|------|---------|
| `pytest` | Test runner |
| `poetry` | Dependency management |
| `ruff` | Linting |
| `black` | Formatting |
| `mypy` | Type checking |
| `pytest-cov` | Coverage (uploading to Codecov) |

---

## Test Categories

### 1. Unit Tests (Repository-Specific)

**Scope:** Individual functions, classes, and modules in isolation.

| Aspect | Requirement |
|--------|-------------|
| Dependencies | Must be mocked (`unittest.mock`, `pytest-mock`) |
| Speed | < 100ms per test |
| Location | `tests/` or `tests/unit/` |

**Current status across repos:**
- ✅ Hermes: Component tests with mock services
- ✅ Sophia: API tests, JEPA integration tests, CWM tests
- ✅ Apollo: CLI tests, client tests, backend API tests
- ✅ Talos: Executor tests, integration tests with Neo4j
- ✅ Logos: Phase 1 milestone tests, ontology validation

### 2. Integration Tests (Repository-Specific)

**Scope:** Interaction between the application and external services (Databases, APIs).

| Aspect | Requirement |
|--------|-------------|
| Dependencies | Real instances via Docker Compose. **Do not mock database drivers** |
| Markers | Must use `@pytest.mark.integration` |
| Location | `tests/integration/` or `tests/` with integration marker |

**Infrastructure per repo:**
- **Hermes:** `docker-compose.test.yml` (Milvus + Neo4j, ports 7687, 7474, 19530, 9091)
- **Sophia:** Uses `logos/infra/docker-compose.hcg.dev.yml`
- **Apollo:** `tests/e2e/docker-compose.e2e.yml` (Neo4j + mock services)
- **Talos:** Uses shared infrastructure or skips if Neo4j unavailable

### 3. End-to-End Tests (Logos Orchestrator)

**Scope:** Full user flows across multiple services.

**Location:** `logos/tests/phase2/test_phase2_end_to_end.py`

**Infrastructure:** `logos/tests/phase2/docker-compose.test.yml`
- Neo4j 5.14.0, Milvus 2.3.3 (with etcd/MinIO)
- Ports: 7687, 7474 (Neo4j), 8001 (Sophia), 8002 (Hermes), 8003 (Apollo), 19530, 9091 (Milvus)
- Credentials: `neo4j/logosdev`, `SOPHIA_API_KEY=test-token-12345`

**Run manually:**
```bash
cd logos/tests/phase2
docker compose -f docker-compose.test.yml up -d
cd ../..
SOPHIA_API_KEY=test-token-12345 RUN_P2_E2E=1 poetry run pytest tests/phase2/test_phase2_end_to_end.py -v
```

---

## CI/CD Requirements

### The "No Skip in CI" Rule

**Never** skip tests solely because they are running in CI.

```python
# ❌ BAD - Don't do this
@pytest.mark.skipif(os.environ.get("CI"), reason="slow")
def test_something():
    ...

# ✅ GOOD - Use markers and run in specialized jobs
@pytest.mark.integration
def test_something():
    ...
```

If a test requires a database, spin it up using Docker Compose in the workflow.

### Reusable Workflow

All repositories must use: `c-daly/logos/.github/workflows/reusable-standard-ci.yml`

See [CI Documentation](ci/README.md) for details.

---

## Best Practices

### Fixtures

Use `pytest` fixtures for setup and teardown:

```python
@pytest.fixture
def milvus_collection():
    collection = create_collection()
    yield collection
    collection.drop()
```

### Async Testing

Use `pytest-asyncio` for async code:

```python
@pytest.mark.asyncio
async def test_websocket_handler():
    ...
```

### Docker Compose for Integration

Define `docker-compose.test.yml` that exposes services on localhost. CI workflow starts these before tests.

### Retry Logic

For async indexing (Milvus, Elasticsearch), use retry loops:

```python
# ✅ Good
for _ in range(10):
    if check_condition():
        break
    time.sleep(0.5)

# ❌ Bad
time.sleep(5)  # Flaky and slow
```

### Test Isolation

- Tests should be independent and runnable in any order
- Use fixtures for setup/teardown, not test dependencies
- Clean up test data (use `clean_neo4j`, `clean_milvus` fixtures)
- Prefix test data with `test_` for easy cleanup

---

## Running Tests

### Per-Repository Unit Tests

```bash
# Any repo
cd <repo>
poetry run pytest
```

### Hermes with Infrastructure

```bash
cd hermes
docker compose -f docker-compose.test.yml up -d
poetry run pytest tests/test_milvus_integration.py
docker compose -f docker-compose.test.yml down -v
```

### Phase 2 E2E (Full Stack)

```bash
cd logos/tests/phase2
docker compose -f docker-compose.test.yml up -d
cd ../..
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py -v
cd tests/phase2
docker compose -f docker-compose.test.yml down -v
```

### Phase 1 Milestones

```bash
cd logos
RUN_M4_E2E=1 pytest tests/phase1/test_m4_end_to_end.py
```

---

## Environment Variables

```bash
# Enable E2E tests
RUN_P2_E2E=1
RUN_M4_E2E=1

# Service URLs
SOPHIA_URL=http://localhost:8001
HERMES_URL=http://localhost:8002
APOLLO_URL=http://localhost:8003

# Database connections (standardized across all repos)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=logosdev

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

---

## Shared Test Utilities (`logos_test_utils`)

**Location:** `logos/logos_test_utils/`

The `logos_test_utils` package provides standardized helpers and pytest fixtures for all LOGOS repos.

### Available Helpers

```python
# Environment loading
from logos_test_utils.env import load_stack_env, get_env_value

# Neo4j utilities
from logos_test_utils.neo4j import (
    get_neo4j_config,
    get_neo4j_driver,
    wait_for_neo4j,
    load_cypher_file,
    run_cypher_query,
)

# Milvus utilities
from logos_test_utils.milvus import (
    get_milvus_config,
    wait_for_milvus,
)

# Docker helpers
from logos_test_utils.docker import (
    is_container_running,
    wait_for_container_health,
    get_container_logs,
)
```

### Pytest Fixtures (For Downstream Repos)

Downstream repos (apollo, hermes, sophia, talos) can import ready-to-use fixtures:

```python
# In conftest.py
from logos_test_utils.fixtures import (
    stack_env,
    neo4j_config,
    neo4j_driver,
    load_cypher,
)

# In tests
def test_something(neo4j_driver):
    with neo4j_driver.session() as session:
        result = session.run("RETURN 1 AS test")
        assert result.single()["test"] == 1
```

### Installation in Downstream Repos

Add to `pyproject.toml`:
```toml
[tool.poetry.group.dev.dependencies]
logos-test-utils = {path = "../logos", develop = true}
```

### Configuration Priority

Helpers follow this resolution order:
1. OS environment variables (highest priority)
2. `.env.test` file from generated stack
3. Hardcoded defaults (lowest priority)

This allows CI overrides while maintaining local defaults.

---

## Test Stack Generator

**Tool:** `logos/infra/scripts/render_test_stacks.py`

Generates standardized docker-compose and environment files for each repo with unique port assignments.

### Usage

```bash
# Generate all repos
poetry run python logos/infra/scripts/render_test_stacks.py

# Generate specific repo
poetry run python logos/infra/scripts/render_test_stacks.py --repo apollo

# Verify no drift
poetry run python logos/infra/scripts/render_test_stacks.py --check
```

### Port Assignments

| Repo | Neo4j Bolt | Neo4j HTTP | Milvus | Milvus Admin |
|------|------------|------------|--------|--------------|
| logos (dev) | 7687 | 7474 | 19530 | 9091 |
| apollo | 27687 | 27474 | 29530 | 29091 |
| hermes | 19687 | 19474 | 19530 | 19091 |
| sophia | 37687 | 37474 | 39530 | 39091 |
| talos | 47687 | 47474 | 49530 | 49091 |

See `docs/operations/PORT_REFERENCE.md` for complete port map.

### Output Files

For each repo:
- `tests/e2e/stack/<repo>/docker-compose.test.<repo>.yml`
- `tests/e2e/stack/<repo>/.env.test`
- `tests/e2e/stack/<repo>/STACK_VERSION`

---

## Migration Guide

For repos adopting the standardized test infrastructure, see:
- `docs/operations/TEST_STANDARDIZATION_MIGRATION.md` - Step-by-step migration guide
- `docs/operations/PORT_REFERENCE.md` - Quick reference for port assignments

---

## Completed Improvements ✅

| Item | Completed | Issue |
|------|-----------|-------|
| Port standardization | ✅ Nov 2025 | #326, #358 |
| Shared `logos_test_utils` package | ✅ Nov 2025 | #326, #367 |
| Test stack generator | ✅ Nov 2025 | #358 |
| Credential standardization | ✅ Nov 2025 | #369 |

## Future Improvements

| Item | Issue |
|------|-------|
| Browser E2E tests (Playwright) | #315 |
| OpenTelemetry testing | #321 |
| Media ingestion testing | #240 |

---

## Related Documentation

- [CI/CD Documentation](ci/README.md)
- [Phase 2 Verification](PHASE2_VERIFY.md)
- [Observability Queries](OBSERVABILITY_QUERIES.md)
