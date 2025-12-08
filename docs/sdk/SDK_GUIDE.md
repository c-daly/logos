# SDK Guide

Client SDKs let Apollo, tests, and external tools call Sophia and Hermes APIs without hand-written HTTP code.

## Available SDKs

### Python
| Package | Source | Install |
|---------|--------|---------|
| `logos-sophia-sdk` | `sdk/python/sophia/` | `pip install git+https://github.com/c-daly/logos.git@main#subdirectory=sdk/python/sophia` |
| `logos-hermes-sdk` | `sdk/python/hermes/` | `pip install git+https://github.com/c-daly/logos.git@main#subdirectory=sdk/python/hermes` |

### TypeScript
| Package | Source |
|---------|--------|
| `@logos/sophia-sdk` | `sdk-web/sophia/` |
| `@logos/hermes-sdk` | `sdk-web/hermes/` |

## Installing SDKs

### Poetry (recommended)

```toml
# pyproject.toml
[tool.poetry.dependencies]
logos-sophia-sdk = {git = "https://github.com/c-daly/logos.git", branch = "main", subdirectory = "sdk/python/sophia"}
logos-hermes-sdk = {git = "https://github.com/c-daly/logos.git", branch = "main", subdirectory = "sdk/python/hermes"}
```

Then: `poetry install`

### pip

```bash
pip install git+https://github.com/c-daly/logos.git@main#subdirectory=sdk/python/sophia
pip install git+https://github.com/c-daly/logos.git@main#subdirectory=sdk/python/hermes
```

### Local development

```bash
cd ~/projects/LOGOS/logos/sdk/python/sophia
pip install -e .
```

## Using the SDKs

### Sophia SDK

```python
from logos_sophia_sdk import ApiClient, Configuration, DefaultApi
from logos_sophia_sdk.models import PlanRequest

config = Configuration(host="http://localhost:8000")
client = ApiClient(configuration=config)
api = DefaultApi(client)

# Create a plan
request = PlanRequest(goal="pick up the red block", context={})
response = api.plan(plan_request=request)
print(f"Plan ID: {response.plan_id}")
```

### Hermes SDK

```python
from logos_hermes_sdk import ApiClient, Configuration, DefaultApi
from logos_hermes_sdk.models import EmbedRequest

config = Configuration(host="http://localhost:8080")
client = ApiClient(configuration=config)
api = DefaultApi(client)

# Generate embeddings
response = api.embed_text(EmbedRequest(text="Hello, world!"))
print(f"Embedding dimension: {len(response.embedding)}")
```

## Regenerating SDKs

When API contracts change (`contracts/*.openapi.yaml`), regenerate:

```bash
cd ~/projects/LOGOS/logos
./scripts/generate-sdks.sh
```

This regenerates all SDKs from the OpenAPI specs. Always commit the regenerated files.

**Requirements:** Node.js/npm (uses `npx @openapitools/openapi-generator-cli`)

## SDK Architecture

```
contracts/
  sophia.openapi.yaml    # API spec (source of truth)
  hermes.openapi.yaml
     ↓ generate-sdks.sh
sdk/python/sophia/       # Generated Python client
sdk/python/hermes/
sdk-web/sophia/          # Generated TypeScript client
sdk-web/hermes/
```

## Publishing

SDKs are consumed directly from git (no PyPI/npm publishing currently). The `logos-foundry` Docker image includes all SDKs pre-installed.

To use the foundry image:

```dockerfile
FROM ghcr.io/c-daly/logos-foundry:latest
# SDKs already available
```

## Troubleshooting

**"Module not found" after poetry install**
```bash
poetry lock --no-update
poetry install
```

**SDK out of date**
```bash
cd ~/projects/LOGOS/logos
git pull
./scripts/generate-sdks.sh
# Then reinstall in consuming repo
```
