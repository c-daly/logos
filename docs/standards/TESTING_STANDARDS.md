# LOGOS Ecosystem Testing Standards

This document defines the canonical testing standards for the entire LOGOS ecosystem. All repositories must follow these conventions.

**Canonical Location:** `logos/docs/TESTING_STANDARDS.md`
**Last Updated:** December 2025

---

## Overview

Testing in the LOGOS ecosystem follows consistent patterns across all repositories. This document is the **source of truth**—individual repos may have additional detail but should not contradict these standards.

### Core Principles

1. **Consistency** – All repos use the same tooling (Pytest, Poetry) and CI workflows
2. **Reliability** – Tests must be deterministic; flaky tests are fixed, not ignored
3. **Completeness** – Integration tests with real infrastructure are mandatory in CI
4. **Isolation** – Tests are independent and runnable in any order

---

## Test Categories

### Unit Tests

**Scope:** Individual functions, classes, and modules in isolation.

| Aspect | Requirement |
|--------|-------------|
| Location | `tests/unit/` |
| Dependencies | Must be mocked (`unittest.mock`, `pytest-mock`) |
| Speed | < 100ms per test |
| Markers | None required |

```python
# Example unit test
def test_parse_config():
    config = parse_config({"host": "localhost"})
    assert config.host == "localhost"
```

### Integration Tests

**Scope:** Interaction between the application and real external services.

| Aspect | Requirement |
|--------|-------------|
| Location | `tests/integration/` |
| Dependencies | Real instances via Docker Compose—**never mock database drivers** |
| Markers | `@pytest.mark.integration` |
| Infrastructure | `docker-compose.test.yml` in each repo |

```python
@pytest.mark.integration
def test_neo4j_crud(neo4j_client):
    # Uses real Neo4j instance from Docker Compose
    neo4j_client.create_node({"name": "test"})
    result = neo4j_client.query("MATCH (n) RETURN n")
    assert len(result) > 0
```

### End-to-End Tests

**Scope:** Full user flows across multiple services.

| Aspect | Requirement |
|--------|-------------|
| Location | `tests/e2e/` |
| Dependencies | Full service stack via Docker Compose |
| Markers | `@pytest.mark.e2e` |
| Trigger | Explicit env var (e.g., `RUN_E2E=1`) |

```python
@pytest.mark.e2e
def test_complete_workflow():
    # Exercises multiple services end-to-end
    response = client.post("/ingest", json={"text": "hello"})
    assert response.status_code == 200
```

---

## Port Allocation

Each repository uses a unique port offset to prevent conflicts when running multiple test stacks simultaneously.

### Standard Offset (base + repo offset)

Each repo has a unique offset to prevent conflicts when running test stacks in parallel.
The single source of truth for these values is `logos_config.ports` in the logos-foundry package.

| Repo | Prefix | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Health | API |
|------|--------|------------|------------|-------------|---------------|-----|
| hermes | 17xxx | 17474 | 17687 | 17530 | 17091 | 17000 |
| apollo | 27xxx | 27474 | 27687 | 27530 | 27091 | 27000 |
| logos | 37xxx | 37474 | 37687 | 37530 | 37091 | 37000 |
| sophia | 47xxx | 47474 | 47687 | 47530 | 47091 | 47000 |
| talos | 57xxx | 57474 | 57687 | 57530 | 57091 | 57000 |

### Environment Variables

Each repo's test stack should set these automatically, but for manual runs:

```bash
# Logos example (offset +30000)
export NEO4J_URI=bolt://localhost:37687
export NEO4J_HTTP=http://localhost:37474
export MILVUS_HOST=localhost
export MILVUS_PORT=37530
```

---

## Tooling Stack

All Python repositories must use:

| Tool | Purpose | Command |
|------|---------|---------|
| `pytest` | Test runner | `poetry run pytest` |
| `poetry` | Dependency management | `poetry install` |
| `ruff` | Linting and formatting | `poetry run ruff check .` |
| `mypy` | Type checking | `poetry run mypy src/` |
| `pytest-cov` | Coverage | `poetry run pytest --cov` |

### Quick Commands

Each repo should provide a `run_tests.sh` script:

