# Standard CI Workflow Template

> Tracks LOGOS issue #294 (CI parity: define standard workflow + template)

The reusable workflow in `.github/workflows/reusable-standard-ci.yml` encapsulates the baseline that every LOGOS repo should run on every PR:

- **Python lint + unit tests** (Ruff, Black, mypy, pytest with coverage)
- **Optional Node/Vite job** for Apollo’s webapp (npm lint → type-check → test → build)
- **Optional integration job** for docker-compose or end-to-end harnesses once the unit jobs succeed

## Default behavior

| Concern | Default |
| --- | --- |
| Python versions | `['3.11']` matrix before pytest
| Dependency manager | `pip` with `pip install -e .[dev]`
| Linting | Ruff + Black against `src tests`
| Type checking | `mypy src`
| Tests | `pytest --cov --cov-report=term --cov-report=xml`
| Coverage upload | Codecov upload from the Python 3.11 run when `CODECOV_TOKEN` is provided |
| Node job | Disabled unless `enable_node: true`
| Integration job | Disabled unless `enable_integration_job: true`

Switching to Poetry or enabling Node/E2E requires only input overrides—no copy/pasted workflows.

## Inputs

| Input | Type | Notes |
| --- | --- | --- |
| `python_versions` | JSON string | e.g. `'["3.11","3.12"]'`
| `python_package_manager` | `pip`/`poetry` | Picks caching + install flow
| `python_install_command` | string | Pip install script (ignored when using Poetry)
| `python_command_prefix` | string | Prefix CLI commands (`"poetry run "`)
| `poetry_install_args` | string | Forwarded to `poetry install`
| `python_lint_paths`, `mypy_targets` | string | Space-separated targets
| `pytest_command` | string | Custom pytest invocation
| `upload_coverage`, `coverage_python_version` | bool/string | Choose Codecov uploader run
| `enable_node`, `node_*` inputs | bool/string | Control webapp job (dir, commands, Node ver.)
| `enable_integration_job` | bool | Adds an extra job using `integration_command`
| `integration_needs_python` | bool | Whether the integration job waits for the Python job
| `working_directory` | string | Root for Python steps

See the workflow file for every available input; anything omitted falls back to the defaults in the table above.

## Example usage

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
      node_cache_path: 'webapp/package-lock.json'
      enable_integration_job: true
      integration_name: 'Apollo E2E harness'
      integration_command: |
        cd tests/e2e
        python test_e2e_flow.py
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Badge snippet

Once a repo adopts the template, add a badge referencing its local CI workflow (usually `ci.yml`):

```
[![CI](https://github.com/c-daly/apollo/actions/workflows/ci.yml/badge.svg)](https://github.com/c-daly/apollo/actions/workflows/ci.yml)
```

Update repository READMEs to include the badge and describe any repo-specific overrides.
