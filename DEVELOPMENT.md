# LOGOS Foundry - Development Setup

This document describes how to set up the development environment for the LOGOS Foundry repository.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for running the HCG dev cluster)
- Git

## Python Environment Setup

### Using Poetry (recommended for development)

1. Install Poetry if not already installed:
```bash
pip install poetry
```

2. Install the package and all dependencies (including dev dependencies):
```bash
poetry install
```

3. Activate the Poetry virtual environment:
```bash
poetry shell
```

Alternatively, run commands directly without activating the shell:
```bash
poetry run pytest
poetry run logos-generate-issues
```

### Using pip (alternative to Poetry)

For installation without Poetry:

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package in editable mode:
```bash
pip install -e .
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

**Note:** Poetry is recommended for development as it provides better dependency management and reproducible environments.

## Dependency Management

The project uses Poetry for dependency management. The `poetry.lock` file is committed to the repository to ensure reproducible builds and to enable GitHub's dependency graph and security features.

### Adding New Dependencies

When adding new dependencies:

1. Add the dependency to `pyproject.toml` under `[tool.poetry.dependencies]` or `[tool.poetry.group.dev.dependencies]`:
```bash
poetry add <package-name>  # Production dependency
poetry add --group dev <package-name>  # Development dependency
```

2. The `poetry.lock` file will be automatically updated. Commit both `pyproject.toml` and `poetry.lock`:
```bash
git add pyproject.toml poetry.lock
git commit -m "Add <package-name> dependency"
```

### Updating Dependencies

To update dependencies to their latest compatible versions:
```bash
poetry update  # Update all dependencies
poetry update <package-name>  # Update specific package
```

**Important**: Always commit the updated `poetry.lock` file to maintain dependency consistency across environments and enable GitHub's dependency graph and security alerts.

## Running Tests

The project uses pytest for testing. Tests should be run via Poetry:

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov --cov-report=term-missing --cov-report=html

# Run specific test file
poetry run pytest tests/test_generate_issues.py

# Run tests matching a pattern
poetry run pytest -k "test_parser"
```

Test configuration is defined in `pyproject.toml` under `[tool.pytest.ini_options]`.

### Local CI Parity

To run the same lint/type/test sequence that executes in `.github/workflows/ci.yml`, use the helper script next to the workflow:

```bash
./.github/workflows/run_ci.sh
```

The script installs dependencies with Poetry and then runs Ruff, Black, mypy, and pytest with the exact arguments defined in CI, making it easy to reproduce failures locally.

## SDK Generation

Shared SDKs for Sophia and Hermes live under `sdk/` (Python) and `sdk-web/` (TypeScript). Whenever the OpenAPI contracts change, regenerate the clients via:

```bash
./scripts/generate-sdks.sh
```

Requirements:
- Node.js/npm (the script uses `npx @openapitools/openapi-generator-cli`)

The script removes existing SDK folders and re-generates them from `contracts/*.openapi.yaml`. Commit the resulting changes so downstream projects can consume the updated packages.

## Hermes `/llm` Gateway Configuration

Hermes proxies all chat/LLM traffic through the `/llm` endpoint defined in `contracts/hermes.openapi.yaml`. When running the Hermes service directly (e.g., during Apollo browser demos), configure the provider via environment variables:

- `HERMES_LLM_PROVIDER` — Provider identifier (`openai`, `local`, `echo`). Defaults to `echo`, or `openai` automatically when an API key is present.
- `HERMES_LLM_API_KEY` / `OPENAI_API_KEY` — Credential required for `openai`.
- `HERMES_LLM_MODEL` — Optional override for the provider model (e.g., `gpt-4o-mini`).
- `HERMES_LLM_BASE_URL` — Override the upstream base URL if routing through a proxy.

Apollo’s SDKs assume the `/llm` contract is available; keep these variables in your shell or supervisor when launching `poetry run uvicorn hermes.api:app --reload`.

## Linting and Code Quality

The project uses Ruff for linting and formatting, and mypy for type checking:

```bash
# Lint the codebase
poetry run ruff check .

# Auto-fix linting issues
poetry run ruff check --fix .

# Format code
poetry run ruff format .

# Type checking with mypy
poetry run mypy logos_tools
```

## Using the CLI Tools

After installation with Poetry, you can use the command-line tools:

```bash
# Generate issues in JSON format
poetry run logos-generate-issues --format json

# Generate issues as GitHub CLI commands
poetry run logos-generate-issues --format gh-cli --output create_issues.sh

# Create issues organized by epochs
poetry run logos-create-issues-by-epoch --format markdown

# Or, if you've activated the Poetry shell (poetry shell):
logos-generate-issues --format json
logos-create-issues-by-epoch --format markdown
```

## Running the HCG Development Cluster

See the main [README.md](README.md) for instructions on running the Neo4j + Milvus development cluster.

## Validating Artifacts

The repository includes automated validation for all canonical artifacts:

```bash
# Validate manually (requires Docker for Neo4j)
# See .github/workflows/validate-artifacts.yml for the validation steps
```

Or trigger the validation workflow:
- Push to main/develop branches
- Open a pull request
- Manually via GitHub Actions UI

## Project Structure

```
logos/
├── .github/
│   ├── scripts/          # Python utility scripts (installed as logos_tools package)
│   │   ├── __init__.py
│   │   ├── generate_issues.py
│   │   └── create_issues_by_epoch.py
│   ├── workflows/        # GitHub Actions workflows
│   └── ISSUE_TEMPLATE/   # Issue templates
├── contracts/            # OpenAPI contracts (e.g., hermes.openapi.yaml)
├── docs/                 # Documentation and specifications
│   └── spec/            # Formal specifications
├── infra/               # Infrastructure configuration (docker-compose, etc.)
├── ontology/            # HCG ontology and SHACL shapes
│   ├── core_ontology.cypher
│   └── shacl_shapes.ttl
├── tests/               # Test suite
├── pyproject.toml       # Python project configuration
└── README.md            # Main documentation
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Open a pull request

All pull requests must pass:
- Automated tests (pytest)
- Artifact validation (Cypher, SHACL, OpenAPI)
- Code quality checks
