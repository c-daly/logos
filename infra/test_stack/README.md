# Shared Test Stack Template

This directory defines a canonical Docker Compose template for the LOGOS test infrastructure
(Neo4j, Milvus, MinIO, etc.) plus a generator that stamps repo-specific `docker-compose.test.yml`
files. The goal is to keep every repository's CI stack self-contained **and** consistent: we make
changes once here, regenerate, and commit the refreshed compose/env files into the downstream
repository. The background, goals, and acceptance criteria for this work live in
[c-daly/logos#359](https://github.com/c-daly/logos/issues/359).

## Layout

```
test_stack/
├── README.md                 # You are here
├── repos.yaml                # Declarative description of each repo's needs
├── services.yaml             # Base service/volume/network templates with format placeholders
├── overlays/                 # Optional service fragments that repos can opt into
└── (rendered into tests/e2e/stack/) # Generator writes to the shared e2e stack layout
```

### `repos.yaml`
- Lists every repo we manage (`apollo`, `hermes`, `logos`, `sophia`, `talos`).
- Defines the relative path to that repo from this file, the compose/env filenames, which
  services to include, service-prefix overrides, and any overlay fragments.
- Holds repo-specific environment overrides so credentials and connection URIs stay accurate.

### `services.yaml`
- Holds the authoritative definition of each shared service.
- Strings support Python-style placeholders (e.g. `{service_prefix}`) which the generator fills at
  runtime with values from `repos.yaml`.
- Add/modify services here when we bump images, ports, or health checks.

### `overlays/`
- Placeholder for optional services that only some repos need (e.g. SHACL validation, mock APIs).
- Each overlay file is a YAML fragment with `services`, `volumes`, or `networks` keys that the
  generator merges after rendering the base template.

### Rendered outputs
- Files land under `tests/e2e/stack/<repo>/` at the repo root. That directory is **not**
  gitignored; LOGOS commits those artifacts so downstream repos can copy them verbatim.
  Structure matches the neutral layout discussed in #356 (`stack/shared/`, `stack/apollo/`, etc.).

## Generator

`logos/infra/scripts/render_test_stacks.py` is the only entry point:

```bash
poetry run python infra/scripts/render_test_stacks.py                               # render all repos
poetry run python infra/scripts/render_test_stacks.py --repo apollo                 # render one repo
poetry run python infra/scripts/render_test_stacks.py --check                       # verify outputs
```

Key behaviors:
- Supports single or multi-repo selection with `--repo`.
- Writes three artifacts per repo inside `tests/e2e/stack/<repo>/`:
  - `docker-compose.test.yml`
  - `.env.test`
  - `STACK_VERSION` (12-char hash of the template + relevant config)
- `--check` recomputes outputs and exits non-zero if anything differs, which is useful for a future
  GitHub Action that guards against drift.

## Next Steps (outside this PR)
1. Copy generated files into each repo and update their CI workflows to call the shared stack.
2. Add an automated sync job (probably here in `logos/.github/workflows`) that runs the generator,
   checks for diffs, and either commits them or fails fast.
3. Populate the `overlays/` directory with real fragments (e.g. Apollo's Sophia mock, OTEL stack,
   SHACL service) and reference them from `repos.yaml`.

Until then, this directory provides the tooling + documentation so we can have a concrete
discussion about the approach.
