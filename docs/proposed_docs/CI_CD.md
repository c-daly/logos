# CI/CD

## Overview

Every LOGOS repo uses GitHub Actions with two types of workflows:

1. **CI** — lint, type check, test (runs on every push/PR to `main`)
2. **Publish** — build and push Docker image to `ghcr.io` (runs on push to `main`)

## Reusable Workflow

Most repos delegate CI to a shared workflow in the logos repo:

```yaml
uses: c-daly/logos/.github/workflows/reusable-standard-ci.yml@main
```

This provides:
- Python setup (Poetry install, virtualenv caching)
- Ruff lint + Black format check
- mypy type checking
- pytest execution
- Optional Docker Compose for test infrastructure
- Optional Node.js lint/test/build
- Coverage upload to Codecov

Repos customize behavior through `with:` inputs (Python versions, lint paths, compose files, etc.).

## How CI Works for Each Repo

### Simple repos (sophia, hermes, talos)

```
push to main
  → checkout
  → poetry install
  → ruff + black + mypy
  → pytest (unit tests only, or with test stack)
  → upload coverage
```

### Apollo (most complex)

```
push to main
  → checkout
  → docker compose up (Neo4j, Milvus, Sophia container, Hermes container, Apollo container)
  → wait for all services healthy
  → poetry install
  → ruff + black + mypy
  → pytest (all tests, including integration)
  → npm ci + lint + type-check + test + build (webapp)
  → Playwright E2E tests
```

Apollo's CI depends on published Docker images for sophia and hermes. If those images are broken, apollo CI fails even if apollo's code is fine.

## Container Publishing

Each repo with a service has a `publish.yml` workflow:

```
push to main
  → build Docker image
  → push to ghcr.io/c-daly/<repo>:latest
  → tag with commit SHA
```

Images are published to:
- `ghcr.io/c-daly/sophia:latest`
- `ghcr.io/c-daly/hermes:latest`
- `ghcr.io/c-daly/apollo:latest`

### Hermes ML Image

Hermes has two image variants:
- Standard: `ghcr.io/c-daly/hermes:latest`
- ML (with whisper, TTS, spaCy): `ghcr.io/c-daly/hermes:ml-latest`

The ML build takes longer due to large model dependencies.

## Version Propagation

When you change `logos_config`:

```
1. Commit to logos, tag (e.g., v0.4.2)
2. Push tag: git push origin v0.4.2
3. In each downstream repo:
   - Update pyproject.toml: tag = "v0.4.2"
   - poetry update logos-foundry
   - git push
4. CI runs → installs new logos_config → tests pass (hopefully)
5. Publish workflow → new Docker image with updated logos_config
```

If you skip step 3 for a repo, its CI will keep using the old tag and its Docker image will have stale config.

## Debugging CI Failures

### "Start test services" fails

The Docker Compose step failed. Common causes:
- A service container image is broken (check if hermes/sophia published recently)
- Port conflict with another running test stack
- Docker pull rate limiting

Check logs:
```bash
gh run view <run-id> --job <job-id> --log
```

### "Wait for services" times out

Infrastructure started but a service never became healthy.
```bash
# Check which service timed out (look at the last "Waiting for..." line)
gh run view <run-id> --log | grep "Waiting for"
```

Common causes:
- Service crashes on startup (stale `logos_config` in the image — check Dockerfile base image version)
- Neo4j or Milvus takes too long to initialize (increase timeout)
- Service can't connect to its dependencies (wrong port in compose env vars)

### Tests fail but pass locally

- Local dev uses shared ports (7687); CI uses offset ports (27687)
- CI installs from `poetry.lock` which may pin a different `logos_config` than your local env
- CI runs all tests including integration; you may only run unit tests locally

### Container publish fails

- Check that the Dockerfile builds locally: `docker build -t test .`
- Verify the base image tag matches what's published (e.g., `logos-foundry:0.4.1`)
- Check GHCR authentication (repo secrets)

## Useful Commands

```bash
# List recent CI runs
gh run list --limit 10

# View a specific run
gh run view <run-id>

# Get failed step logs
gh run view <run-id> --log-failed

# Re-run a failed workflow
gh run rerun <run-id>

# Check container image details
docker pull ghcr.io/c-daly/hermes:latest
docker inspect ghcr.io/c-daly/hermes:latest | grep -i version
```
