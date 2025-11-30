# Test Standardization Migration Guide

**Status**: In Progress (feature/logos-test-utils branch)  
**Related Issues**: #326, #358, #363-367  
**Target Date**: December 2025

## Overview

This migration standardizes test infrastructure across all LOGOS repos to eliminate port conflicts, credential inconsistencies, and fixture duplication.

## What Changed

### 1. Port Assignments (No More Conflicts!)

| Repo   | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Metrics |
|--------|-----------|-----------|-------------|----------------|
| logos  | 7474      | 7687      | 19530       | 9091          |
| apollo | 27474     | 27687     | 29530       | 29091         |
| hermes | N/A       | N/A       | 19530       | 19091         |
| sophia | 37474     | 37687     | 39530       | 39091         |
| talos  | 47474     | 47687     | N/A         | N/A           |

**Result**: All repos can run tests simultaneously without port conflicts.

### 2. Credential Standardization

**Before**: `neo4j/password`, `neo4j/testpassword`, `neo4j/sophia_dev`  
**After**: `neo4j/neo4jtest` (everywhere)

### 3. Shared Test Utilities

**Package**: `logos_test_utils` (exported from logos repo)

**Contents**:
- `docker.py` - Container health checks, name resolution
- `env.py` - Load `.env.test` with consistent schema
- `milvus.py` - Milvus connection helpers, config
- `neo4j.py` - Neo4j driver setup, query runners
- `fixtures.py` - Pytest fixtures for common scenarios

**Installation** (from other repos):
```toml
# In apollo/sophia/hermes/talos pyproject.toml
[tool.poetry.group.dev.dependencies]
logos-test-utils = { path = "../logos", develop = true }
```

## Migration Steps by Repo

### For Apollo (#363)

1. **Regenerate stack files**:
   ```bash
   cd logos
   poetry run render-test-stacks --repo apollo
   cp tests/e2e/stack/apollo/* ../apollo/tests/e2e/
   ```

2. **Update pyproject.toml**:
   ```toml
   [tool.poetry.group.dev.dependencies]
   logos-test-utils = { path = "../logos", develop = true }
   ```

3. **Replace fixtures in conftest.py**:
   ```python
   # OLD
   @pytest.fixture
   def neo4j_driver():
       driver = GraphDatabase.driver("bolt://localhost:7687", ...)
   
   # NEW
   from logos_test_utils import get_neo4j_driver, get_neo4j_config
   
   @pytest.fixture
   def neo4j_driver():
       config = get_neo4j_config()  # Reads from .env.test
       return get_neo4j_driver(config)
   ```

4. **Update test runner**:
   ```bash
   # tests/e2e/run_e2e.sh
   source tests/e2e/.env.test
   docker compose -f tests/e2e/docker-compose.test.apollo.yml up -d
   ```

5. **Verify**:
   ```bash
   poetry install
   ./tests/e2e/run_e2e.sh
   poetry run pytest tests/e2e/
   ```

### For Hermes (#364)

1. **Regenerate stack files**:
   ```bash
   cd logos
   poetry run render-test-stacks --repo hermes
   cp tests/e2e/stack/hermes/* ../hermes/tests/integration/
   ```

2. **Replace `scripts/run_integration_stack.sh`**:
   ```bash
   #!/bin/bash
   set -e
   
   # Source generated env
   if [ -f tests/integration/.env.test ]; then
       export $(grep -v '^#' tests/integration/.env.test | xargs)
   fi
   
   # Start stack
   docker compose -f tests/integration/docker-compose.test.hermes.yml up -d
   
   # Wait for health
   poetry run python -c "from logos_test_utils import wait_for_milvus; wait_for_milvus()"
   ```

3. **Update credentials**:
   - Remove references to `neo4j/password`
   - Use `neo4j/neo4jtest` everywhere

