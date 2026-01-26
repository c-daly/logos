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
| `pytest-cov` | Coverage (Codecov upload currently disabled; generate XML locally) |

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
- **Hermes:** `docker-compose.test.yml` (Milvus + Neo4j, ports 17687, 17474, 17530, 17091)
- **Sophia:** Uses `logos/infra/docker-compose.hcg.dev.yml`
- **Apollo:** `tests/e2e/docker-compose.e2e.yml` (Neo4j + mock services)
- **Talos:** Uses shared infrastructure or skips if Neo4j unavailable

### 3. End-to-End Tests (Logos Orchestrator)

**Scope:** Full user flows across multiple services.

**Location:** `logos/tests/e2e/test_phase2_end_to_end.py`

**Infrastructure:** `logos/tests/e2e/stack/logos/docker-compose.test.yml` (managed via `tests/e2e/run_e2e.sh`)
- Neo4j 5.14.0, Milvus 2.4.x (with etcd/MinIO)
- Ports: 37687, 37474 (Neo4j), 8001 (Sophia), 8002 (Hermes), 8003 (Apollo), 37530, 37091 (Milvus)
- Credentials: `neo4j/neo4jtest`, `SOPHIA_API_KEY=test-token-12345`

**Run manually:**
```bash
./tests/e2e/run_e2e.sh up
SOPHIA_API_KEY=test-token-12345 RUN_P2_E2E=1 poetry run pytest tests/e2e/test_phase2_end_to_end.py -v
./tests/e2e/run_e2e.sh down
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

Notes:
- Coverage upload to Codecov is currently disabled; keep generating `coverage.xml` locally for quality gates.
- Perception workflow jobs have switched to Poetry; align local runs with the workflow commands.

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

### End-to-End (Full Stack)

```bash
cd logos
./tests/e2e/run_e2e.sh up
RUN_P2_E2E=1 pytest tests/e2e/test_phase2_end_to_end.py -v
./tests/e2e/run_e2e.sh down
```

### Phase 1 Milestones

```bash
cd logos
RUN_M4_E2E=1 pytest tests/e2e/test_phase1_end_to_end.py
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

# Database connections
NEO4J_URI=bolt://localhost:37687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=37530
```

---

## Known Issues

### Port Conflicts

⚠️ Multiple Logos test environments use the same ports (37474, 37687, 37530, 37091). Running multiple Logos test stacks simultaneously will fail.

**Workaround:** Run test suites sequentially.

### Credential Inconsistencies

⚠️ Hermes uses `neo4j/password` while others use `neo4j/neo4jtest`.

---

## Future Improvements

| Item | Issue |
|------|-------|
| Port standardization | #326 |
| Shared `logos_test_utils` package | #326 |
| Browser E2E tests (Playwright) | #315 |
| OpenTelemetry testing | #321 |
| Media ingestion testing | #240 |

---

## Related Documentation

- [CI/CD Documentation](ci/README.md)
- [Phase 2 Verification](PHASE2_VERIFY.md)
- [Observability Queries](OBSERVABILITY_QUERIES.md)
- [Local Development](../LOCAL_DEVELOPMENT.md)

---

## Shared Test Utilities (logos_test_utils)

All LOGOS repositories share a common testing library: `logos_test_utils`. This package is the canonical source for test fixtures and helpers.

### Installing in Your Repo

Add to `pyproject.toml`:
```toml
[tool.poetry.group.dev.dependencies]
logos-test-utils = {path = "../logos", develop = true}
```

### Importing Shared Fixtures

In your `conftest.py`:
```python
from logos_test_utils.fixtures import (
    stack_env,       # Parsed environment from .env.test
    neo4j_config,    # Neo4j connection configuration
    neo4j_driver,    # Connected Neo4j driver (session-scoped)
    load_cypher,     # Helper to load .cypher files
)
```

### Available Helpers

Import directly from the package:
```python
from logos_test_utils import (
    load_stack_env,        # Load environment from .env.test
    get_neo4j_config,      # Build Neo4jConfig from env
    get_neo4j_driver,      # Create connected driver
    get_milvus_config,     # Build MilvusConfig from env
    wait_for_neo4j,        # Block until Neo4j is ready
    wait_for_milvus,       # Block until Milvus is ready
    setup_logging,         # Configure structured logging
)
```

---

## Port Allocation Scheme

Each repository has a unique port prefix to prevent conflicts when running tests in parallel (local or CI).

### Port Table

| Repo   | Prefix | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Metrics | API   |
|--------|--------|------------|------------|-------------|----------------|-------|
| hermes | 17     | 17474      | 17687      | 17530       | 17091          | 17000 |
| apollo | 27     | 27474      | 27687      | 27530       | 27091          | 27000 |
| logos  | 37     | 37474      | 37687      | 37530       | 37091          | 37000 |
| sophia | 47     | 47474      | 47687      | 47530       | 47091          | 47000 |
| talos  | 57     | 57474      | 57687      | 57530       | 57091          | 57000 |

### Container-Internal vs Host-Mapped Ports

Services inside containers listen on standard ports (e.g., Neo4j on 7687, API on 8080). The repo-specific ports are host-mapped:

```
Container (internal)          Host (mapped)
-------------------------     -----------------
neo4j:7687           --->     localhost:47687 (sophia)
sophia-api:8080      --->     localhost:47000 (sophia)
```

### Using Port Allocation in Code

```python
from logos_config.ports import get_repo_ports

# Get ports for your repo
ports = get_repo_ports("sophia")
print(ports.neo4j_bolt)   # 47687
print(ports.api)          # 47000

# Environment variables override defaults
# NEO4J_BOLT_PORT, MILVUS_PORT, API_PORT, etc.
```
