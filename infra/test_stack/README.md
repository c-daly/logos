# Shared Test Stack Template

This directory defines a canonical Docker Compose template for the LOGOS test infrastructure
(Neo4j, Milvus, MinIO, etc.) plus a generator that stamps repo-specific `docker-compose.test.yml`
files. The goal is to keep every repository's CI stack self-contained **and** consistent: we make
changes once here, regenerate, and commit the refreshed compose/env files into the downstream
repository.

**Status:** ✅ **Complete** - Standardization implemented across all repos (Nov 2025)

## Purpose

- **Consistency**: Single source of truth for test infrastructure configuration
- **Isolation**: Each repo gets unique port assignments to prevent conflicts
- **Maintainability**: Update once here, regenerate everywhere
- **Standardization**: Unified credentials (`neo4j/logosdev`), environment variables, and helper patterns

## Layout

```
test_stack/
├── README.md                 # You are here
├── repos.yaml                # Declarative description of each repo's needs
├── services.yaml             # Base service/volume/network templates with format placeholders
├── overlays/                 # Optional service fragments that repos can opt into
└── out/                      # Staging area for generated outputs (gitignored)
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

### `out/`
- Temporary staging directory where the generator writes outputs inside this repo. Once the files
  look good, copy/commit them into the target repo (or automate the sync in a follow-up step).
- `out/` stays gitignored so we never accidentally commit preview artifacts to this repo.

## Generator

`logos/infra/scripts/render_test_stacks.py` is the entry point:

```bash
# Available via Poetry script after installation
poetry run render-test-stacks                    # render all repos
poetry run render-test-stacks --repo apollo      # single repo
poetry run render-test-stacks --check            # verify no drift

# Or directly
poetry run python logos/infra/scripts/render_test_stacks.py
```

Key behaviors:
- Supports single or multi-repo selection with `--repo`.
- Writes three artifacts per repo to `tests/e2e/stack/<repo>/`:
  - `docker-compose.test.<repo>.yml`
  - `.env.test`
  - `STACK_VERSION` (12-char hash of the template + relevant config)
- `--check` recomputes outputs and exits non-zero if anything differs (useful for CI drift detection).

## Port Assignments

Each repo has unique port ranges to enable parallel testing:

| Repo | Neo4j Bolt | Neo4j HTTP | Milvus | Milvus Admin |
|------|------------|------------|--------|--------------|\n| logos (dev) | 7687 | 7474 | 19530 | 9091 |
| apollo | 27687 | 27474 | 29530 | 29091 |
| hermes | 19687 | 19474 | 19530 | 19091 |
| sophia | 37687 | 37474 | 39530 | 39091 |
| talos | 47687 | 47474 | 49530 | 49091 |

See `docs/operations/PORT_REFERENCE.md` for complete reference.

## Credentials

All repos use standardized credentials:
- **Neo4j**: `neo4j/logosdev`
- **Milvus**: No authentication (test mode)
- **MinIO**: `minioadmin/minioadmin`

## Integration with `logos_test_utils`

Generated `.env.test` files work seamlessly with the `logos_test_utils` package:

```python
from logos_test_utils.neo4j import get_neo4j_config

# Automatically reads from .env.test, falls back to defaults
config = get_neo4j_config()
print(config.uri, config.user, config.password)
```

## Current Status

- ✅ Generator complete and tested
- ✅ All repos have standardized compose/env files
- ✅ Port assignments prevent conflicts
- ✅ Credentials unified across ecosystem
- ✅ `logos_test_utils` package adopted by Phase 1 and Phase 2 tests
- 🔄 Downstream repo adoption in progress (#363-366)
