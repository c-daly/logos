# Contributing to Project LOGOS

Thank you for your interest in contributing to Project LOGOS! This document provides guidelines for contributing to the LOGOS ecosystem.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct (see `CODE_OF_CONDUCT.md`). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

Project LOGOS is a foundational research initiative building a non-linguistic cognitive architecture for autonomous agents. The system uses a Hybrid Causal Graph (HCG) for knowledge representation.

### Repository Structure

This is the LOGOS meta-repository, which serves as the canonical source of truth:

- `/docs/spec/` - Formal specifications and design documents
- `/docs/phase1/`, `/docs/phase2/` - Phase-specific specifications
- `/ontology/` - HCG ontology definition and validation constraints
- `/contracts/` - API contracts in OpenAPI format
- `/infra/` - Development infrastructure (Docker Compose configurations)
- `/tests/` - Integration tests for HCG and milestone verification

### Ecosystem Components

LOGOS consists of five main repositories:

1. **LOGOS** (this repo) - Foundry and canonical source of truth
2. **Sophia** (`c-daly/sophia`) - Non-linguistic cognitive core
3. **Hermes** (`c-daly/hermes`) - Language & embedding utilities
4. **Talos** (`c-daly/talos`) - Hardware abstraction layer
5. **Apollo** (`c-daly/apollo`) - Client UI and command layer

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11 or higher
- Git
- At least 4GB RAM allocated to Docker

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/c-daly/logos.git
   cd logos
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Start the HCG infrastructure:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml up -d
   ```

4. **Load the core ontology:**
   ```bash
   ./infra/load_ontology.sh
   ```

5. **Run tests:**
   ```bash
   pytest
   ```

For detailed setup instructions, see `DEVELOPMENT.md` and `README.md`.

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues in the codebase
- **Features** - Implement new capabilities aligned with the project roadmap
- **Documentation** - Improve or expand documentation
- **Tests** - Add or improve test coverage
- **Ontology extensions** - Extend the HCG ontology for new domains
- **Research** - Contribute research findings or experimental features

### Finding Issues to Work On

- Check the [GitHub Issues](https://github.com/c-daly/logos/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Review the phase specifications in `/docs/phase1/` and `/docs/phase2/`
- Check the project board for current priorities

### Reporting Bugs

When reporting bugs, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Your environment (OS, Docker version, Python version)
- Relevant logs or error messages
- Screenshots if applicable

### Suggesting Enhancements

For feature requests or enhancements:

- Check if the feature aligns with the project's non-linguistic cognition philosophy
- Review existing phase specifications to see if it's already planned
- Describe the use case and expected behavior
- Consider how it fits into the HCG architecture

## Pull Request Process

### Before Submitting

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following the coding standards**

3. **Run tests and validation:**
   ```bash
   pytest
   ./scripts/validate_artifacts.sh  # If modifying ontology or contracts
   ```

4. **Update documentation** if your changes affect user-facing behavior

5. **Commit your changes** with clear, descriptive messages

### Submitting a Pull Request

1. Push your branch to your fork
2. Create a pull request against the `main` branch
3. Fill out the pull request template with:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Documentation updates

### PR Review Process

- Maintainers will review your PR within a few days
- Automated tests must pass (GitHub Actions workflows)
- At least one maintainer approval is required
- Address any requested changes
- Once approved, a maintainer will merge your PR

### Issue & PR Templates (enforced)

This repository provides templates to standardize issue reports and pull requests. Use them to ensure fast triage and smoother reviews.

- Issue template: `logos/.github/ISSUE_TEMPLATE.md` — includes sections for a short, bracketed title (`[COMPONENT] short-summary`), reproduction steps, proposed change, acceptance criteria, environment, and suggested labels.
- PR template: `logos/.github/PULL_REQUEST_TEMPLATE.md` — includes a required link to the related issue (use `Closes #<issue-number>` when the PR resolves it), a checklist for tests/lint/docs, and exact commands to run locally.

