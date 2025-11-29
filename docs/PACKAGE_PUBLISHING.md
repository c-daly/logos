# Package Publishing Guide

This document describes how to publish and consume the `logos-foundry` package using GitHub Packages.

## Overview

`logos-foundry` is published to GitHub Packages (GitHub's PyPI-compatible package registry) to enable other LOGOS repositories to consume shared utilities without path dependencies.

**Package Name:** `logos-foundry`  
**Current Version:** `0.1.0`  
**Registry:** `https://pypi.pkg.github.com/c-daly`

## Publishing New Versions

### Automatic Publishing (Recommended)

1. **Update version in `pyproject.toml`:**
   ```bash
   # Bump version following semver: MAJOR.MINOR.PATCH
   # Edit pyproject.toml manually or use:
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
   - Package appears at: https://github.com/c-daly/logos/packages

### Manual Publishing

If you need to publish without creating a release:

1. **Trigger workflow manually:**
   - Go to https://github.com/c-daly/logos/actions/workflows/publish-package.yml
   - Click "Run workflow"
   - Select branch (usually `main`)
   - Click "Run workflow"

2. **Or publish locally:**
   ```bash
   # Configure authentication (one-time)
   poetry config http-basic.github YOUR_GITHUB_USERNAME YOUR_PERSONAL_ACCESS_TOKEN
   
   # Build and publish
   poetry build
   poetry publish -r github
   ```

## Consuming from GitHub Packages

### For Poetry Projects (Recommended)

1. **Add GitHub Packages as a source in `pyproject.toml`:**
   ```toml
   [[tool.poetry.source]]
   name = "github"
   url = "https://pypi.pkg.github.com/c-daly"
   priority = "supplemental"  # Check PyPI first, fall back to GitHub
   ```

2. **Add the dependency:**
   ```toml
   [tool.poetry.dependencies]
   logos-foundry = "^0.1.0"
   ```

3. **Configure authentication:**
   ```bash
   # One-time setup
   poetry config http-basic.github YOUR_GITHUB_USERNAME YOUR_PERSONAL_ACCESS_TOKEN
   ```

4. **Install:**
   ```bash
   poetry install
   ```

### For pip Projects

```bash
# Set up authentication
export PIP_INDEX_URL=https://pypi.org/simple/
export PIP_EXTRA_INDEX_URL=https://pypi.pkg.github.com/c-daly/

# Install with authentication
pip install \
  --index-url https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@pypi.pkg.github.com/c-daly/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  logos-foundry==0.1.0
```

## Authentication

### Creating a Personal Access Token

1. Go to https://github.com/settings/tokens/new
2. Set description: "logos-foundry package access"
3. Select scopes:
   - `read:packages` (required for consuming)
   - `write:packages` (required for publishing)
4. Generate token and save it securely

### For CI/CD (GitHub Actions)

GitHub Actions automatically has access via `GITHUB_TOKEN`:

```yaml
- name: Configure Poetry for GitHub Packages
  run: |
    poetry config repositories.github https://pypi.pkg.github.com/c-daly
    poetry config http-basic.github __token__ ${{ secrets.GITHUB_TOKEN }}

- name: Install dependencies
  run: poetry install
```

## Local Development Workflow

When working on changes to `logos-foundry` that need testing in dependent repos:

### Option 1: Path Override (Temporary)

```bash
cd dependent-repo

# Use local version
poetry add ../logos

# Work on changes, test...

# Revert to published version
poetry add logos-foundry@^0.1.0
```

### Option 2: Editable Install

```bash
cd dependent-repo

# Install logos-foundry in editable mode
pip install -e ../logos

# Changes in ../logos are immediately reflected
# Remember to uninstall before switching back:
pip uninstall logos-foundry
poetry install  # Reinstall from lock file
```

### Option 3: Local Build and Install

```bash
cd logos
poetry build

cd ../dependent-repo
pip install ../logos/dist/logos_foundry-0.1.0-py3-none-any.whl
```

## Package Contents

`logos-foundry` includes the following sub-packages:

- **`logos_tools`** - CLI tools for issue generation and management
- **`logos_hcg`** - Hybrid Cognitive Graph data structures and utilities
- **`logos_observability`** - OpenTelemetry instrumentation and logging
- **`logos_persona`** - Persona diary and emotional state models
- **`logos_cwm_e`** - Causal World Model - Emotional layer
- **`logos_perception`** - Perception and media ingestion utilities
- **`logos_sophia`** - Sophia-specific utilities
- **`logos_test_utils`** - Shared test fixtures and utilities
- **`planner_stub`** - Planning stub implementations

### Using Test Utilities

To use `logos_test_utils` in consuming repos:

```python
# In conftest.py or test files
from logos_test_utils import (
    get_neo4j_config,
    get_milvus_config,
    cleanup_neo4j,
    cleanup_milvus,
)

# Neo4j fixture using shared utilities
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

**Note:** Consuming repos must declare test dependencies themselves or install with extras if `logos_test_utils` requires them (neo4j, pymilvus, etc.).

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

### Package not found

**Error:** `Package logos-foundry not found`

**Solutions:**
1. Verify GitHub Packages source is configured in `pyproject.toml`
2. Check authentication is set up correctly
3. Ensure the package version exists: https://github.com/c-daly/logos/packages

### Authentication failed

**Error:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**
1. Verify your Personal Access Token has `read:packages` scope
2. Re-run: `poetry config http-basic.github USERNAME TOKEN`
3. For CI, ensure `GITHUB_TOKEN` has `packages: read` permission

### Wrong package version installed

**Error:** Getting an old version despite specifying newer one

**Solutions:**
1. Clear Poetry cache: `poetry cache clear github --all`
2. Force update: `poetry update logos-foundry`
3. Check your version constraint in `pyproject.toml`

### Local changes not reflected

If you're using path dependencies and changes aren't reflected:

```bash
# Force reinstall
poetry install --no-cache
# Or
pip install --force-reinstall -e ../logos
```

## Related Documentation

- **Issue #373:** Package Distribution Strategy
- **Issue #374:** GitHub Packages Setup (this implementation)
- **Testing Guide:** `docs/operations/TESTING.md`
- **GitHub Packages Docs:** https://docs.github.com/en/packages
