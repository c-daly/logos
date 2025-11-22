# CI/CD Inventory and Consolidation

This document outlines the state of CI/CD workflows across the LOGOS repositories following the consolidation effort (Issue #32).

## Goal
Establish consistent testing and linting standards across all repositories using a shared reusable workflow, while accommodating specific integration testing needs.

## Shared Infrastructure
All repositories now utilize the reusable workflow defined in `c-daly/logos/.github/workflows/reusable-standard-ci.yml`. This workflow provides:
- Python setup and dependency installation (Poetry or Pip)
- Linting (Ruff)
- Formatting checks (Black)
- Type checking (MyPy)
- Unit testing (Pytest with coverage)
- Optional Node.js/Webapp testing

## Repository Status

### Apollo
- **Workflow**: `.github/workflows/ci.yml`
- **Type**: Hybrid (Python + Node.js)
- **Configuration**:
  - Uses reusable workflow for Python backend (FastAPI).
  - Uses reusable workflow's `node-ci` job for React webapp.
  - **Changes**: Merged `phase2-apollo-web.yml` into `ci.yml`.

### Sophia
- **Workflow**: `.github/workflows/ci.yml`
- **Type**: Python (Poetry)
- **Configuration**:
  - Standard Python CI configuration.
  - **Status**: Already compliant.

### Hermes
- **Workflow**: `.github/workflows/ci.yml`
- **Type**: Python (Poetry) + Integration Services
- **Configuration**:
  - Uses reusable workflow for standard checks.
  - Defines a custom `integration-test` job using `docker compose` to spin up Milvus, Etcd, MinIO, and Neo4j.
  - **Changes**: Merged `phase2-hermes-service.yml` into `ci.yml`, standardized on `docker compose` for integration tests.

### Talos
- **Workflow**: `.github/workflows/ci.yml`
- **Type**: Python (Poetry)
- **Configuration**:
  - Standard Python CI configuration.
  - **Status**: Already compliant.

### Logos (Foundry)
- **Workflow**: `.github/workflows/ci.yml` (renamed from `test.yml`)
- **Type**: Python (Poetry) + Monorepo
- **Configuration**:
  - Uses reusable workflow for standard checks across all packages in the root.
  - Retains specialized workflows (`phase2-perception.yml`, `phase2-otel.yml`) for specific validation tasks (Ontology, OTel config).
  - **Changes**: Renamed `test.yml` to `ci.yml`, switched to Poetry, enabled MyPy.

## Future Recommendations
- **Release Workflow**: Standardize the release/publish workflow (currently `build` job exists in Hermes, but not others).
- **Integration Tests**: Consider moving Hermes' integration test logic into a reusable composite action if other repos need similar vector DB setups.
