# Phase 2 End-to-End Tests (New Layout)

All Phase 2 end-to-end suites now live under `tests/e2e/`. This file remains for historical reference because external docs still deep-link here; everything below explains how to run the migrated test stack.

**See also:** [`tests/e2e/README.md`](../e2e/README.md) for the canonical, always-up-to-date overview of the shared E2E stack.

## Directory Map

```
tests/
├── integration/
│   ├── ontology/
│   ├── planning/
│   ├── perception/
│   └── observability/
└── e2e/
    ├── test_phase1_end_to_end.py
    ├── test_phase2_end_to_end.py   # former phase2 suite
    ├── fixtures.py
    ├── conftest.py
    ├── run_e2e.sh
    └── stack/
        └── logos/docker-compose.test.yml
```

## Quick Start

```bash
# Start the isolated Neo4j + Milvus stack
./tests/e2e/run_e2e.sh up

# (optional) Seed ontology + Milvus collections
./tests/e2e/run_e2e.sh seed

# Run only the Phase 2 E2E suite
RUN_P2_E2E=1 poetry run pytest tests/e2e/test_phase2_end_to_end.py -v

# Stop services when finished
./tests/e2e/run_e2e.sh down
```

The helper script wraps the generated compose file in `tests/e2e/stack/logos/`. It is safe to keep the stack running for local development; use `status` / `logs` subcommands to inspect health.

## Service Dependencies

- **Neo4j 5.14.0** exposed on `bolt://localhost:7687`
- **Milvus v2.4.15** exposed on `localhost:19530` with etcd + MinIO sidecars
- The application services (Sophia, Hermes, Apollo) are started via `scripts/start_services.sh` once the stack is healthy.

Environment variables used by fixtures (override as needed):

```bash
export RUN_P2_E2E=1
export SOPHIA_URL=http://localhost:8001
export HERMES_URL=http://localhost:8002
export APOLLO_URL=http://localhost:8003
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=neo4jtest
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
```

## Test Modules

The suite remains organised by milestone-focused classes inside `tests/e2e/test_phase2_end_to_end.py`:

- `TestP2M1ServicesOnline` – baseline service health
- `TestP2CrossServiceIntegration` – chained API flows across services
- `TestP2CompleteWorkflow` – end-to-end workflow assertions
- `TestP2M2ApolloDualSurface`, `TestP2M3PerceptionImagination`, `TestP2M4DiagnosticsPersona` – milestone-specific coverage with targeted skips documented inline
- Shared fixtures (`tests/e2e/fixtures.py`) provide client instances, Milvus/Neo4j cleanup, and sample data payloads.

For service-specific integration coverage (ontology, planning, perception, observability) refer to `tests/integration/`.

## CI Entry Points

- `.github/workflows/phase2-e2e.yml` – runs this suite after bringing up the shared stack and bootstrapping sibling repos
- `.github/workflows/phase2-perception.yml`, `.github/workflows/phase2-otel.yml` – now target the `tests/integration/*` subdirectories

## Adding New Phase 2 E2E Coverage

1. Place assertions in the relevant class within `tests/e2e/test_phase2_end_to_end.py`.
2. Extend `tests/e2e/fixtures.py` if additional shared state or service clients are required.
3. Document any intentional skips with linked tracking issues.
4. Verify locally with `RUN_P2_E2E=1 poetry run pytest tests/e2e/test_phase2_end_to_end.py::TestClass::test_case -v`.

## Legacy Files

`docker-compose.test.yml` remains here temporarily for backwards compatibility but the canonical definition is generated into `tests/e2e/stack/logos/`. Prefer the new location to avoid divergence.

Questions? See the [operations testing guide](../../docs/operations/TESTING.md) or ping #logos-testing in Slack.
