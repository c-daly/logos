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

> **Tip:** `tests/e2e/run_e2e.sh` wraps the same stack definition, sources the
> generated `.env.test`, and exports the container identifiers required by the
> integration tests. Prefer the helper when you need the Phase 1 milestone
> suites and Phase 2 flows to share a single stack.

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

`tests/e2e/stack/logos/.env.test` is the canonical schema for the shared test
stack. The file is generated via `poetry run render-test-stacks --repo logos`
and is automatically sourced by `tests/e2e/run_e2e.sh`. Copy or export the
variables below when running tests directly via `pytest`.

### Test Toggles

```bash
RUN_P2_E2E=1      # Enable Phase 2 end-to-end suite
RUN_M4_E2E=1      # Enable Phase 1 Milestone 4 suite
```

### Service URLs

```bash
SOPHIA_URL=http://localhost:8001
HERMES_URL=http://localhost:8002
APOLLO_URL=http://localhost:8003
```

### Neo4j Configuration

```bash
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=logosdev
NEO4J_CONTAINER=logos-phase2-test-neo4j   # Optional override when reusing an existing stack
```

### Milvus Configuration

```bash
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_HEALTHCHECK=http://milvus:9091/healthz
MILVUS_CONTAINER=logos-phase2-test-milvus
```

> Integration tests auto-detect the running container names via
> `tests/utils/container_utils.py`, but defining `NEO4J_CONTAINER` and
> `MILVUS_CONTAINER` keeps the behaviour deterministic across CI jobs and local
> developer stacks.

---

## Known Issues

### Port Conflicts

⚠️ Multiple test environments use the same ports (7687, 7474, 19530, 9091). Running tests from different repos simultaneously will fail.

**Workaround:** Run test suites sequentially.

### Credential Inconsistencies

⚠️ Hermes uses `neo4j/password` while others use `neo4j/logosdev`.

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
