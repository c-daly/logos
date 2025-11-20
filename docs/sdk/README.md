# LOGOS SDKs

Shared client SDKs allow the CLI, browser, and automation jobs to consume the Sophia and Hermes APIs without hand-written HTTP glue. This directory documents how to install, regenerate, and publish the generated packages.

## Available Packages

### Python (sdk/)
- `sdk/python/sophia` → `logos_sophia_sdk`
- `sdk/python/hermes` → `logos_hermes_sdk`

### TypeScript (sdk-web/)
- `sdk-web/sophia` → `@logos/sophia-sdk`
- `sdk-web/hermes` → `@logos/hermes-sdk`

The packages are generated from the OpenAPI contracts in `contracts/`.

## Regenerating SDKs

Whenever `contracts/sophia.openapi.yaml` or `contracts/hermes.openapi.yaml` change, regenerate all SDKs:

```bash
./scripts/generate-sdks.sh
```

Requirements:
- Node.js/npm (script uses `npx @openapitools/openapi-generator-cli`)

The script overwrites everything under `sdk/` and `sdk-web/`. Always commit the regenerated files.

## Installing Locally

### Python

From the desired SDK directory:

```bash
cd sdk/python/sophia
pip install .
```

or for development:

```bash
pip install -e .
```

Then import in your project:

```python
from logos_sophia_sdk import Configuration, PlanningApi
```

Repeat with `sdk/python/hermes` for Hermes.

### TypeScript / JavaScript

Link locally using `npm`:

```bash
cd sdk-web/sophia
npm install
npm pack  # produces a tarball
```

Then install that tarball in the consumer project, or use `npm link` for development. Once published to an npm registry, install via `npm install @logos/sophia-sdk`.

## Versioning & Publishing

Generated packages default to version `0.1.0`. When cutting a release:
1. Update `packageVersion`/`npmVersion` in `scripts/generate-sdks.sh` (or edit the generated `pyproject.toml`/`package.json`).
2. Regenerate and commit.
3. Publish:
   - Python: `cd sdk/python/<name> && python -m build && twine upload dist/*` (requires credentials).
   - TypeScript: `cd sdk-web/<name> && npm publish` (configure registry as needed).

Document published versions in release notes so downstream clients can pin known-good builds.

## Continuous Integration

Future work (Issue #256) will add a GitHub Actions workflow to regenerate SDKs when contracts change and fail if generated files are out of date. Until then, run `./scripts/generate-sdks.sh` manually before submitting PRs that touch `contracts/`.
