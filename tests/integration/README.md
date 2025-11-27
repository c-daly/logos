# Integration Test Layout

This directory is the canonical home for LOGOS integration suites—tests that exercise a bounded slice of the platform (individual services, shared helpers, or lightweight contracts) without bringing up the entire multi-repo stack. The neighboring `tests/e2e/` folder covers the full-system Docker Compose workflows, while `tests/integration/` keeps smaller stacks, mocks, and fixtures organized.

## Directory layout

```
tests/integration/
├── README.md
├── suites/                 # Future home for repo-agnostic integration suites (SHACL, ontology, etc.)
└── stack/
    ├── shared/             # Building blocks reused by integration helpers (env templates, scripts)
    └── <repo>/             # Optional rendered assets for repo-specific integration stacks
```

Nothing under `stack/<repo>/` is generated yet—that slot is reserved for cases where we want a lighter-weight compose bundle (e.g., Milvus-only for Hermes) that still comes from the shared template. When those needs surface, rerun the same generator that powers the e2e layout with a different `--output-root`:

```bash
poetry run python infra/scripts/render_test_stacks.py --repo hermes --output-root tests/integration/stack
```

This command emits `docker-compose.test.yml`, `.env.test`, and `STACK_VERSION` under `tests/integration/stack/hermes/`. Because the template logic lives in `infra/test_stack/`, the env schema and hash semantics match `tests/e2e/` exactly; only the target directory changes.

## Usage guidance

- Create new integration suites inside `suites/` (or repo-specific subfolders) and reference assets from `stack/` if you need containers.
- Favor lightweight mocks and direct client calls when possible; fall back to the shared stack assets only when a service dependency cannot be faked cheaply.
- When onboarding downstream repos, keep their integration helpers in this folder and leave end-to-end orchestration in `tests/e2e/` so newcomers immediately understand the scope of each script.

As we migrate legacy `phase1/` and `phase2/` directories, treat this layout as the landing zone: move tests into `tests/integration/` (or `tests/e2e/`) based on the breadth of dependencies they require.
