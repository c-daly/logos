# LOGOS Testing Standards

This document defines the testing standards and best practices for all repositories in the Project LOGOS ecosystem.

## Core Philosophy

1.  **Consistency**: All repositories use the same tooling (Pytest, Poetry) and CI workflows.
2.  **Reliability**: Tests must be deterministic. Flaky tests should be fixed, not ignored.
3.  **Completeness**: Integration tests running in CI are mandatory for services with external dependencies (Milvus, Neo4j).

## Tooling Stack

All Python repositories must use the following standard stack:

-   **Test Runner**: `pytest`
-   **Dependency Management**: `poetry`
-   **Linting**: `ruff`
-   **Formatting**: `black`
-   **Type Checking**: `mypy`
-   **Coverage**: `pytest-cov` (uploading to Codecov)

## Test Categories

### 1. Unit Tests
-   **Scope**: Individual functions, classes, or modules.
-   **Dependencies**: Must be mocked (e.g., `unittest.mock`, `pytest-mock`).
-   **Speed**: Must be extremely fast (<100ms per test).
-   **Location**: `tests/` (default) or `tests/unit/`.

### 2. Integration Tests
-   **Scope**: Interaction between the application and external services (Databases, APIs).
-   **Dependencies**: Real instances running via Docker Compose. **Do not mock database drivers** in integration tests.
-   **Markers**: Must be marked with `@pytest.mark.integration`.
-   **CI Execution**: Must run in CI. Use the `integration-test` job pattern in GitHub Actions.
-   **Location**: `tests/integration/` or `tests/` with the integration marker.

### 3. End-to-End (E2E) Tests
-   **Scope**: Full user flows across multiple services.
-   **Location**: Typically in `apollo/tests/e2e` or `logos/tests/phase2`.

## CI/CD Requirements

### The "No Skip in CI" Rule
**Never** skip tests solely because they are running in CI (`@pytest.mark.skipif(os.environ.get("CI"))`).
-   If a test is slow, optimize it or move it to a specialized job.
-   If a test requires a database, spin it up using Docker Compose in the workflow.
-   **Rationale**: Skipping tests in CI hides regressions.

### Reusable Workflow
All repositories must use the shared workflow: `c-daly/logos/.github/workflows/reusable-standard-ci.yml`.

## Best Practices

### 1. Fixtures
Use `pytest` fixtures for setup and teardown. Avoid `unittest.TestCase` style classes unless necessary.

```python
@pytest.fixture
def milvus_collection():
    # Setup
    collection = create_collection()
    yield collection
    # Teardown
    collection.drop()
```

### 2. Async Testing
Use `pytest-asyncio` for async code. Mark async tests explicitly if not using the `auto` mode.

```python
@pytest.mark.asyncio
async def test_websocket_handler():
    ...
```

### 3. Docker Compose for Integration
For integration tests, define a `docker-compose.test.yml` that exposes necessary services (Milvus, Neo4j, MinIO) on localhost ports. The CI workflow should start these services before running tests.

### 4. Retry Logic
For tests involving asynchronous indexing (e.g., Milvus, Elasticsearch), use retry loops with timeouts rather than hardcoded `time.sleep()`.

```python
# Good
for _ in range(10):
    if check_condition():
        break
    time.sleep(0.5)

# Bad
time.sleep(5)  # Flaky and slow
```
