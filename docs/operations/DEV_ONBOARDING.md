# Developer Onboarding Guide

Last updated: December 2025

## 0) Prerequisites
- Docker + Docker Compose
- Python 3.11
- Poetry (`curl -sSL https://install.python-poetry.org | python3 -`)
- Git + GitHub SSH access

## 1) Get the repo
```bash
git clone git@github.com:c-daly/logos.git
cd logos
poetry install --with dev,test
```

## 2) Core commands (CI parity)
```bash
poetry run ruff check src tests
poetry run black --check src tests
poetry run mypy src
poetry run pytest --cov --cov-report=term --cov-report=xml
```
Notes:
- Coverage upload to Codecov is disabled; `coverage.xml` is still produced.
- Perception workflow jobs use Poetry; align local runs accordingly.

## 3) Infra: HCG stack (Neo4j + Milvus + SHACL)
Quick start:
```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d
./infra/load_ontology.sh
./infra/init_milvus.sh
```
Ports: Neo4j 7474/7687, Milvus 19530 (gRPC) / 9091 (metrics). Credentials: `neo4j/neo4jtest`.

Stop/clean:
```bash
docker compose -f infra/docker-compose.hcg.dev.yml down    # keep data
docker compose -f infra/docker-compose.hcg.dev.yml down -v # wipe data
```

## 4) E2E test stack (Phase 2)
```bash
./tests/e2e/run_e2e.sh up
SOPHIA_API_KEY=test-token-12345 RUN_P2_E2E=1 poetry run pytest tests/e2e/test_phase2_end_to_end.py -v
./tests/e2e/run_e2e.sh down
```
Stack ports: Neo4j 7474/7687, Milvus 19530/9091, Sophia 8001, Hermes 8002, Apollo 8003.

## 5) Observability stack (OTEL + Jaeger + Prometheus)
```bash
./scripts/start-otel-stack.sh
# Jaeger: http://localhost:16686
# Prometheus: http://localhost:9090
./scripts/stop-otel-stack.sh
```
Service env vars:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4319
VITE_OTEL_EXPORTER_URL=http://localhost:4320/v1/traces
```
See `docs/observability/OTEL_INFRASTRUCTURE.md` and `docs/operations/OBSERVABILITY_QUERIES.md`.

## 6) Common checks
- **Lint/format/type/test:** `poetry run ruff …`, `black --check`, `mypy`, `pytest`
- **Ports busy?** `lsof -i :7687` / `lsof -i :19530`
- **Neo4j health:** `curl http://localhost:7474`
- **Milvus health:** `curl http://localhost:9091/healthz`

## 7) Docs to know
- Architecture: `docs/architecture/PHASE1_SPEC.md`, `docs/architecture/PHASE2_SPEC.md`
- Testing: `docs/operations/TESTING.md`
- Ports: `docs/operations/PORT_REFERENCE.md`
- OTEL: `docs/observability/OTEL_INFRASTRUCTURE.md`
- Assessment: `ASSESSMENT_SUMMARY.md`, `docs/operations/CANDID_ASSESSMENT_2025_12.md`

## 8) Workflow tips
- Use Poetry for all Python commands (`poetry run …`).
- Keep stacks off when not in use (`run_e2e.sh down`, `stop-otel-stack.sh`).
- Align branches with the shared CI template; re-run CI-parity commands locally before pushing.
