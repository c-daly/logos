# Workflow Inventory

> Tracking LOGOS #293 (workflow inventory) under the CI/Test Parity initiative in LOGOS #32. Updated: 2025-11-21.

This document captures the current GitHub Actions coverage across the active LOGOS repositories so we can identify the gaps that the shared workflow template (issue #294) must close.

## Coverage Snapshot

| Repo | Key workflows | Lint/Format | Type check | Unit tests | Service / integration | E2E / system | Coverage artifact | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logos | `test`, `m1–m4`, `phase2-otel`, `phase2-perception`, `validate-artifacts` | ✅ Ruff in `test.yml` | ❌ mypy installed but unused | ✅ Pytest matrix (3.10–3.12) | ✅ Phase 2 pipelines, ontology + collector validation | ✅ Docker-based M4 flow (weekly + PR) | ⚠️ Uploads XML as artifact only | Needs consistent type-checking and fewer bespoke triggers |
| apollo | `ci`, `e2e`, `phase2-apollo-web` | ✅ Ruff/Black + npm lint | ✅ mypy + TS type-check | ✅ Pytest (3.9–3.11) & web unit tests | ✅ CLI E2E harness brings up Sophia/Talos stubs | ✅ Same harness (opt-in skip) | ✅ Codecov for Python (web build produces dist only) | E2E job can be skipped; JS coverage not published |
| sophia | `ci` | ✅ Black/Ruff | ❌ | ✅ Pytest (unit only) | ❌ | ❌ | ✅ Codecov (py3.12 only) | No integration/perception tests wired into CI |
| hermes | `ci`, `phase2-hermes-service` | ✅ Ruff/Black | ✅ mypy | ✅ Pytest via Poetry | ⚠️ Milvus/Neo4j job only on push or labeled PRs | ❌ | ✅ Codecov with flags | Two workflows duplicate logic; integration not enforced on PRs |
| talos | `ci` | ✅ Ruff/Black | ✅ mypy | ✅ Pytest (3.11–3.12) | ❌ | ❌ | ✅ Codecov (py3.12) | Runs on `main` only; no hardware or shim coverage |

Legend: ✅ = covered, ⚠️ = partially covered / optional, ❌ = not covered.

## Repository Details

### logos (core knowledge graph)

| Workflow | Scope | Notes |
| --- | --- | --- |
| `test.yml` | Multi-version pytest + Ruff lint | Installs mypy but never runs it; uploads `coverage.xml` as an artifact instead of Codecov. |
| `m1-neo4j-crud.yml` | Acceptance test for CRUD paths against Neo4j via docker-compose | Runs weekly + on PRs; ensures infra stack spins up but never reports coverage. |
| `m2-shacl-validation.yml` | Validates SHACL shapes and ontology constraints | Provides semantic checks but no unit suite. |
| `m3-planning.yml` | Planning pipeline smoke test | Uses planner stub / ontology data; currently optional via workflow dispatch. |
| `m4-end-to-end.yml` | Full Apollo→Sophia→Talos→HCG demo | Heavy docker setup with optional skip flag; weekly cron + PRs. |
| `phase2-otel.yml` | OTel collector + observability smoke tests | Validates configs and JEPA instrumentation; includes YAML/JSON validation job. |
| `phase2-perception.yml` | JEPA runner + simulation service tests | Uploads coverage via Codecov token but only for perception files. |
| `validate-artifacts.yml`, `sdk-regen.yml`, `publish-api-docs.yml`, `weekly-progress.yml`, `create-phase1-issues.yml` | Automation / reporting | Not directly tied to test coverage but need consideration when standardizing triggers. |

Gaps:
- No enforced type-checking despite mypy dependency.
- Coverage data is split between artifacts and targeted Codecov uploads; nothing for the base library.
- M1–M4 jobs are long-running and sometimes skipped manually, so they do not provide reliable gates.

### apollo

| Workflow | Scope | Notes |
| --- | --- | --- |
| `ci.yml` | Lint (Ruff/Black), mypy, pytest with coverage upload | Matrix across 3.9–3.11; Codecov tokenless upload enabled. |
| `phase2-apollo-web.yml` | Webapp lint/type-check/test/build | Triggered only on `webapp/**` changes; build artifact retained for 7 days but no coverage upload. |
| `e2e.yml` | Docker-based CLI→Sophia→Talos E2E | Can be skipped via workflow-dispatch input; uses test harness from `tests/e2e`. |

Gaps:
- Webapp job runs independently of the Python CI so status checks can pass without the web verification.
- E2E workflow lacks retries for flaky service startup and has no coverage or artifact to prove plan generation.
- No shared badge/reporting across repos yet (ties into issue #295).

### sophia

| Workflow | Scope | Notes |
| --- | --- | --- |
| `ci.yml` | Black, Ruff, Poetry-based pytest (unit only) | Skips `@pytest.mark.integration` suites; Codecov upload only when python=3.12. |

Gaps:
- No mypy or pyright equivalent, even though type hints are pervasive.
- Integration tests for planner calls, JEPA interactions, and HCG persistence are absent from CI.
- No e2e workflow to coordinate with Apollo CLI tests; everything relies on local test harnesses.

### hermes

| Workflow | Scope | Notes |
| --- | --- | --- |
| `ci.yml` | Ruff, Black, mypy, pytest matrix (3.11/3.12) + integration option | Integration job starts etcd/minio/milvus/neo4j but only runs on push or with PR label `integration-test`. |
| `phase2-hermes-service.yml` | Mirrors CI for Phase 2 plus Milvus smoke test | Duplicates lint/type/test logic, then runs docker compose Milvus smoke tests with Codecov flags. |

Gaps:
- Integration coverage is optional on PRs, so regressions can merge without exercising Milvus or Neo4j.
- Two workflows run nearly identical install/lint/test steps; consolidating into a reusable workflow will reduce drift.
- No system-level E2E linking Hermes to downstream services (Sophia/HCG).

### talos

| Workflow | Scope | Notes |
| --- | --- | --- |
| `ci.yml` | Ruff, Black, mypy, pytest with 95% coverage gate | Publishes coverage to Codecov only for Python 3.12; matrix also runs 3.11. |

Gaps:
- Workflow triggers only watch `main`, so feature branches cannot rely on CI until merged.
- No integration tests for the shim or hardware abstractions.
- No E2E orchestration alongside Apollo/Sophia flows yet.

## Next Steps (toward issue #294 / #295)

1. Define a reusable workflow template that standardizes lint → type check → unit → integration → e2e stages and centralizes Codecov uploads.
2. Gate PRs on the standardized workflow per repo (including Sophia/Talos integration suites).
3. Publish consistent README badges per repo once the shared workflow is live.

These items will be tracked in LOGOS issues #294 (template) and #295 (badges & documentation) after validating this inventory with the team.