4. **Add shared fixtures**:
   ```toml
   [tool.poetry.group.dev.dependencies]
   logos-test-utils = { path = "../logos", develop = true }
   ```

### For Sophia (#365)

1. **Regenerate stack files**:
   ```bash
   cd logos
   poetry run render-test-stacks --repo sophia
   cp tests/e2e/stack/sophia/* ../sophia/tests/integration/
   ```

2. **Replace `run_prototype_integration.sh`**:
   ```bash
   # OLD: scripts/run_prototype_integration.sh with hardcoded ports
   # NEW: Use generated .env.test with unique ports (37xxx)
   ```

3. **Update credentials**:
   - Change `neo4j/sophia_dev` → `neo4j/neo4jtest`
   - Update tests expecting old password

4. **Adopt shared fixtures**:
   ```python
   # tests/conftest.py
   from logos_test_utils import get_neo4j_config, wait_for_neo4j
   ```

### For Talos (#366)

1. **Regenerate stack files**:
   ```bash
   cd logos
   poetry run render-test-stacks --repo talos
   cp tests/e2e/stack/talos/* ../talos/tests/integration/
   ```

2. **Update unique ports** (47xxx range)

3. **Add shared fixtures**:
   ```toml
   [tool.poetry.group.dev.dependencies]
   logos-test-utils = { path = "../logos", develop = true }
   ```

## Verification Checklist

### Per Repo

- [ ] Generated stack files exist in `tests/e2e/` or `tests/integration/`
- [ ] `.env.test` has unique ports matching `repos.yaml`
- [ ] `pyproject.toml` includes `logos-test-utils` dependency
- [ ] Tests import from `logos_test_utils` instead of local duplicates
- [ ] Helper scripts source `.env.test`
- [ ] All credentials use `neo4j/neo4jtest`
- [ ] CI passes with new configuration

### Cross-Repo

- [ ] Run tests in 2+ repos simultaneously → no port conflicts
- [ ] Environment variables follow consistent schema
- [ ] Documentation updated with new ports

## Common Patterns

### Loading Environment

```python
from logos_test_utils import load_stack_env

# In conftest.py or test setup
load_stack_env()  # Finds and loads .env.test
```

### Waiting for Services

```python
from logos_test_utils import wait_for_neo4j, wait_for_milvus

@pytest.fixture(scope="session")
def services_ready():
    wait_for_neo4j(timeout=30)
    wait_for_milvus(timeout=30)
```

### Getting Configuration

```python
from logos_test_utils import get_neo4j_config, get_milvus_config

neo4j_cfg = get_neo4j_config()  # Reads NEO4J_URI, NEO4J_USER, etc.
milvus_cfg = get_milvus_config()  # Reads MILVUS_HOST, MILVUS_PORT
```

## Troubleshooting

### "Port already in use"
- Check if another test suite is running
- Verify ports in `.env.test` match `repos.yaml`
- Use `docker ps` to find conflicting containers

### "Connection refused" 
- Ensure services are healthy: `docker compose ps`
- Check container names match service_prefix in `repos.yaml`
- Verify firewall isn't blocking localhost ports

### "Authentication failed"
- Confirm using `neo4j/neo4jtest` everywhere
- Check `.env.test` has correct NEO4J_PASSWORD
- Regenerate stack files if old credentials cached

## Benefits

1. **Parallel Testing**: Run all repo tests simultaneously
2. **Consistent Behavior**: Same Neo4j/Milvus versions across repos
3. **Reduced Duplication**: Shared fixtures = single source of truth
4. **Easier Onboarding**: One pattern to learn
5. **Faster Debugging**: Standard env vars and helpers

## Timeline

- **Week 1**: Logos repo complete (feature/logos-test-utils branch)
- **Week 2**: Apollo + Hermes migration
- **Week 3**: Sophia + Talos migration
- **Week 4**: Documentation + CI validation

## Questions?

See issues #326, #358, #363-367 or the parent tracking issue.
