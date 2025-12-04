# Create Shared Test Utilities Package (logos_test_utils)

## Summary
Create a shared `logos_test_utils` package with common test fixtures, helpers, and utilities to reduce code duplication across service repositories and simplify test maintenance.

## Problem

**Current State:**
Each service repository duplicates similar test infrastructure:

**Hermes** (`hermes/tests/conftest.py`):
```python
@pytest.fixture
def milvus_connection():
    from pymilvus import connections
    connections.connect(alias="test", host="localhost", port="19530")
    yield connections
    connections.disconnect("test")

@pytest.fixture
def neo4j_driver():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    yield driver
    driver.close()
```

**Logos Phase 2** (`logos/tests/e2e/fixtures.py`):
```python
@pytest.fixture
def sophia_client():
    config = SophiaConfig(host=host, port=port)
    return SophiaClient(config)

@pytest.fixture
def clean_neo4j():
    # Cleanup logic...
```

**Apollo** (`apollo/tests/conftest.py`):
```python
@pytest.fixture
def mock_hcg_client():
    # Mock setup...
```

**Problems:**
- 🔁 Same fixtures copied across 4+ repositories
- 🐛 Bug fixes must be applied to each copy
- 📊 Inconsistent test data across repos
- 🔧 Maintenance burden when infrastructure changes
- 📚 No single source of truth for test utilities

## Proposed Solution

Create a new package `logos_test_utils` in the logos repository that provides:

1. **Common Fixtures** - Reusable pytest fixtures
2. **Service Clients** - Test client wrappers
3. **Mock Factories** - Consistent mock data generators
4. **Health Checks** - Service availability helpers
5. **Cleanup Utilities** - Database cleanup functions

### Package Structure

```
logos/
├── logos_test_utils/
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── database.py      # Neo4j, Milvus fixtures
│   │   ├── services.py      # Service client fixtures
│   │   └── cleanup.py       # Cleanup fixtures
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── sophia.py        # SophiaClient wrapper
│   │   ├── hermes.py        # HermesClient wrapper
│   │   └── persona.py       # PersonaClient wrapper
│   ├── mocks/
│   │   ├── __init__.py
│   │   ├── hcg_data.py      # Mock HCG entities
│   │   ├── embeddings.py    # Mock embedding data
│   │   └── cwmstate.py      # Mock CWMState data
│   ├── health/
│   │   ├── __init__.py
│   │   └── checks.py        # Service health utilities
│   └── config.py            # Test configuration
├── pyproject.toml           # Add logos_test_utils package
└── tests/
```

### Example Usage

**In Service Repositories:**

```python
# hermes/tests/test_milvus.py
from logos_test_utils.fixtures.database import milvus_connection, clean_milvus
from logos_test_utils.mocks.embeddings import sample_embedding

def test_embedding_storage(milvus_connection, clean_milvus, sample_embedding):
    # Test implementation using shared fixtures
    pass
```

```python
# sophia/tests/test_planning.py
from logos_test_utils.fixtures.services import sophia_client
from logos_test_utils.mocks.hcg_data import sample_goal_state

def test_plan_creation(sophia_client, sample_goal_state):
    # Test implementation
    pass
```

```python
# apollo/tests/test_cli.py
from logos_test_utils.clients import SophiaTestClient, HermesTestClient
from logos_test_utils.health import wait_for_services

def test_cli_command(wait_for_services):
    sophia = SophiaTestClient()
    # Test implementation
    pass
```

### Key Features

**1. Database Fixtures** (`fixtures/database.py`)
```python
@pytest.fixture
def neo4j_driver():
    """Provide Neo4j driver with configurable URI."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    auth = (os.getenv("NEO4J_USER", "neo4j"), 
            os.getenv("NEO4J_PASSWORD", "neo4jtest"))
    driver = GraphDatabase.driver(uri, auth=auth)
    yield driver
    driver.close()

@pytest.fixture
def milvus_connection():
    """Provide Milvus connection with configurable host/port."""
    host = os.getenv("MILVUS_HOST", "localhost")
    port = int(os.getenv("MILVUS_PORT", "19530"))
    connections.connect(alias="test", host=host, port=port)
    yield connections
    connections.disconnect("test")

@pytest.fixture
def clean_neo4j(neo4j_driver):
    """Clean test data from Neo4j before and after tests."""
    # Cleanup implementation
```

**2. Service Client Fixtures** (`fixtures/services.py`)
```python
@pytest.fixture
def sophia_client():
    """Provide configured SophiaClient for tests."""
    from apollo.client.sophia_client import SophiaClient
    from apollo.config.settings import SophiaConfig
    
    url = os.getenv("SOPHIA_URL", "http://localhost:8001")
    config = SophiaConfig.from_url(url)
    return SophiaClient(config)

@pytest.fixture
def services_running():
    """Check that all required services are healthy."""
    # Health check implementation
```

**3. Mock Data Factories** (`mocks/hcg_data.py`)
```python
def sample_entity(entity_type="goal", **kwargs):
    """Create sample Entity for testing."""
    return Entity(
        id=kwargs.get("id", "test-entity-001"),
        type=entity_type,
        properties=kwargs.get("properties", {}),
        labels=kwargs.get("labels", [entity_type.capitalize()]),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

def sample_cwmstate(**kwargs):
    """Create sample CWMState envelope for testing."""
    return {
        "state_id": kwargs.get("state_id", "test-state-001"),
        "model_type": kwargs.get("model_type", "plan"),
        "source": kwargs.get("source", "test"),
        "timestamp": kwargs.get("timestamp", datetime.now().isoformat()),
        "confidence": kwargs.get("confidence", 0.95),
        "status": kwargs.get("status", "active"),
        "links": kwargs.get("links", []),
        "tags": kwargs.get("tags", ["test"]),
        "data": kwargs.get("data", {}),
    }
```

