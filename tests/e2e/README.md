# Shared Test Stack Assets

This directory holds the rendered Docker Compose bundles that downstream repos (Apollo, Hermes, Sophia, Talos) commit verbatim for their end-to-end tests. LOGOS remains the source of truth: contributors refresh the artifacts here, then push the copies to the individual repos so every stack stays in sync. Lighter-weight contract suites live next door in `tests/integration/` (see its README for guidance) so newcomers can immediately tell which scripts bring up the full stack.

## Directory layout

```
tests/e2e/
├── README.md                 # This guide
└── stack/
    ├── shared/               # Assets consumed by every repo (placeholders for now)
    └── <repo>/               # Repo-specific outputs (apollo, hermes, sophia, talos, logos)
        ├── docker-compose.test.yml
        ├── .env.test
        └── STACK_VERSION
```

`shared/` is intentionally kept in this repo so that future helpers (scripts, sanity checks, lint rules) have a single home. Generator runs will create the `<repo>/` directories as needed; commit the resulting files in both LOGOS and the target repo whenever the template changes.

## Rendering the stacks

From the LOGOS repository root:

```bash
poetry run python infra/scripts/render_test_stacks.py
```

Key flags:

- `--repo <name>` renders only the requested repo (repeat flag to render multiple).
- `--check` recomputes outputs and fails if anything under `tests/e2e/stack/` is stale.
- `--output-root` already points at `tests/e2e/stack/` by default; override it only when experimenting locally.

The generator writes three files per repo:

1. `docker-compose.test.yml` – fully resolved services with repo-specific prefixes and ports.
2. `.env.test` – canonical environment variables consumed by helper scripts and CI.
3. `STACK_VERSION` – a 12-character SHA derived from the template, repo config, and env file contents. Downstream repos copy this to detect when their committed assets drift from LOGOS.

## Env schema

Every generated `.env.test` contains the following keys (superset of what downstream repos currently read):

| Variable | Meaning |
| --- | --- |
| `NEO4J_URI` | Bolt URL emitted by the template (e.g. `bolt://neo4j:7687`). |
| `NEO4J_USERNAME` | Canonical Neo4j username for clients. |
| `NEO4J_USER` | Temporary alias for repos that have not migrated to `NEO4J_USERNAME` yet. |
| `NEO4J_PASSWORD` | Password matching the credentials baked into the compose file. |
| `MILVUS_HOST` | Hostname of the Milvus server container (blank for Talos-only stacks). |
| `MILVUS_PORT` | gRPC port for Milvus (blank when Milvus is not part of the stack). |
| `MILVUS_HEALTHCHECK` | HTTP endpoint used by helper scripts to wait on Milvus readiness. |

Additions (e.g. MinIO, OTEL) should be made in `infra/test_stack/repos.yaml` so they propagate to every repo the next time the generator runs.

## Downstream sync checklist

1. Run the generator as described above (optionally with `--repo` to limit scope).
2. Inspect the diffs under `tests/e2e/stack/<repo>/` and confirm the compose/env files match expectations.
3. Copy the entire `<repo>/` directory into the matching downstream repository (replace its committed files).
4. Commit both the LOGOS changes **and** the downstream repo changes, ensuring `STACK_VERSION` travels with them.
5. Update that repo's helper script(s) to source the `.env.test` file if anything in the schema changed.
6. In the parent tracker issue (#358), check off the repo once its changes land so the shared board stays current.

## Verification

Use the `--check` flag to ensure staged files match the current template:

```bash
poetry run python infra/scripts/render_test_stacks.py --check
```

This command recomputes the compose/env files and exits non-zero if any file differs. CI can wire this into a guardrail so changes to `infra/test_stack/` cannot merge without refreshing the rendered assets first.
