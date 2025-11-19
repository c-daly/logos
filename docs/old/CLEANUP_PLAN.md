# Cleanup Plan (Phase 1 Closers)

Tracking issue: https://github.com/c-daly/logos/issues/206

Goals:
- Reduce test/CI complexity and keep defaults lean.
- Separate fast unit/static checks from optional integration/E2E.
- Prune unused scaffolding and align tests with actual fixtures.

Proposed actions:
- Tests:
  - Split heavy or integration-like tests (deep mocks, service deps) behind explicit markers/flags.
  - Keep default CI running pyshacl + unit smoke; move Neo4j SHACL and M4 E2E to opt-in jobs/flags.
  - Align assertions with fixtures (avoid name mismatches like "Manipulator" vs. RobotArm01).
- CI:
  - Ensure optional jobs (e.g., Neo4j SHACL, full M4) are gated by inputs/env (e.g., RUN_NEO4J_SHACL, skip_e2e).
  - Trim redundant steps/artifacts; surface clear summaries.
- Repo hygiene:
  - Remove unused scripts/workflows; document how to run optional checks locally.
  - Keep Dockerfiles minimal; only copy needed packages/files.

Next steps:
- Identify heavy tests to mark as integration/slow or refactor into simpler unit coverage.
- Adjust CI workflows to run optional jobs only when requested.
- Update docs (PHASE1_VERIFY, scripts README) to describe optional vs required checks and how to enable them.***
