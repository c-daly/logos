# LOGOS Foundry - Development Setup

This document describes how to set up the development environment for the LOGOS Foundry repository.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for running the HCG dev cluster)
- Git

## Python Environment Setup

### Using pip (recommended for development)

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package in editable mode with development dependencies:
```bash
pip install -e .
pip install -r requirements-dev.txt
```

**Note**: The project uses Poetry for dependency management. If you have Poetry installed, you can use:
```bash
poetry install
```

### Using system Python

If you prefer to install dependencies system-wide:
```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Running Tests

The project uses pytest for testing:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=logos_tools --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_generate_issues.py

# Run tests matching a pattern
pytest -k "test_parser"
```

Test configuration is defined in `pyproject.toml` under `[tool.pytest.ini_options]`.

## Linting and Code Quality

The project uses Ruff for linting and formatting:

```bash
# Lint the codebase
ruff check .

# Format code
ruff format .

# Type checking with mypy
mypy .github/scripts
```

## Using the CLI Tools

After installation, you can use the command-line tools:

```bash
# Generate issues in JSON format
logos-generate-issues --format json

# Generate issues as GitHub CLI commands
logos-generate-issues --format gh-cli --output create_issues.sh

# Create issues organized by epochs
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
