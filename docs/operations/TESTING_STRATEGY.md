# LOGOS Testing Strategy

**Current Status:** This document reflects the actual testing setup as of November 2025.

## Overview

LOGOS uses a multi-layered testing approach with tests distributed across repositories. Each repository owns its unit and component tests, while logos acts as the orchestrator for end-to-end integration tests.

## Testing Layers

### 1. Unit Tests (Repository-Specific)

**Purpose:** Test individual functions, classes, and modules in isolation.

**Location:** Each repository maintains its own unit tests:
- `hermes/tests/` - Hermes unit tests
- `sophia/tests/` - Sophia unit tests  
- `apollo/tests/` - Apollo unit tests
- `talos/tests/` - Talos unit tests
- `logos/tests/` - Logos foundry tests (ontology, tools)

**When to run:** 
- Before every commit
- Automatically in each repo's CI pipeline
- Fast (< 1 minute per repo)

**Current status:**
- ✅ Hermes: Component tests with mock services
- ✅ Sophia: API tests, JEPA integration tests, CWM tests
- ✅ Apollo: CLI tests, client tests, backend API tests
- ✅ Talos: Executor tests, integration tests with Neo4j
- ✅ Logos: Phase 1 milestone tests, ontology validation

### 2. Component/Integration Tests (Repository-Specific)

**Purpose:** Test service components with minimal external dependencies (usually just Neo4j/Milvus).

**Location:** Same `tests/` directory as unit tests, often distinguished by markers or subdirectories.

**Infrastructure needs:**
- **Hermes:** Has `docker-compose.test.yml` (Milvus + Neo4j only, ports 7687, 7474, 19530, 9091)
- **Sophia:** Uses shared logos infrastructure via `infra/docker-compose.hcg.dev.yml`
- **Apollo:** Has `tests/e2e/docker-compose.e2e.yml` (Neo4j + mock services)
- **Talos:** Uses shared infrastructure or skips if Neo4j unavailable

**When to run:**
- Before PR submission
- In CI when infrastructure is available
- Medium speed (2-5 minutes)

**Current status:**
- ✅ Hermes: Milvus integration tests, Neo4j embedding tests
- ✅ Sophia: JEPA simulation, media ingestion (partial), CWM state persistence
- ✅ Apollo: HCG client integration, persona store tests
- ✅ Talos: Executor Neo4j integration tests

### 3. End-to-End Integration Tests (Logos Orchestrator)

**Purpose:** Validate all services working together in complete workflows.

**Location:** `logos/tests/phase2/test_phase2_end_to_end.py`

**Infrastructure:** `logos/tests/phase2/docker-compose.test.yml` 
- Provides: Neo4j 5.14.0, Milvus 2.3.3 (with etcd/MinIO)
- Services run via `logos/scripts/start_services.sh` (not in Docker)
- Ports: 7687, 7474 (Neo4j), 8001 (Sophia), 8002 (Hermes), 8003 (Apollo), 19530, 9091 (Milvus)
- Credentials: neo4j/logosdev, SOPHIA_API_KEY=test-token-12345

**Test coverage:**
- ✅ Service health checks (5/5 tests)
- ✅ CWMState contract validation (3/4 tests, 1 blocked by SDK bug)
- ✅ Cross-service chains (4/5 tests, 1 blocked by OTel)
- ✅ SDK client integration (4/4 tests)
- ✅ Persona diary functionality (7/7 tests for CRUD/reflections)
- ✅ JEPA simulation (4/4 stub tests)
- ✅ Complete workflow validation (5/5 available workflow steps)

**When to run:**
- On PRs affecting logos/, sophia/, hermes/, apollo/
- Manually: `SOPHIA_API_KEY=test-token-12345 RUN_P2_E2E=1 poetry run pytest tests/phase2/test_phase2_end_to_end.py -v`
- CI: `.github/workflows/phase2-e2e.yml`
- Runtime: ~5-10 minutes including infrastructure startup

**Current status (Nov 24, 2025):**
- ✅ 32/33 tests passing (97%)
- ⏭️ 11 tests skipped with tracking issues:
  - 2 by sophia#32, apollo#91 (SDK/API format mismatch)
  - 3 by logos#240 (media ingestion)
  - 3 by logos#321 (OpenTelemetry) 
  - 3 by logos#315 (Playwright browser tests)
- ❌ 0 tests failing
- 📋 Cross-repo blockers documented in GitHub issues

### 4. Phase 1 Milestone Tests (Logos)

**Purpose:** Validate Phase 1 specification compliance.

**Location:** `logos/tests/phase1/`
- `test_m1_neo4j_crud.py` - M1: Neo4j CRUD operations
- `test_m2_shacl_validation.py` - M2: SHACL validation
- `test_m3_planning.py` - M3: Planning functionality
- `test_m4_end_to_end.py` - M4: Complete pick-and-place workflow

**When to run:**
- Phase 1 verification
- Regression testing
- Example: `RUN_M4_E2E=1 pytest tests/phase1/test_m4_end_to_end.py`

**Current status:**
- ✅ Phase 1 complete and validated
- Maintained for regression testing

## Test Execution

### Running Tests Locally

**Individual repo unit/component tests:**
```bash
# Hermes
cd hermes
poetry run pytest

# Sophia
cd sophia
poetry run pytest

# Apollo
cd apollo
poetry run pytest

# Talos
cd talos
poetry run pytest
```

**Hermes with infrastructure:**
```bash
cd hermes
docker compose -f docker-compose.test.yml up -d
poetry run pytest tests/test_milvus_integration.py
docker compose -f docker-compose.test.yml down -v
```

