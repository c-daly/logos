# Ticket: Repo Root Environment Variable Support

## Summary
We currently hard-code repository root paths in multiple test helpers and scripts (e.g., resolving `Path(__file__).parents[3]`). This causes fragility and prevents reusing the shared tooling when repositories are vendored, renamed, or relocated (e.g., running tests from a different checkout path, or consuming `logos_test_utils` from another project). We should standardize on environment variables for repo roots and allow overrides via generated `.env.test` files.

## Acceptance Criteria
- Introduce an environment variable for each repo root (starting with `LOGOS_REPO_ROOT` for this repository) that can be populated from `.env.test` (and default to the current repo root when unset).
- Update shared helpers (`logos_test_utils`, test suites, and scripts) to use the new environment variable instead of hard-coded path traversal.
- Ensure tests continue to pass when the repo is relocated, including when `LOGOS_REPO_ROOT` is set to a different path (write at least one test or documentation example demonstrating this).
- Update documentation (e.g., `tests/e2e/README.md`, relevant migration guides) describing how to override repo roots for custom setups.

## Proposed Implementation Outline
1. **Define environment variables**
   - Extend `tests/e2e/stack/logos/.env.test` (and equivalent stack templates) with `LOGOS_REPO_ROOT=${LOGOS_REPO_ROOT:-/workspace/logos}` (or similar sensible default).
   - Update `logos_test_utils.env.load_stack_env` to expose `LOGOS_REPO_ROOT` and provide a `get_repo_root()` helper with caching.

2. **Refactor helpers and tests**
   - Replace occurrences of `Path(__file__).resolve().parents[...]` in tests and scripts (starting with `tests/integration/ontology` modules) with calls to the new helper.
   - Ensure `load_cypher_file`, `load_shacl` utilities, and other cross-repo scripts accept or derive the repo root from the new environment variable.

3. **Documentation & Validation**
   - Document the new environment variable in `tests/e2e/README.md` and `docs/operations/TEST_STANDARDIZATION_MIGRATION.md`.
   - Add a short regression test or CI check verifying that overriding `LOGOS_REPO_ROOT` works (e.g., set to a temp directory copy during tests).

## Open Questions / Follow-ups
- Should we introduce similar env vars for sibling repositories (e.g., `APOLLO_REPO_ROOT`, `HERMES_REPO_ROOT`) as part of the same ticket, or stage that work separately once the pattern is in place?
- How do we want to distribute defaults when `logos_test_utils` is installed from another repo (path vs. package resource)? May require a fallback to `import logos` to find the installed location.

## Risks
- Need to ensure backward compatibility where scripts rely on current behavior (e.g., running within the repo without `.env.test`).
- Packaging `logos_test_utils` as a dependency must still work when the repo is not adjacent; ensure the helper gracefully handles missing env values.

## Related Work
- `tests/integration/ontology/test_neo4j_crud.py` path fixes (`feat/logos-356-neo4jtest-standard` branch).
- Test infrastructure standardization documented in `docs/operations/TEST_STANDARDIZATION_MIGRATION.md`.