Examples:
- Issue title: `[apollo] Add mock fixture for chat panel (#1234)`
- PR description: include `Closes #1234`, a short summary, files changed list, and a `How to run / test locally` section with copyable commands.

Maintainers will expect the checklist in the PR template to be completed before merging. Use the workspace `logos/.github/copilot-instructions.md` for full GitHub/ticketing rules (labels, branch naming, status labels, etc.).

## Coding Standards

### CI/CD Standards

All LOGOS repositories follow standardized CI/CD patterns for consistency and maintainability.

#### Standard CI Workflow

All repos use the reusable CI workflow at `c-daly/logos/.github/workflows/reusable-standard-ci.yml`:

```yaml
# Example ci.yml for a LOGOS repo
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    uses: c-daly/logos/.github/workflows/reusable-standard-ci.yml@main
    with:
      python_package_manager: poetry
      run_ruff: true
      run_black: true
      run_mypy: true
      run_pytest: true
      pytest_command: 'pytest --cov --cov-report=term --cov-report=xml -m "not requires_torch"'
      upload_coverage: true
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

**Key inputs:**
- `python_package_manager`: `poetry` or `pip`
- `run_ruff`, `run_black`, `run_mypy`, `run_pytest`: Enable/disable linting steps
- `pytest_command`: Customize pytest invocation (e.g., exclude GPU tests)
- `enable_node`: Set `true` for repos with webapp/ (e.g., Apollo)
- `docker_compose_file`: Path to test infrastructure compose file

#### Publish Workflow

All repos use the reusable workflow at `c-daly/logos/.github/workflows/reusable-publish.yml`:

```yaml
# Example publish.yml for a LOGOS repo
name: Publish Container

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Dockerfile'
      - 'pyproject.toml'
      - 'poetry.lock'
  release:
    types: [published]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

jobs:
  publish:
    uses: c-daly/logos/.github/workflows/reusable-publish.yml@main
    with:
      image_name: <repo-name>  # sophia, hermes, apollo, talos
    secrets: inherit
```

**Standard triggers** (all repos must have):
- `push: branches: [main]` with path filters for source changes
- `release: types: [published]`
- `workflow_dispatch` for manual runs

#### Port Allocation

Each service has a designated port range to avoid conflicts:

| Service | Port Range | Example Ports |
|---------|------------|---------------|
| Hermes  | 1xxxx      | 10000, 10001  |
| Apollo  | 2xxxx      | 20000, 20080  |
| Logos   | 3xxxx      | 30000         |
| Sophia  | 4xxxx      | 40000, 40080  |
| Talos   | 5xxxx      | 50000         |

See `config/repos.yaml` for the canonical port assignments.

#### SDK Dependencies

For repos that depend on LOGOS SDKs (e.g., Apollo):

```toml
# Preferred: use branch reference for latest
logos-sophia-sdk = {git = "https://github.com/c-daly/logos.git", branch = "main", subdirectory = "sdk/python/sophia"}

# Alternative: pinned revision for stability
logos-sophia-sdk = {git = "https://github.com/c-daly/logos.git", rev = "abc123...", subdirectory = "sdk/python/sophia"}
```

When using pinned revisions, update them regularly or configure Dependabot/Renovate.

### Python Code

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Keep functions focused and concise
- Use descriptive variable names

### Cypher Scripts

- Include file header comments with purpose and spec reference
- Use descriptive constraint and relationship names
- Group related constraints together
- End scripts with meaningful RETURN statements

### YAML Files (OpenAPI, Docker Compose)

- Use 2-space indentation
- Include inline comments for complex configurations
- Maintain alphabetical ordering where logical

### Ontology Contributions

When modifying the HCG ontology:

- Follow existing patterns in `ontology/core_ontology.cypher`
- Maintain causal coherence in relationships
- Update SHACL shapes in `ontology/shacl_shapes.ttl` accordingly
- Reference specification sections in comments
- Add tests to verify your ontology changes

## Testing Guidelines

### Test Requirements

- All new features must include tests
- Tests should be consistent with existing test patterns
- Integration tests go in `tests/integration/`; cross-service E2E suites live in `tests/e2e/`
- Use fixtures for common test data

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/integration/ontology/test_neo4j_crud.py

# Run with coverage
pytest --cov=logos_hcg --cov=logos_tools
```