```bash
./scripts/run_tests.sh all          # Run all tests
./scripts/run_tests.sh unit         # Unit tests only
./scripts/run_tests.sh integration  # Integration tests
./scripts/run_tests.sh e2e          # End-to-end tests
./scripts/run_tests.sh up           # Start infrastructure
./scripts/run_tests.sh down         # Stop infrastructure
./scripts/run_tests.sh ci           # Full CI parity
```

---

## CI/CD Requirements

### The "No Skip in CI" Rule

**Never** skip tests solely because they are running in CI.

```python
# ❌ BAD – Don't do this
@pytest.mark.skipif(os.environ.get("CI"), reason="slow")
def test_something():
    ...

# ✅ GOOD – Use markers and run in specialized jobs
@pytest.mark.integration
def test_something():
    ...
```

If a test requires infrastructure, the CI workflow must spin it up via Docker Compose.

### Reusable Workflow

All repositories must use the shared workflow:

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    uses: c-daly/logos/.github/workflows/reusable-standard-ci.yml@main
    with:
      python-version: "3.11"
```

See `logos/docs/operations/ci/README.md` for workflow documentation.

---

## Best Practices

### Fixtures

Use `pytest` fixtures for setup and teardown:

```python
@pytest.fixture
def neo4j_client():
    client = Neo4jClient(uri="bolt://localhost:37687")
    yield client
    client.close()

@pytest.fixture
def clean_database(neo4j_client):
    yield
    neo4j_client.run("MATCH (n) WHERE n.name STARTS WITH 'test_' DELETE n")
```

### Async Testing

Use `pytest-asyncio` for async code:

```python
import pytest

@pytest.mark.asyncio
async def test_async_handler():
    result = await async_function()
    assert result is not None
```

### Retry Logic for Eventual Consistency

For services with async indexing (Milvus, Elasticsearch):

```python
# ✅ Good – Retry with backoff
for _ in range(10):
    if check_condition():
        break
    time.sleep(0.5)
else:
    pytest.fail("Condition not met after retries")

# ❌ Bad – Arbitrary sleep
time.sleep(5)  # Flaky and slow
```

### Test Isolation

- Tests must be independent and runnable in any order
- Use fixtures for setup/teardown, not test dependencies
- Clean up test data after each test
- Prefix test data with `test_` for easy identification and cleanup

### Test Naming

```python
# Pattern: test_{action}_{scenario}_{expected_result}
def test_create_node_with_valid_data_succeeds():
    ...

def test_create_node_with_missing_field_raises_validation_error():
    ...
```

---

## Running Tests

### Local Development

```bash
# Install dependencies
poetry install

# Run unit tests (fast feedback)
poetry run pytest tests/unit/

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test
poetry run pytest tests/unit/test_client.py::test_connection -v
```

### With Infrastructure

```bash
# Start test infrastructure
./scripts/run_tests.sh up

# Run integration tests
./scripts/run_tests.sh integration

# Stop and clean up
./scripts/run_tests.sh down
```

### Full CI Parity

```bash
# Run exactly what CI runs
./scripts/run_tests.sh ci
```

---

## Troubleshooting

### Port Conflicts

If services fail with "port already in use":

```bash
# Check what's using the port
lsof -i :37687

# Stop any existing containers
./scripts/run_tests.sh down
docker ps | grep test | awk '{print $1}' | xargs docker stop 2>/dev/null
```

### Neo4j Won't Start

```bash
# Check container logs
docker logs logos-test-neo4j

# Clear volumes and restart
./scripts/run_tests.sh clean
./scripts/run_tests.sh up
```

### Milvus Health Check Failing

Milvus can take 60-90 seconds to become healthy:

```bash
# Check dependencies first
docker logs logos-test-milvus-etcd
docker logs logos-test-milvus-minio

# Then check milvus
docker logs logos-test-milvus
```

### Tests Can't Connect to Services

Ensure environment variables match the port allocation:

```bash
# Source the test environment
source tests/e2e/stack/logos/.env.test

# Or set manually
export NEO4J_URI=bolt://localhost:37687
```

---

## Related Documentation

- [CI/CD Documentation](operations/ci/README.md)
- [Port Reference](operations/PORT_REFERENCE.md)
- [Phase 2 Verification](operations/PHASE2_VERIFY.md)

---

## Changelog

| Date | Change |
|------|--------|
| Dec 2025 | Consolidated from AGENTS.md and operations/TESTING.md |
| Nov 2025 | Added port standardization |
| Oct 2025 | Initial version |
