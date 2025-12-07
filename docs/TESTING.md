# Testing Guide

## Test Categories

| Category | Location | Markers | Infrastructure |
|----------|----------|---------|----------------|
| **Unit** | `tests/unit/` | None | None (all mocked) |
| **Integration** | `tests/integration/` | `@pytest.mark.integration` | Docker (Neo4j, Milvus) |
| **E2E** | `tests/e2e/` | `@pytest.mark.e2e` | Full service stack |

## Running Tests

### Unit Tests (fast, no dependencies)

```bash
poetry run pytest tests/unit/ -v
```

### Integration Tests

Each repo has a helper script that starts infrastructure and runs tests:

```bash
# Sophia
cd ~/projects/LOGOS/sophia
./scripts/run_integration_stack.sh

# Talos
cd ~/projects/LOGOS/talos
./scripts/run_integration_stack.sh

# Hermes
cd ~/projects/LOGOS/hermes
./scripts/run_e2e.sh
```

The scripts:
1. Check for port conflicts
2. Start Docker containers (Neo4j, Milvus)
3. Wait for health checks
4. Run pytest
5. Clean up containers

### Manual Infrastructure

If you prefer to manage infrastructure yourself:

```bash
# Start test stack for sophia (uses 47xxx ports)
cd ~/projects/LOGOS/sophia
docker compose -f docker-compose.test.yml up -d

# Run tests with infrastructure available
RUN_SOPHIA_INTEGRATION=1 poetry run pytest tests/integration/ -v

# Clean up
docker compose -f docker-compose.test.yml down -v
```

## Port Allocation

Each repo uses unique ports to allow parallel test runs:

| Repo | Prefix | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Health |
|------|--------|------------|------------|-------------|---------------|
| hermes | 17xxx | 17474 | 17687 | 17530 | 17091 |
| apollo | 27xxx | 27474 | 27687 | 27530 | 27091 |
| logos | 37xxx | 37474 | 37687 | 37530 | 37091 |
| sophia | 47xxx | 47474 | 47687 | 47530 | 47091 |
| talos | 57xxx | 57474 | 57687 | 57530 | 57091 |

The source of truth is `logos_config.ports` in the logos-foundry package.

## Test Stack Generation

Test `docker-compose.test.yml` files are generated from logos:

```bash
cd ~/projects/LOGOS/logos
poetry run render-test-stacks --repo sophia
# Generates logos/infra/sophia/docker-compose.test.yml
```

Copy to target repo or generate all at once:
```bash
poetry run render-test-stacks --all
```

## Environment Variables

Tests read configuration from environment:

| Variable | Purpose | Example |
|----------|---------|---------|
| `NEO4J_URI` | Neo4j connection | `bolt://localhost:47687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `neo4jtest` |
| `MILVUS_HOST` | Milvus host | `localhost` |
| `MILVUS_PORT` | Milvus gRPC port | `47530` |
| `RUN_*_INTEGRATION` | Enable integration tests | `1` |

## CI Behavior

- Unit tests run on every push
- Integration tests run on push to main and PRs
- E2E tests run on explicit trigger or release

Coverage is collected automatically. Target: 80%+ for unit, 60%+ overall.

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_parser.py
def test_parse_goal():
    result = parse_goal("pick up block")
    assert result.action == "pick"
    assert result.target == "block"
```

### Integration Test Example

```python
# tests/integration/test_neo4j.py
import pytest

@pytest.mark.integration
def test_create_node(neo4j_client):
    node = neo4j_client.create_node({"name": "test"})
    assert node["name"] == "test"
```

### Skipping When Infrastructure Missing

Tests skip automatically if services aren't available:

```python
@pytest.fixture
def neo4j_client():
    try:
        client = Neo4jClient(os.getenv("NEO4J_URI"))
        client.verify_connection()
        return client
    except Exception:
        pytest.skip("Neo4j not available")
```

## Troubleshooting

**Tests skip with "service not available"**
```bash
# Check if containers are running
docker ps | grep -E "neo4j|milvus"

# Check health
curl http://localhost:47474  # Neo4j
curl http://localhost:47091/healthz  # Milvus
```

**Port conflict**
```bash
# Find what's using the port
lsof -i :47474

# Kill it or use a different stack
docker compose down -v
```

**Flaky tests**
- Never ignore flaky tests - fix the root cause
- Use proper waits for async operations
- Ensure test isolation (each test cleans up after itself)
