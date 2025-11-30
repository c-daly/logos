# Ticket: Shared Test Stack Template

## Summary
Centralize the Docker-based test infrastructure definitions (Neo4j, Milvus, MinIO, etc.) so that every LOGOS repository consumes the same versions, health checks, and credentials while keeping their CI stacks self-contained.

## Problem Statement
- Each repo currently owns a bespoke `docker-compose.test.yml`, making it painful to bump core services (e.g., Milvus or Neo4j) consistently.
- CI jobs require self-contained stacks, so we cannot depend on `logos` being checked out when tests run.
- Divergent configs are already causing drift (different Neo4j passwords, plugin settings, Milvus images, and volume names).

## Goals
1. Authoritative template for shared services lives in `logos`.
2. Generator emits repo-local compose/env files that CI can use without additional steps.
3. Track template version via `STACK_VERSION` hash to detect stale copies.
4. Provide a path for optional overlays (e.g., SHACL service, mock APIs) without duplicating shared services.

## Non-Goals
- Consolidating dev (non-test) Docker Compose setups.
- Automatically copying files into downstream repos (manual commit for now).
- Reworking existing CI workflows beyond switching to the generated compose files.

## Implementation Outline
1. Define base services in `infra/test_stack/services.yaml` with placeholder fields (service prefix, ports, credentials).
2. Describe repo requirements in `infra/test_stack/repos.yaml` (services list, overrides, env vars, optional overlays).
3. Implement `infra/scripts/render_test_stacks.py` to render compose/env files plus `STACK_VERSION` into `infra/test_stack/out/<repo>/`.
4. Document usage in `infra/test_stack/README.md` and keep staged outputs gitignored.
5. Ensure `.github/workflows/run_ci.sh` stays in sync so contributors can mirror CI locally before adopting the generated stacks.
6. (Follow-up) Copy generated files into each repo and add a drift-check workflow.

## Acceptance Criteria
- Template + generator live in `logos` and render without errors for all repos defined in `repos.yaml`.
- Generated compose files include only the services requested per repo and use consistent naming/health checks.
- `.env.test` output contains the standardized connection info for each repo.
- `STACK_VERSION` hash changes whenever template inputs change.
- Documentation explains how to run the generator, interpret outputs, and next steps for syncing downstream repos.

## Open Questions
- Where should overlay fragments (e.g., Apollo's Sophia mock) live and how do we share build contexts?
- Should we wire an automated sync now or wait until downstream repos adopt the generated files?
- Do we need per-repo port customizations to avoid conflicts when multiple stacks run concurrently locally?