### Test Categories

- **Unit tests** - Test individual components
- **Integration tests** - Test component interactions
- **Milestone tests** - Verify milestone acceptance criteria (M1-M4)
- **End-to-end tests** - Test complete workflows

### Phase 2 E2E Testing Requirements

All PRs affecting Phase 2 functionality should ensure Phase 2 E2E tests pass:

1. **Run Phase 2 E2E tests locally before submitting PR:**
   ```bash
   # Start/stop the shared stack
   ./tests/e2e/run_e2e.sh up
   RUN_P2_E2E=1 pytest tests/e2e/test_phase2_end_to_end.py -v
   ./tests/e2e/run_e2e.sh down
   ```

2. **Phase 2 E2E tests automatically run in CI** on all PRs affecting:
   - `logos/**`
   - `sophia/**`
   - `hermes/**`
   - `apollo/**`

3. **Test coverage expectations:**
   - Service health checks must pass
   - CWMState contract validation must pass
   - Cross-service integration tests must pass
   - Blocked tests (media, OTel, browser) can be skipped with proper `@pytest.mark.skip()` annotations

4. **When adding new Phase 2 features:**
   - Add corresponding E2E tests to `tests/e2e/test_phase2_end_to_end.py`
   - Update test fixtures in `tests/e2e/fixtures.py` if needed
   - Document new tests in `tests/e2e/README.md`
   - If feature is blocked by another issue, use `@pytest.mark.skip(reason="Blocked by logos#XXX")`

See `tests/e2e/README.md` for detailed testing documentation.

## Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples where appropriate
- Reference specification sections explicitly
- Update the relevant service README if your changes affect setup or usage and link back to the canonical doc in `docs/`
- Add Architecture Decision Records (ADRs) for significant design choices
- Avoid creating standalone files that only restate tickets—keep substantive content in the consolidated doc tree

### Documentation Locations

- **Documentation guide**: `docs/README.md` (authoritative structure + navigation links)
- **Architecture overviews**: `docs/architecture/`
- **HCG ontology & CWM specs**: `docs/hcg/`
- **Service-specific docs**: `docs/services/<service>/`
- **Operations / verification**: `docs/operations/`
- **Reference contracts & SDK notes**: `docs/reference/` (linked from `contracts/` and `sdk/`)

When adding or updating documentation:

1. Pick the appropriate directory from the list above (or propose a new one via issue if it truly does not fit).
2. Link the new doc from the local `index.md`/README and, if applicable, the service README in the owning repo.
3. Remove or update older files that duplicated the same content.
4. Mention the doc changes in your PR so reviewers can verify navigation updates.

## Community

### Communication Channels

- **GitHub Issues**: For bug reports, feature requests, and task tracking
- **Pull Requests**: For code review and technical discussions
- **Discussions**: For general questions and community engagement

### Getting Help

- Review the documentation in `/docs/`
- Check existing issues for similar problems
- Ask questions in GitHub Discussions
- Reach out to maintainers if you need guidance on contributions

## Project Philosophy

Keep in mind LOGOS's core principles when contributing:

- **Non-linguistic cognition first**: Internal reasoning uses causal graph structures, not language
- **Language as interface**: Natural language is an I/O modality, not the substrate of thought
- **Causal coherence**: All reasoning maintains explicit causal relationships
- **Validation by constraint**: Multi-level validation ensures logical consistency
- **Flexibility**: Support various deployment modes from graph-only to physical embodiment

## Recognition

Contributors will be recognized in:

- GitHub contributor graphs
- Release notes for significant contributions
- The project's acknowledgments section

## Questions?

If you have questions about contributing, please:

1. Check the documentation
2. Search existing issues
3. Open a new issue with the `question` label
4. Reach out to maintainers

Thank you for contributing to Project LOGOS! Your efforts help advance research in non-linguistic cognitive architectures.