**Phase 2 E2E from logos:**
```bash
cd logos/tests/phase2
docker compose -f docker-compose.test.yml up -d
cd ../..
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py -v
cd tests/phase2
docker compose -f docker-compose.test.yml down -v
```

### CI/CD Execution

**Repository-level CI:**
Each repo has `.github/workflows/ci.yml` that:
- Runs unit tests on every push
- Runs component tests if infrastructure available
- Fast feedback (< 5 minutes)

**Logos orchestrator CI:**
- `.github/workflows/phase2-e2e.yml` - Full Phase 2 integration tests
- Triggers on PRs affecting logos/, sophia/, hermes/, apollo/
- Starts isolated docker-compose environment
- Runs comprehensive integration suite

## Current Infrastructure

### Shared Development Infrastructure

**Location:** `logos/infra/docker-compose.hcg.dev.yml`

**Services:**
- Neo4j 5.14.0 (ports 7687, 7474)
- Milvus 2.3.3 (ports 19530, 9091) 
- SHACL validation service (port 8081)

**Usage:** Default for development, used by Sophia and Talos tests

### Test-Specific Infrastructure

**Hermes tests:**
- File: `hermes/docker-compose.test.yml`
- Ports: 7687, 7474, 19530, 9091 (same as dev - **potential conflict**)
- Services: Milvus (full stack with etcd/MinIO), Neo4j
- Credentials: `neo4j/password`

**Apollo E2E:**
- File: `apollo/tests/e2e/docker-compose.e2e.yml`
- Ports: 7687, 7474 (same as dev - **potential conflict**)
- Services: Neo4j only
- Credentials: `neo4j/logosdev`

**Logos Phase 2 E2E:**
- File: `logos/tests/phase2/docker-compose.test.yml`
- Ports: 7687, 7474, 8001, 8002, 8003, 19530, 9091 (same as dev)
- Services: Full stack (Neo4j, Milvus, Sophia, Hermes, Apollo)
- Credentials: `neo4j/logosdev`
- **Note:** As orchestrator, this legitimately uses default ports

## Known Issues and Limitations

### Port Conflicts
⚠️ Multiple test environments use the same ports (7687, 7474, 19530, 9091). Running tests from different repos simultaneously will fail. 

**Workaround:** Run test suites sequentially or shut down conflicting services.

**Future:** See issue #326 for port standardization plan.

### Credential Inconsistencies
⚠️ Hermes uses `neo4j/password` while others use `neo4j/logosdev`.

**Workaround:** Be aware when copying test code between repos.

**Future:** Will be standardized to `neo4j/logosdev` (issue #326).

### Fixture Duplication
⚠️ Each repo duplicates similar fixtures (Neo4j connections, Milvus connections, service clients).

**Workaround:** Current state is functional but creates maintenance burden.

**Future:** Shared `logos_test_utils` package planned (issue #326).

## Test Development Guidelines

### When Adding New Tests

**For unit tests (new feature in a repo):**
1. Add test to the appropriate repo's `tests/` directory
2. Use existing fixtures from repo's `conftest.py`
3. Ensure tests pass locally with `poetry run pytest`
4. Tests run automatically in that repo's CI

**For component tests (feature needs infrastructure):**
1. Add test to repo's `tests/` directory
2. Mark with `@pytest.mark.integration` or similar
3. Use repo's test docker-compose if available
4. Document infrastructure requirements in test docstring

**For cross-service integration (feature spans multiple services):**
1. Add test to `logos/tests/phase2/test_phase2_end_to_end.py`
2. Add to appropriate test class (TestP2M1, TestP2M2, etc.)
3. Use fixtures from `logos/tests/phase2/fixtures.py`
4. If blocked by dependencies, mark with:
   ```python
   @pytest.mark.skip(reason="Blocked by logos#XXX - description")
   ```
5. Tests run in Phase 2 E2E CI workflow

### Test Isolation

**Best practices:**
- Tests should be independent and runnable in any order
- Use fixtures for setup/teardown, not test dependencies
- Clean up test data (use `clean_neo4j`, `clean_milvus` fixtures)
- Prefix test data with `test_` or `Test` for easy cleanup

### Environment Variables

**Standard test environment variables:**
```bash
# Enable Phase 2 E2E tests
RUN_P2_E2E=1

# Enable Phase 1 E2E tests  
RUN_M4_E2E=1

# Service URLs (default ports shown)
SOPHIA_URL=http://localhost:8001
HERMES_URL=http://localhost:8002
APOLLO_URL=http://localhost:8003

# Database connections
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=logosdev  # or 'password' for hermes

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Future Improvements

These improvements are planned but not yet implemented:

1. **Port standardization** (Issue #326)
   - Unique port ranges for each test environment
   - Enables simultaneous test execution

2. **Shared test utilities** (Issue #326)
   - `logos_test_utils` package
   - Common fixtures and helpers
   - Reduces duplication

3. **Browser E2E tests** (Issue #315)
   - Playwright infrastructure for Apollo webapp
   - GraphViewer interaction tests
   - ChatPanel E2E tests

4. **OpenTelemetry testing** (Issue #321)
   - Trace propagation validation
   - Telemetry export verification

5. **Media ingestion testing** (Issue #240)
   - Image/video upload tests
   - JEPA embedding generation
   - Media-conditioned simulation

## References

- [Phase 2 E2E Testing Documentation](../../tests/phase2/README.md)
- [Hermes Testing Guide](../../../hermes/TESTING.md)
- [Contributing Guide - Testing Requirements](../../CONTRIBUTING.md#testing-guidelines)
- [Issue #324](https://github.com/c-daly/logos/issues/324) - Phase 2 E2E Testing
- [Issue #326](https://github.com/c-daly/logos/issues/326) - Port Standardization & Shared Fixtures
