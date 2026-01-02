# Package Publishing Guide

This document describes how to publish and consume the `logos-foundry` package using GitHub Container Registry.

## Overview

`logos-foundry` is published as a container image to GitHub Container Registry (ghcr.io) to enable other LOGOS repositories to consume shared utilities and dependencies without path dependencies.

**Package Name:** `logos-foundry`  
**Current Version:** `0.1.0`  
**Registry:** `ghcr.io/c-daly/logos-foundry`

## What's Included

The container includes:
- All logos packages: `logos_test_utils`, `logos_hcg`, `logos_observability`, `logos_perception`, `logos_persona`, `logos_sophia`, `logos_cwm_e`, `logos_tools`, `planner_stub`
- All runtime and test dependencies (pytest, rdflib, pyshacl, neo4j, pymilvus, opentelemetry, etc.)
- Poetry for package management
- Python 3.11

## Publishing New Versions

### Automatic Publishing (Recommended)

1. **Update version in `pyproject.toml`:**
   ```bash
   # Bump version following semver: MAJOR.MINOR.PATCH
   poetry version patch  # 0.1.0 -> 0.1.1
   poetry version minor  # 0.1.0 -> 0.2.0
   poetry version major  # 0.1.0 -> 1.0.0
   ```

2. **Commit the version change:**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to $(poetry version -s)"
   git push origin main
   ```

3. **Create a GitHub release:**
   - Go to https://github.com/c-daly/logos/releases/new
   - Create tag: `v0.1.1` (matching version in pyproject.toml)
   - Set as title: `v0.1.1`
   - Add release notes describing changes
   - Click "Publish release"

4. **Verify publication:**
   - GitHub Actions will automatically trigger the publish workflow
   - Check workflow at: https://github.com/c-daly/logos/actions
   - Container appears at: https://github.com/c-daly/logos/pkgs/container/logos-foundry

### Manual Publishing

If you need to publish without creating a release:

1. **Trigger workflow manually:**
   - Go to https://github.com/c-daly/logos/actions/workflows/publish-package.yml
   - Click "Run workflow"
   - Select branch (usually `main`)
   - Click "Run workflow"

## Consuming the Package in Other Repos

### Using as Base Image in Docker Compose

Most common use case - use the container as a base for running tests:

```yaml
# docker-compose.test.yml
services:
  test-runner:
    image: ghcr.io/c-daly/logos-foundry:0.1.0
    volumes:
      - ./tests:/app/tests
      - ./src:/app/src  # Mount your repo's code
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - MILVUS_HOST=milvus
    command: pytest tests/
    depends_on:
      - neo4j
      - milvus
```

### Using as Base in Dockerfile

Build your service on top of the foundry image:

```dockerfile
# Dockerfile
FROM ghcr.io/c-daly/logos-foundry:0.1.0

# Copy your service code
COPY . /app/myservice
WORKDIR /app/myservice

# Install your service's additional dependencies
RUN poetry install --no-interaction --no-ansi

