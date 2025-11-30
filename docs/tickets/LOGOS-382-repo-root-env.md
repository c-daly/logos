# LOGOS-382 — Repo Root Environment Variable Support

- **Issue**: https://github.com/c-daly/logos/issues/382
- **Status**: Open

## Summary
Several tests and helper scripts hard-code repository root paths (for example `Path(__file__).resolve().parents[3]`). This breaks when the repo is vendored, relocated, or consumed through the `logos_test_utils` package. We should expose repo-root paths through environment variables (starting with `LOGOS_REPO_ROOT`) and teach our tooling to respect them.

## Acceptance Criteria
- Introduce environment variables for each repo root (beginning with `LOGOS_REPO_ROOT`) that can be populated via `.env.test`, falling back to the current repo root when unset.
- Update shared helpers (`logos_test_utils`, integration/e2e tests, scripts) to use the new env vars instead of hard-coded parent traversals.
- Verify the suite still runs when the repository is relocated by overriding `LOGOS_REPO_ROOT` in a test or documented example.
- Update documentation (`tests/e2e/README.md`, `docs/operations/TEST_STANDARDIZATION_MIGRATION.md`, etc.) describing how to configure repo roots.

## Implementation Outline
1. **Env plumbing**
   - Extend stack env templates so they emit `LOGOS_REPO_ROOT`.
   - Add a cached `get_repo_root()` helper to `logos_test_utils.env` that resolves the env or falls back to the installed package location.
2. **Refactor callers**
   - Replace hard-coded `parents[...]` path logic in tests (e.g., ontology suites) and scripts with the new helper.
   - Ensure `load_cypher_file`, SHACL loaders, and similar utilities accept repo-root overrides where appropriate.
3. **Docs & validation**
   - Document the new variable and relocation workflow.
   - Add a regression check or CI example verifying the override works.

## Follow-Ups / Questions
- Should sibling repos (Apollo, Hermes, etc.) adopt `*_REPO_ROOT` variables in the same change, or after the pattern lands?
- When `logos_test_utils` ships as a dependency, what is the fallback path resolution strategy (e.g., `import logos` to find package resources)?

## Risks
- Need to maintain backward compatibility—defaults must match current behavior for local dev.
- Ensure environments consuming `logos_test_utils` without `.env.test` still work (fallback logic should be robust).
