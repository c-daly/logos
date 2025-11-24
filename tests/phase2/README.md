# Phase 2 End-to-End Integration Tests

End-to-end integration tests validating Phase 2 services working together. Based on Phase 1's `test_m4_end_to_end.py` pattern.

**Related:** [Phase 2 Spec](../../apollo/docs/phase2/PHASE2_SPEC.md) · [GitHub Issue #324](https://github.com/c-daly/logos/issues/324) · [Testing Gap Analysis #322](https://github.com/c-daly/logos/issues/322)

## Quick Start

### Prerequisites

1. **Apollo SDK** must be installed in logos virtualenv:
   ```bash
   cd logos
   poetry run pip install -e ../apollo
   ```

2. **Services** must be cloned to sibling directories:
   ```
   LOGOS/
   ├── logos/
   ├── sophia/
   ├── hermes/
   └── apollo/
   ```

### Infrastructure Options

**Option A: Test-specific infrastructure** (isolated, used in CI):
```bash
cd logos/tests/phase2
docker compose -f docker-compose.test.yml up -d
```

**Option B: Shared infrastructure** (for local dev, cross-repo testing):
```bash
cd logos/infra
docker compose -f docker-compose.hcg.dev.yml up -d
```

Both provide: Neo4j (bolt://localhost:7687, user: neo4j, password: logosdev), Milvus (localhost:19530)

⚠️ **Don't run both!** They use the same ports.

### Running Tests (Validated Setup)

```bash
# 1. Start infrastructure (choose Option A or B above)
cd logos/tests/phase2
docker compose -f docker-compose.test.yml up -d

# 2. Wait for infrastructure (optional but recommended)
# Neo4j: docker exec logos-phase2-neo4j-test cypher-shell -u neo4j -p logosdev "RETURN 1"
# Milvus: curl http://localhost:9091/healthz

# 3. Start services with proper environment variables
cd logos/scripts
NEO4J_URI=bolt://localhost:7687 \
NEO4J_USER=neo4j \
NEO4J_PASSWORD=logosdev \
MILVUS_HOST=localhost \
MILVUS_PORT=19530 \
SOPHIA_API_KEY=test-token-12345 \
HERMES_PORT=8002 \
APOLLO_PORT=8003 \
./start_services.sh start

# 4. Run all Phase 2 E2E tests
cd logos
SOPHIA_API_KEY=test-token-12345 RUN_P2_E2E=1 poetry run pytest tests/phase2/test_phase2_end_to_end.py -v

# 5. Run specific test class
SOPHIA_API_KEY=test-token-12345 RUN_P2_E2E=1 poetry run pytest tests/phase2/test_phase2_end_to_end.py::TestP2M1ServicesOnline -v

# 6. Clean up
cd logos/scripts
./start_services.sh stop
cd ../tests/phase2
docker compose -f docker-compose.test.yml down -v
```

**Expected Results (as of Nov 24, 2025):**
- ✅ 32 tests PASSED
- ⏭️ 11 tests SKIPPED (with tracking issues)
- ❌ 0 tests FAILED

## Test Coverage

### Current Status (Nov 24, 2025)

**Overall: 32/33 tests passing (97%), 11 tests skipped**

### TestP2M1ServicesOnline
**Status:** ✅ 5/5 passing  
Validates service health and connectivity:
- Sophia health (Neo4j + Milvus dependencies)
- Hermes health check
- Neo4j bolt connectivity
- Milvus collection listing
- Apollo HCG health endpoint

### TestP2CWMStateEnvelope  
**Status:** ✅ 3/4 passing, ⏭️ 1 skipped  
Tests CWMState contract across `/plan`, `/state`, `/simulate` endpoints:
- ✅ Plan endpoint returns CWMState envelope
- ✅ State endpoint returns CWMState envelope  
- ⏭️ `test_simulate_endpoint_returns_cwmstate` - blocked by [sophia#32](https://github.com/c-daly/sophia/issues/32), [apollo#91](https://github.com/c-daly/apollo/issues/91) (SDK/API format mismatch)
- ⏭️ Media upload/processing test - blocked by [logos#240](https://github.com/c-daly/logos/issues/240) (media ingestion not implemented)

### TestP2M3PerceptionImagination
**Status:** ✅ 4/7 passing, ⏭️ 3 skipped  
Tests JEPA simulation, imagined states, confidence decay:
- ✅ Mock JEPA simulation returns imagined state
- ✅ Confidence decay over time steps
- ✅ Perception from real observations
- ✅ Imagination from counterfactual prompts
- ⏭️ 3 media tests - blocked by [logos#240](https://github.com/c-daly/logos/issues/240)

### TestP2M2ApolloDualSurface
**Status:** ✅ 4/7 passing, ⏭️ 3 skipped  
Tests Apollo CLI SDK integration and backend API:
- ✅ Apollo CLI available and versioned
- ✅ SophiaClient instantiation
- ✅ HermesClient instantiation
- ✅ PersonaClient instantiation
- ⏭️ 3 browser E2E tests - blocked by [logos#315](https://github.com/c-daly/logos/issues/315) (Playwright not configured)

### TestP2M4DiagnosticsPersona
**Status:** ✅ 7/10 passing, ⏭️ 3 skipped  
Tests persona diary CRUD, reflections, EmotionState:
- ✅ Create persona entry
- ✅ List persona entries
- ✅ Retrieve persona entry
- ✅ Persona reflection generation
- ✅ EmotionState in persona context
- ✅ Multi-entry persona context
- ✅ Persona context influences planning
- ⏭️ 3 OpenTelemetry tests - blocked by [logos#321](https://github.com/c-daly/logos/issues/321)

### TestP2CrossServiceIntegration
**Status:** ✅ 4/5 passing, ⏭️ 1 skipped  
Tests Apollo→Sophia→Hermes chains, SDK clients, error propagation:
- ✅ Apollo calls Sophia /plan successfully
- ✅ Sophia stores state in Neo4j
- ✅ Hermes retrieves state from Neo4j
- ✅ Service chain: Apollo→Sophia→Hermes
- ⏭️ Trace propagation test - blocked by [logos#321](https://github.com/c-daly/logos/issues/321)

### TestP2CompleteWorkflow
**Status:** ✅ 5/7 passing, ⏭️ 2 skipped  
Tests end-to-end Phase 2 workflow with available components:
- ✅ Complete planning workflow (goal→plan→state)
- ✅ Persona context in planning
- ✅ Multi-step planning with state evolution
- ✅ Error handling across services
- ✅ State persistence and retrieval
- ⏭️ Media ingestion workflow - blocked by [logos#240](https://github.com/c-daly/logos/issues/240)  
- ⏭️ Complete telemetry workflow - blocked by [logos#321](https://github.com/c-daly/logos/issues/321)

### Blocked Tests Summary

**SDK/API Contract Issues (2 tests):**
- [sophia#32](https://github.com/c-daly/sophia/issues/32): API expects dict for goal, SDK sends string
- [apollo#91](https://github.com/c-daly/apollo/issues/91): SophiaClient.create_goal() format mismatch
- [hermes#26](https://github.com/c-daly/hermes/issues/26): HEAD method support (worked around in tests)

**Missing Features (9 tests):**
- [logos#240](https://github.com/c-daly/logos/issues/240): Media ingestion (3 tests)
- [logos#315](https://github.com/c-daly/logos/issues/315): Playwright browser automation (3 tests)
- [logos#321](https://github.com/c-daly/logos/issues/321): OpenTelemetry integration (3 tests)

## Running Tests

### Prerequisites

See [DEVELOPMENT.md](../../DEVELOPMENT.md) for Python environment setup. Additional requirements:

```bash
# Install test dependencies
cd logos
pip install -e ".[test]"

# Install Apollo SDK (required for client fixtures)
cd ../apollo
pip install -e .
```

Services must be running (see README.md "Infrastructure Setup" or use docker-compose.test.yml below).

### Test Environments

**Option 1: Isolated test environment (recommended)**
```bash
cd logos/tests/phase2
docker compose -f docker-compose.test.yml up -d
# Services start on default ports with test-specific data volumes
```

**Option 2: Existing dev environment**
```bash
# If already running infra/docker-compose.hcg.dev.yml
cd logos
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py -v
```

### Running Tests

```bash
# All Phase 2 E2E tests
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py -v

# Specific test class
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py::TestP2M1ServicesOnline -v

# With coverage
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py --cov --cov-report=html

# Verbose output with logs
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py -vv -s
```

### Configuration

Override service URLs via environment variables:

```bash
export SOPHIA_URL=http://localhost:8001
export HERMES_URL=http://localhost:8002
export APOLLO_URL=http://localhost:8003
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=logosdev
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
export RUN_P2_E2E=1  # Required to enable tests
```

Or pass as pytest options:
```bash
RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py -v \
  --sophia-url=http://custom-sophia:8001 \
  --hermes-url=http://custom-hermes:8002
```

## Test Fixtures

Available fixtures in `fixtures.py`:

**Service Clients:**
- `sophia_client` - SophiaClient instance
- `hermes_client` - HermesClient instance  
- `persona_client` - PersonaClient instance
- `all_clients` - Dict with all clients

**Service Health:**
- `services_running` - Service health status dict
- `require_services` - Skip if services unavailable

**Database Cleanup:**
- `clean_neo4j` - Reset test data in Neo4j
- `clean_milvus` - Reset test collections in Milvus

**Test Data:**
- `sample_embeddings` - Mock embedding data
- `sample_cwmstate` - Sample CWMState envelope
- `sample_persona_entry` - Sample persona entry
- `sample_simulation_request` - Sample simulation request

Usage:
```python
def test_something(sophia_client, clean_neo4j):
    response = sophia_client.create_goal("test goal")
    assert response.success
```

## CI Integration

Phase 2 E2E tests run automatically in GitHub Actions (`.github/workflows/phase2-e2e.yml`) on:
- Pull requests affecting `logos/`, `sophia/`, `hermes/`, `apollo/`
- Pushes to `main`
- Manual workflow dispatch

**Workflow (matches validated local setup):**
1. Starts infrastructure (Neo4j + Milvus) via docker-compose.test.yml
2. Waits for infrastructure to be healthy
3. Installs Poetry and logos dependencies
4. Installs Apollo SDK into logos virtualenv
5. Starts services (Sophia, Hermes, Apollo) with proper env vars
6. Runs Phase 2 E2E tests with RUN_P2_E2E=1
7. Stops services and cleans up infrastructure

**Environment Variables (CI):**
- `NEO4J_URI=bolt://localhost:7687`
- `NEO4J_USER=neo4j`
- `NEO4J_PASSWORD=logosdev`
- `MILVUS_HOST=localhost`
- `MILVUS_PORT=19530`
- `SOPHIA_API_KEY=test-ci-key`
- `HERMES_PORT=8002`
- `APOLLO_PORT=8003`
- `RUN_P2_E2E=1`

See [CI Workflow](../../.github/workflows/phase2-e2e.yml) for full details.

## Troubleshooting

**Services not starting:**
```bash
# Check logs
docker compose -f docker-compose.test.yml logs

# Check specific service
docker logs logos-phase2-sophia-test

# Verify ports available
netstat -an | grep -E '7687|8001|8002|8003|19530'
```

**Tests failing:**
```bash
# Check service health
curl http://localhost:8001/health  # Sophia
curl http://localhost:8002/health  # Hermes

# Check Neo4j
docker exec logos-phase2-neo4j-test cypher-shell -u neo4j -p logosdev "RETURN 1"

# Check Milvus
curl http://localhost:9091/healthz
```

**Import errors:**
```bash
# Verify Apollo SDK installed
cd apollo && pip install -e .

# Test import
python -c "from apollo.client.sophia_client import SophiaClient; print('OK')"
```

**Port conflicts:**
```bash
# Stop conflicting services
docker compose -f infra/docker-compose.hcg.dev.yml down

# Or use different ports in docker-compose.test.yml
```

See [Operations Guide](../../docs/operations/) for more troubleshooting.

## Adding New Tests

1. **Add test method to appropriate class in `test_phase2_end_to_end.py`:**
   ```python
   class TestP2M1ServicesOnline:
       def test_new_service_check(self):
           """Verify new service is available."""
           response = requests.get(f"{NEW_SERVICE_URL}/health")
           assert response.status_code == 200
   ```

2. **Use existing fixtures or add new ones to `fixtures.py`:**
   ```python
   @pytest.fixture
   def new_service_client() -> NewClient:
       """Create NewClient instance."""
       return NewClient(config)
   ```

3. **Mark blocked tests appropriately:**
   ```python
   @pytest.mark.skip(reason="Blocked by logos#XXX - feature not implemented")
   def test_future_feature(self):
       pass
   ```

4. **Update this README** with new test descriptions and coverage stats

5. **Run tests locally** to verify:
   ```bash
   RUN_P2_E2E=1 pytest tests/phase2/test_phase2_end_to_end.py::TestClass::test_method -v
   ```

See [Contributing Guide](../../CONTRIBUTING.md#phase-2-e2e-testing-requirements) for PR requirements.

## References

- **Issue:** [c-daly/logos#324](https://github.com/c-daly/logos/issues/324) - Phase 2 E2E Testing
- **Parent:** [c-daly/logos#322](https://github.com/c-daly/logos/issues/322) - Testing Gaps
- **Phase 1 Pattern:** [`tests/phase1/test_m4_end_to_end.py`](../phase1/test_m4_end_to_end.py)
- **Phase 2 Spec:** [`apollo/docs/phase2/PHASE2_SPEC.md`](../../apollo/docs/phase2/PHASE2_SPEC.md)
- **Contributing:** [`CONTRIBUTING.md`](../../CONTRIBUTING.md#phase-2-e2e-testing-requirements)
