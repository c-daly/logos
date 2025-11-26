# CI/CD Documentation

This directory contains documentation for the shared CI/CD infrastructure across all LOGOS repositories.

## Overview

All LOGOS repositories use a shared reusable workflow defined in `c-daly/logos/.github/workflows/reusable-standard-ci.yml`. This provides consistent testing and linting standards while accommodating repository-specific needs.

**Related Issues:** #32 (consolidation), #293 (inventory), #294 (template), #295 (badges)

---

## Shared Workflow Features

The reusable workflow provides:
- Python setup and dependency installation (Poetry or Pip)
- Linting (Ruff) and formatting checks (Black)
- Type checking (MyPy)
- Unit testing (Pytest with coverage)
- Optional Node.js/Webapp testing
- Optional integration test job

### Default Behavior

| Concern | Default |
|---------|---------|
| Python versions | `['3.11']` matrix |
| Dependency manager | `pip` with `pip install -e .[dev]` |
| Linting | Ruff + Black against `src tests` |
| Type checking | `mypy src` |
| Tests | `pytest --cov --cov-report=term --cov-report=xml` |
| Coverage upload | Codecov upload from Python 3.11 run when `CODECOV_TOKEN` provided |
| Node job | Disabled unless `enable_node: true` |
| Integration job | Disabled unless `enable_integration_job: true` |

### Workflow Inputs

| Input | Type | Notes |
|-------|------|-------|
| `python_versions` | JSON string | e.g. `'["3.11","3.12"]'` |
| `python_package_manager` | `pip`/`poetry` | Picks caching + install flow |
| `python_command_prefix` | string | Prefix CLI commands (`"poetry run "`) |
| `poetry_install_args` | string | Forwarded to `poetry install` |
| `python_lint_paths`, `mypy_targets` | string | Space-separated targets |
| `pytest_command` | string | Custom pytest invocation |
| `upload_coverage`, `coverage_python_version` | bool/string | Codecov uploader config |
| `enable_node`, `node_*` inputs | bool/string | Control webapp job |
| `enable_integration_job` | bool | Adds extra job using `integration_command` |

---

## Repository Status

| Repo | Workflow | Type | Lint | Type Check | Unit | Integration | E2E | Coverage |
|------|----------|------|------|------------|------|-------------|-----|----------|
| **logos** | `ci.yml` | Python (Poetry) + Monorepo | ✅ Ruff | ✅ mypy | ✅ Pytest | ✅ Phase 2 pipelines | ✅ M4 flow | ⚠️ XML artifact |
| **apollo** | `ci.yml` | Hybrid (Python + Node.js) | ✅ Ruff/Black + npm | ✅ mypy + TS | ✅ Pytest + Vitest | ✅ CLI E2E harness | ✅ | ✅ Codecov |
| **sophia** | `ci.yml` | Python (Poetry) | ✅ Black/Ruff | ❌ | ✅ Pytest | ❌ | ❌ | ✅ Codecov |
| **hermes** | `ci.yml` | Python (Poetry) + Services | ✅ Ruff/Black | ✅ mypy | ✅ Pytest | ⚠️ Optional | ❌ | ✅ Codecov |
| **talos** | `ci.yml` | Python (Poetry) | ✅ Ruff/Black | ✅ mypy | ✅ Pytest | ❌ | ❌ | ✅ Codecov |

Legend: ✅ = covered, ⚠️ = partially covered / optional, ❌ = not covered

---

## Example Usage

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  standard:
    uses: c-daly/logos/.github/workflows/reusable-standard-ci.yml@main
    with:
      python_versions: '["3.11","3.12"]'
      python_package_manager: 'poetry'
      python_command_prefix: 'poetry run '
      poetry_install_args: '--with dev --all-extras'
      enable_node: true
      node_working_directory: 'webapp'
      enable_integration_job: true
      integration_name: 'E2E harness'
      integration_command: |
        cd tests/e2e
        python test_e2e_flow.py
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Badge Snippet

```markdown
[![CI](https://github.com/c-daly/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/c-daly/REPO/actions/workflows/ci.yml)
```

---

## Known Gaps

### Sophia
- No mypy despite pervasive type hints
- Integration tests not wired into CI

### Hermes
- Integration coverage optional on PRs

### Talos
- Workflow triggers only watch `main`
- No integration tests for shim/hardware abstractions

### Cross-Repo
- No system-level E2E linking all services
- Coverage reporting inconsistent across repos

---

## Related Documentation

- [Testing Standards](../TESTING.md) - Guidelines for writing tests
- [Observability Queries](../OBSERVABILITY_QUERIES.md) - TraceQL queries for debugging
