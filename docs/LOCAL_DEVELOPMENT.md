# LOGOS Local Development Guide

This guide covers setting up a local development environment for LOGOS repositories.

**Last Updated:** January 2025

---

## Development Philosophy

### Git Dependencies for Local Dev, Containers for CI

- **Local development**: Use git dependencies between repos for fast iteration
- **CI/CD**: Containerized services with published packages for reproducibility

Each repository is designed to deploy independently. There is no filesystem coupling between repos.

---

## Quick Start

### 1. Clone All Repos

```bash
# Create workspace directory
mkdir logos-workspace && cd logos-workspace

# Clone all repos
git clone git@github.com:c-daly/logos.git
git clone git@github.com:c-daly/apollo.git
git clone git@github.com:c-daly/hermes.git
git clone git@github.com:c-daly/sophia.git
git clone git@github.com:c-daly/talos.git
```

### 2. Set Up Each Repository

Each repo has a setup script that configures local dependencies:

```bash
cd logos && ./scripts/setup-local-dev.sh
cd ../apollo && ./scripts/setup-local-dev.sh
cd ../hermes && ./scripts/setup-local-dev.sh
cd ../sophia && ./scripts/setup-local-dev.sh
cd ../talos && ./scripts/setup-local-dev.sh
```

The setup scripts:
- Install Poetry dependencies
- Configure path-based git dependencies for local development
- Generate `.env.test` with correct port allocations

---

## Port Allocation

Each repository has a unique port prefix to allow parallel test execution.

| Repo   | Prefix | Neo4j Bolt | Neo4j HTTP | Milvus gRPC | API Port |
|--------|--------|------------|------------|-------------|----------|
| hermes | 17     | 17687      | 17474      | 17530       | 17000    |
| apollo | 27     | 27687      | 27474      | 27530       | 27000    |
| logos  | 37     | 37687      | 37474      | 37530       | 37000    |
| sophia | 47     | 47687      | 47474      | 47530       | 47000    |
| talos  | 57     | 57687      | 57474      | 57530       | 57000    |

### Using Port Allocation Programmatically

```python
from logos_config.ports import get_repo_ports

# Get ports for your repo
ports = get_repo_ports("sophia")
print(f"Neo4j Bolt: {ports.neo4j_bolt}")  # 47687
print(f"API Port: {ports.api}")            # 47000
```

---

## Environment Variables

Environment variables override default port allocations:

| Variable | Description |
|----------|-------------|
| `NEO4J_BOLT_PORT` | Neo4j Bolt protocol port |
| `NEO4J_HTTP_PORT` | Neo4j HTTP port |
| `MILVUS_PORT` | Milvus gRPC port |
| `MILVUS_METRICS_PORT` | Milvus metrics port |
| `API_PORT` | Service API port |

### Common Connection Variables

```bash
# Neo4j
NEO4J_URI=bolt://localhost:47687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=47530

# Service URLs
SOPHIA_URL=http://localhost:47000
HERMES_URL=http://localhost:17000
APOLLO_URL=http://localhost:27000
```

---

## Shared Packages

### logos_config

Configuration utilities shared across all repos:

```python
from logos_config import get_repo_ports, Neo4jConfig, MilvusConfig
from logos_config.env import load_env_file
```

### logos_test_utils

Testing utilities and fixtures:

```python
from logos_test_utils import (
    load_stack_env,
    get_neo4j_config,
    get_milvus_config,
    wait_for_neo4j,
)

from logos_test_utils.fixtures import (
    stack_env,
    neo4j_config,
    neo4j_driver,
)
```

---

## Running Tests Locally

### Unit Tests (No Infrastructure)

```bash
cd <repo>
poetry run pytest tests/unit/
```

### Integration Tests (With Infrastructure)

```bash
cd <repo>

# Start test infrastructure
docker compose -f docker-compose.test.yml up -d

# Run tests
poetry run pytest tests/integration/

# Stop infrastructure
docker compose -f docker-compose.test.yml down -v
```

### Full Stack E2E Tests

```bash
cd logos

# Start full stack
./tests/e2e/run_e2e.sh up

# Run E2E tests
RUN_P2_E2E=1 poetry run pytest tests/e2e/test_phase2_end_to_end.py -v

# Stop stack
./tests/e2e/run_e2e.sh down
```

---

## Independent Deployment

Each repository deploys independently:

- No shared filesystem mounts between services
- Communication via HTTP APIs only
- Shared packages are published to PyPI for production

This means you can:
- Develop and test one repo without running others
- Deploy repos in any order
- Scale repos independently

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using a port
lsof -i :47687

# Stop all test containers
docker ps --filter "name=test" -q | xargs docker stop
```

### Neo4j Connection Refused

```bash
# Check if Neo4j is healthy
docker inspect <container-name> | grep -A 10 Health

# Wait for Neo4j to be ready
from logos_test_utils import wait_for_neo4j, get_neo4j_config
wait_for_neo4j(get_neo4j_config())
```

### Milvus Initialization Delay

Milvus can take 30-60 seconds to initialize. Use retry loops:

```python
from logos_test_utils import wait_for_milvus, get_milvus_config
wait_for_milvus(get_milvus_config())
```

---

## Related Documentation

- [Testing Documentation](operations/TESTING.md)
- [Port Reference](operations/PORT_REFERENCE.md)
- [CI/CD Documentation](operations/ci/README.md)