# Run your service
CMD ["uvicorn", "myservice.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using in GitHub Actions

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/c-daly/logos-foundry:0.1.0
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest tests/
```

## Authentication

### For Public Access (Read-Only)

The container is publicly accessible for pulling - no authentication needed:

```bash
docker pull ghcr.io/c-daly/logos-foundry:0.1.0
```

### For CI/CD (GitHub Actions)

GitHub Actions automatically has access via `GITHUB_TOKEN` for private images:

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### For Local Development (Private Images)

```bash
# Create a Personal Access Token with read:packages scope
# Then login:
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

## Local Development Workflow

When working on changes to `logos-foundry` that need testing in dependent repos:

### Option 1: Mount Local logos Directory

```yaml
# docker-compose.test.yml (temporary)
services:
  test-runner:
    image: ghcr.io/c-daly/logos-foundry:0.1.0
    volumes:
      - ../logos:/app/logos:ro  # Override with local version
      - ./tests:/app/tests
```

### Option 2: Build Custom Image

```dockerfile
# Dockerfile.dev
FROM ghcr.io/c-daly/logos-foundry:0.1.0

# Override with local logos packages
COPY ../logos/logos_test_utils /app/logos_test_utils
COPY ../logos/logos_hcg /app/logos_hcg
# ... other packages as needed
```

### Option 3: Publish a Dev Version

```bash
cd logos
poetry version 0.1.1-dev
# Build and test locally, then trigger workflow
```

## Package Contents

The container includes the following logos sub-packages:

- **`logos_tools`** - CLI tools for issue generation and management
- **`logos_hcg`** - Hybrid Cognitive Graph data structures and utilities
- **`logos_observability`** - OpenTelemetry instrumentation and logging
- **`logos_persona`** - Persona diary and emotional state models
- **`logos_cwm_e`** - Causal World Model - Emotional layer
- **`logos_perception`** - Perception and media ingestion utilities
- **`logos_sophia`** - Sophia-specific utilities
- **`logos_test_utils`** - Shared test fixtures and utilities
- **`planner_stub`** - Planning stub implementations

Plus all test dependencies (pytest, neo4j, pymilvus, rdflib, pyshacl, opentelemetry, etc.)

### Using Test Utilities

```python
# In your repo's tests - everything is already installed
from logos_test_utils import (
    get_neo4j_config,
    get_milvus_config,
    cleanup_neo4j,
    cleanup_milvus,
)

@pytest.fixture
def neo4j_driver():
    config = get_neo4j_config()
    driver = neo4j.GraphDatabase.driver(
        config["uri"],
        auth=(config["username"], config["password"])
    )
    yield driver
    cleanup_neo4j(driver)
    driver.close()
```

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking API changes
- **MINOR** (0.2.0): New features, backward-compatible
- **PATCH** (0.1.1): Bug fixes, backward-compatible

### When to Bump Versions

- **Patch:** Bug fixes in existing functionality
- **Minor:** Adding new sub-packages, new functions/classes, new fixtures
- **Major:** Removing packages, changing function signatures, breaking test fixture changes

### Pre-release Versions

For testing before official release:

```bash
poetry version prerelease  # 0.1.0 -> 0.1.1-alpha.0
poetry version prerelease  # 0.1.1-alpha.0 -> 0.1.1-alpha.1
```

## Troubleshooting

## Troubleshooting

### Container not found

**Error:** `Error response from daemon: pull access denied`

**Solutions:**
1. Verify the image name: `ghcr.io/c-daly/logos-foundry:0.1.0`
2. Check if you need authentication (for private images)
3. Ensure the container version exists: https://github.com/c-daly/logos/pkgs/container/logos-foundry

### Authentication failed

**Error:** `401 Unauthorized` or `403 Forbidden` when pulling

**Solutions:**
1. Login to ghcr.io: `echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin`
2. Verify your Personal Access Token has `read:packages` scope
3. For CI, ensure workflow has `packages: read` permission

### Local changes not reflected

If you're mounting local directories and changes aren't reflected:

```bash
# Rebuild if using custom Dockerfile
docker-compose build --no-cache test-runner

# Or restart services
docker-compose restart test-runner
```

### Import errors in tests

**Error:** `ModuleNotFoundError: No module named 'logos_test_utils'`

**Solutions:**
1. Ensure you're using the foundry container: `image: ghcr.io/c-daly/logos-foundry:0.1.0`
2. Check PYTHONPATH is set correctly (default: `/app`)
3. Verify your code is mounted in the right location

## Version Strategy

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **PATCH (0.1.x):** Bug fixes, documentation updates, no breaking changes
- **MINOR (0.x.0):** New features, new utilities, backward compatible
- **MAJOR (x.0.0):** Breaking changes to APIs or package structure

**Dev versions:** Use `-dev` suffix (e.g., `0.1.1-dev`) for testing unpublished changes

## Related Documentation

- **Issue #373:** Package Distribution Strategy  
- **Issue #374:** GitHub Packages Setup (this implementation)
- **Testing Guide:** `docs/operations/TESTING.md`
- **GitHub Container Registry Docs:** https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