**4. Health Check Utilities** (`health/checks.py`)
```python
def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wait for service to become available."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False

def wait_for_neo4j(uri: str, auth: tuple, timeout: int = 30) -> bool:
    """Wait for Neo4j to become available."""
    # Implementation
```

## Implementation Plan

### Phase 1: Package Setup (Required)
- [ ] Create `logos_test_utils/` package structure
- [ ] Add package to `logos/pyproject.toml`
- [ ] Create basic fixtures for Neo4j and Milvus
- [ ] Add mock data factories for common entities
- [ ] Write package documentation

### Phase 2: Hermes Integration (Proof of Concept)
- [ ] Add `logos-foundry[test]` to Hermes dev dependencies
- [ ] Replace Hermes fixtures with `logos_test_utils`
- [ ] Update Hermes tests to use shared fixtures
- [ ] Verify tests pass with shared utilities

### Phase 3: Sophia Integration
- [ ] Add `logos-foundry[test]` to Sophia dev dependencies
- [ ] Replace Sophia fixtures with `logos_test_utils`
- [ ] Update Sophia tests

### Phase 4: Apollo Integration
- [ ] Add `logos-foundry[test]` to Apollo dev dependencies
- [ ] Replace Apollo fixtures with `logos_test_utils`
- [ ] Update Apollo tests

### Phase 5: Logos Phase 2 Tests
- [ ] Update Phase 2 E2E tests to use `logos_test_utils`
- [ ] Remove duplicated fixtures from `tests/e2e/fixtures.py`

### Phase 6: Documentation & Best Practices
- [ ] Create `logos_test_utils/README.md`
- [ ] Add examples to TESTING_STRATEGY.md
- [ ] Document in CONTRIBUTING.md
- [ ] Add to Development Setup guide

## Package Distribution

**Option 1: Install from Local Path** (Development)
```toml
# In service's pyproject.toml
[tool.poetry.dependencies]
logos-foundry = {path = "../logos", develop = true, extras = ["test"]}
```

**Option 2: Install from Git** (CI/Production)
```toml
[tool.poetry.dependencies]
logos-foundry = {git = "https://github.com/c-daly/logos.git", branch = "main", extras = ["test"]}
```

**Option 3: Publish to PyPI** (Future)
```toml
[tool.poetry.dependencies]
logos-foundry = {version = "^0.1.0", extras = ["test"]}
```

## Dependencies

Add test utilities as optional dependency group in `logos/pyproject.toml`:

```toml
[tool.poetry.extras]
test = [
    "pytest",
    "pytest-cov",
    "neo4j",
    "pymilvus",
    "httpx",
    "requests",
]

[tool.poetry.dependencies]
# Core dependencies already defined
```

## Benefits

1. **🔄 DRY Principle** - Single source of truth for test utilities
2. **🛠️ Easy Maintenance** - Fix bugs once, benefit everywhere
3. **📊 Consistency** - Standardized test data across all repos
4. **⚡ Faster Development** - Reuse tested fixtures instead of writing new ones
5. **📚 Better Documentation** - Centralized test utilities documentation
6. **🧪 Quality** - Well-tested utilities improve all service tests

## Risks & Mitigations

**Risk:** Adding dependency between repos
**Mitigation:** 
- Optional dependency (extras group)
- Services can still run tests without it
- Version pin in each service's lock file

**Risk:** Breaking changes affect all repos
**Mitigation:**
- Semantic versioning
- Comprehensive tests for utilities themselves
- Clear changelog

**Risk:** Coupling test infrastructure
**Mitigation:**
- Keep utilities generic and flexible
- Allow overrides via environment variables
- Document how to opt-out if needed

## Acceptance Criteria

- [ ] `logos_test_utils` package created with all core fixtures
- [ ] Package installable via Poetry in service repos
- [ ] Documentation written (README, examples)
- [ ] At least one service (Hermes) successfully migrated
- [ ] Tests pass in service repos using shared utilities
- [ ] CI workflows updated and passing
- [ ] TESTING_STRATEGY.md updated with usage examples

## Related Issues

- Phase 2 E2E Testing: #324
- Testing Gap Analysis: #322
- Port Assignment Standardization: #XXX (related issue)

## Effort Estimate

- Phase 1 (Package Setup): 4-6 hours
- Phase 2 (Hermes POC): 3-4 hours
- Phase 3 (Sophia): 2-3 hours
- Phase 4 (Apollo): 2-3 hours
- Phase 5 (Logos Phase 2): 1-2 hours
- Phase 6 (Documentation): 2-3 hours
- **Total: 14-21 hours** (2-3 days)

## Priority

**Medium-High** - High value for developer experience and maintainability, moderate implementation effort

## Future Enhancements

- [ ] Mock service responses for offline testing
- [ ] Performance benchmarking utilities
- [ ] Test data builders with fluent API
- [ ] Snapshot testing utilities for HCG states
- [ ] Docker Compose helpers for test environments
