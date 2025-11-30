# Phase 2 E2E Testing Implementation Summary (Updated Layout)

The original Phase 2 effort delivered a comprehensive end-to-end suite plus supporting fixtures, documentation, and CI. Those assets now live in the reorganised structure:

- `tests/e2e/test_phase2_end_to_end.py`
- `tests/e2e/fixtures.py`
- `tests/e2e/conftest.py`
- `tests/e2e/run_e2e.sh` and generated stack under `tests/e2e/stack/`
- `.github/workflows/phase2-e2e.yml`

## Delivered Coverage

| Test class | Focus | Status |
| --- | --- | --- |
| `TestP2M1ServicesOnline` | Baseline health of Sophia, Hermes, Apollo, Neo4j, Milvus | ✅ impl, executes when stack running |
| `TestP2CWMStateEnvelope` | Contract validation across `/plan`, `/state`, `/simulate` | ✅ + skips for known API gaps |
| `TestP2M2ApolloDualSurface` | SDK usage + dual-surface interactions | ✅ + Playwright-dependent skips |
| `TestP2M3PerceptionImagination` | JEPA simulation and imagined state lifecycle | ✅ + media ingestion skips |
| `TestP2M4DiagnosticsPersona` | Persona diary, telemetry assertions | ✅ + OTel skips |
| `TestP2CrossServiceIntegration` | Cross-service chains and error handling | ✅ + OTel skip |
| `TestP2CompleteWorkflow` | Scenario walkthrough across milestones | ✅ partial (skips align with issues) |

Blocked tests remain tagged with `pytest.skip` and issue numbers (#240 media ingestion, #315 browser automation, #321 telemetry, etc.).

## Fixtures & Utilities

`tests/e2e/fixtures.py` provides:

- Service clients (`sophia_client`, `hermes_client`, `persona_client`, `all_clients`)
- Health gating (`services_running`, `require_services`)
- Cleanup helpers (`clean_neo4j`, `clean_milvus`)
- Sample payload factories (`sample_cwmstate`, `sample_embeddings`, `sample_persona_entry`, etc.)

The test stack is reproduced via `tests/e2e/run_e2e.sh`, which wraps the docker-compose bundle generated from `infra/test_stack` definitions.

## CI Integration

- `.github/workflows/phase2-e2e.yml` spins up the shared stack, installs sibling repos (Sophia, Hermes, Apollo), and runs `pytest tests/e2e/test_phase2_end_to_end.py` with `RUN_P2_E2E=1`.
- Complementary workflows (`phase2-perception`, `phase2-otel`) now point at `tests/integration/` for domain-specific integration suites.

## How to Run Locally (Current Best Practice)

```bash
./tests/e2e/run_e2e.sh up        # Start Neo4j + Milvus stack
./tests/e2e/run_e2e.sh seed      # Optional ontology + Milvus bootstrap

RUN_P2_E2E=1 poetry run pytest tests/e2e/test_phase2_end_to_end.py -v

./tests/e2e/run_e2e.sh down      # Tear down stack when finished
```

Ensure Sophia, Hermes, and Apollo are available (either via `scripts/start_services.sh` or your preferred dev environment) before running the suite.

## Roadmap Follow-ups

- Enable skipped telemetry/media/browser cases as upstream issues close.
- Continue migrating documentation consumers to the new `tests/e2e` references (this file kept as breadcrumb for legacy links).
- Periodically regenerate the stack via `poetry run render-test-stacks --repo logos` to pick up infrastructure updates.

For deeper operational guidance see `tests/e2e/README.md` and `docs/operations/TESTING.md`.
