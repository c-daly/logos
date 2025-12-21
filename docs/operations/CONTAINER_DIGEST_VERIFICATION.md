# Container Digest Verification Design

> **Tracking Issue:** [#425](https://github.com/c-daly/logos/issues/425)

## Overview

This document describes a proposed container digest verification system for the LOGOS ecosystem. The goal is to ensure that containers pulled by downstream services match exactly what was published, providing integrity guarantees across the dependency chain.

## Background

### Why Container-Based Distribution?

The LOGOS ecosystem consists of five independent repositories: logos, sophia, hermes, apollo, and talos. Early iterations attempted to share code via path dependencies (`{path = "../logos"}`) or git dependencies in pyproject.toml. This approach had fundamental problems:

1. **CI Breakage**: Path dependencies don't exist in CI environments, requiring complex custom checkout logic
2. **Repository Coupling**: Changes in one repo would immediately affect all others, making independent development impossible
3. **Version Ambiguity**: No clear way to pin versions or roll back to known-good states
4. **Coordination Overhead**: Every cross-repo change required synchronized commits across multiple repos

The solution was to treat each repository as a **publisher of artifacts** rather than a source dependency. Each repo builds and publishes a Docker container to GitHub Container Registry (GHCR). Other repos consume these containers, not source code.

### How the Container System Works

#### Base Image: logos-foundry

The `logos` repository publishes `ghcr.io/c-daly/logos-foundry`, a base image containing:
- All shared logos packages (logos_hcg, logos_test_utils, logos_observability, etc.)
- Python 3.11 with Poetry
- All common dependencies pre-installed

This image is built from `Dockerfile.foundry` and published via `.github/workflows/publish-package.yml`.

#### Service Containers

Each service repository (sophia, hermes, apollo, talos) builds its own container:

```dockerfile
# sophia/Dockerfile
FROM ghcr.io/c-daly/logos-foundry:0.1.0

WORKDIR /app/sophia
COPY src/ ./src/
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main
# ...
```

The service inherits everything from logos-foundry and layers its own code on top. This provides:
- **Isolation**: Each service is a self-contained artifact
- **Reproducibility**: Same image runs in dev, CI, and production
- **Speed**: Base image is cached; only service layer rebuilds

#### Service Dependencies at Runtime

Services don't import each other's code—they communicate via HTTP/REST at runtime. Docker-compose files define the service topology:

```yaml
services:
  sophia:
    image: ghcr.io/c-daly/sophia:${SOPHIA_IMAGE_TAG:-latest}
    
  hermes:
    image: ghcr.io/c-daly/hermes:${HERMES_IMAGE_TAG:-latest}
    environment:
      - SOPHIA_URL=http://sophia:8000
    depends_on:
      - sophia
```

This keeps repositories independent:
- Sophia doesn't know hermes exists at build time
- Hermes just needs a running Sophia service at a URL
- Either can be updated, versioned, and deployed independently

#### Local Development

For local development, git dependencies in pyproject.toml allow `poetry install` to resolve logos packages without the container:

```toml
logos-foundry = {git = "https://github.com/c-daly/logos.git", branch = "main"}
```

This is a **fallback for development convenience**, not the production distribution path. In CI and production, the container provides everything.

### Current Distribution Model

1. **logos** publishes `ghcr.io/c-daly/logos-foundry` when shared libs change
2. **Each service repo** builds FROM logos-foundry, publishes its own container
3. **Docker-compose files** reference service containers by image tag
4. **Template rendering** (`render_test_stacks.py`) generates test compose files
5. **Git dependencies** exist for local dev but aren't used in containers

## Problem Statement

Currently, there's no verification that a pulled container matches what was published. A mismatch could occur due to:
- Tag mutation (`:latest` pointing to different image)
- Registry issues
- Man-in-the-middle attacks
- Build reproducibility failures

## Proposed Solution

### Core Concept: Digest Registry

Each repo maintains a registry of known-good container digests for its dependencies. When pulling a container, the digest is verified against this registry.

### Distribution Repository

A dedicated distribution repository holds:
```
dist-repo/
  digests/
    logos-foundry.digest
    sophia.digest
    hermes.digest
    apollo.digest
    talos.digest
```

Each digest file contains the current valid digest for that container.

### Workflow

#### 1. Publish (in each repo's publish workflow)

```
Build container → Push to GHCR → Capture digest → Push to dist repo
```

The publish workflow:
1. Builds and pushes the container
2. Captures the digest from the push step
3. Writes the digest to the dist repo
4. Fires `repository_dispatch` to notify downstream repos

#### 2. Template Rendering (triggered by dispatch)

When a new digest is available:
1. Each downstream repo receives the dispatch event
2. Pulls the updated digest(s) from the dist repo  
3. Renders templates (docker-compose, etc.) with the new digest(s)
4. Commits the updated files

#### 3. Build Verification

When a downstream repo builds its container:
1. The expected digest is embedded in the container filesystem (during template render)
2. At build time, verify the pulled base image matches the expected digest
3. Fail the build if mismatch

#### 4. Runtime Verification

When starting services (docker-compose up, k8s deploy):
1. Compare pulled image digest to the expected digest from the registry
2. If match, append to known-good list and mark as current
3. If mismatch, fail startup

### Digest File Format

Simple single-line format:
```
sha256:abc123def456...
```

No history needed - if restoring an old image, manually update the digest file.

### Operations

| Operation | Description |
|-----------|-------------|
| **Publish** | Normal flow - build, push, record digest |
| **Fetch** | Pull specific container by digest |
| **Restore** | Manually set digest to an older known-good value |
| **Delete** | Remove a digest from known-good list (cleanup) |

## Implementation Steps

### Step 1: Digest Capture in Publish Workflows

Add `id: build` to docker/build-push-action to capture digest output:
```yaml
- name: Build and push container
  id: build
  uses: docker/build-push-action@v5
  # ...

- name: Output digest
  run: echo "Digest: ${{ steps.build.outputs.digest }}"
```

### Step 2: Distribution Repository Setup

Create a repo (or branch) to hold digest files:
- Simple file structure
- Each repo has write access to its own digest file
- All repos have read access to all digests

### Step 3: Push Digest After Publish

Add step to publish workflows:
```yaml
- name: Update digest in dist repo
  run: |
    echo "${{ steps.build.outputs.digest }}" > digests/myrepo.digest
    # commit and push to dist repo
```

### Step 4: Repository Dispatch

Notify downstream repos when digest changes:
```yaml
- name: Notify downstream
  run: |
    curl -X POST \
      -H "Authorization: token ${{ secrets.REPO_TOKEN }}" \
      https://api.github.com/repos/c-daly/sophia/dispatches \
      -d '{"event_type": "digest-updated", "client_payload": {"repo": "logos-foundry", "digest": "${{ steps.build.outputs.digest }}"}}'
```

### Step 5: Template Rendering with Digests

Update `render_test_stacks.py` to:
1. Read digest files from dist repo (or local checkout)
2. Inject digests into rendered docker-compose files
3. Generate Dockerfile FROM lines with digest pinning

### Step 6: Build-time Verification

In Dockerfiles or build scripts, verify base image digest before proceeding.

### Step 7: Runtime Verification

Add verification step to test scripts and deployment tooling.

## Open Questions

1. **Dist repo structure**: Separate repo vs branch in logos?
2. **Authentication**: How do downstream repos authenticate to push their digests?
3. **Rollback procedure**: How to handle failed digest verification?
4. **CI/CD timing**: How to handle the delay between publish and digest propagation?
5. **Local development**: How does this affect local dev workflow?

## Related Issues

- [#373](https://github.com/c-daly/logos/issues/373) - Package Distribution Strategy (closed, established container model)
- [#374](https://github.com/c-daly/logos/issues/374) - logos: Set up package publishing (closed)
- [#423](https://github.com/c-daly/logos/issues/423) - Cross-repo package distribution automation

## References

- [Docker Content Trust](https://docs.docker.com/engine/security/trust/)
- [OCI Image Digest](https://github.com/opencontainers/image-spec/blob/main/descriptor.md#digests)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
