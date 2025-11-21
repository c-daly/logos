# Dependency Management Strategy for Project LOGOS

## Overview

This document defines the standard dependency management approach for all repositories in the Project LOGOS ecosystem. Each repository manages its own dependencies independently, using consistent tooling and best practices across the entire project.

## Architecture Decision

### Per-Repository Dependency Management

Project LOGOS uses a **decoupled, multi-repository architecture** where each component (Sophia, Hermes, Talos, Apollo, and LOGOS foundry) operates as an independent service. This architectural choice necessitates a per-repository dependency management strategy rather than a centralized monorepo approach.

**Rationale:**
- Each component has unique dependencies and lifecycle requirements
- Components can evolve independently without affecting others
- Reduces coupling and allows for component-specific optimization
- Aligns with microservices best practices
- Facilitates independent deployment and versioning

## Standard Tool: Poetry

All LOGOS repositories use **Poetry** as the standard dependency management tool.

### Why Poetry?

Poetry was chosen for the following reasons:

1. **Modern Dependency Resolution**: Poetry uses a deterministic dependency resolver that ensures consistent installations across all environments
2. **Integrated Virtual Environment Management**: Built-in venv management simplifies development setup
3. **pyproject.toml Standard**: Uses PEP 518/517 standards for Python project configuration
4. **Dependency Groups**: Supports organizing dependencies into logical groups (dev, test, docs, etc.)
5. **Lock File**: `poetry.lock` ensures reproducible builds across all environments
6. **Publishing Support**: Streamlines package publishing to PyPI or private repositories
7. **Active Development**: Well-maintained with strong community support

## Setting Up Poetry in a New Repository

### 1. Installation

Install Poetry globally (recommended) or in your project:

```bash
# Via pip (simplest method)
pip install poetry

# Via official installer (recommended for production)
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

### 2. Initialize Poetry in Your Repository

Navigate to your repository root and initialize Poetry:

```bash
# Option 1: Initialize a new Poetry project interactively
poetry init

# Option 2: Convert existing pyproject.toml (if applicable)
# Poetry will detect and work with existing pyproject.toml files
```

### 3. Configure pyproject.toml

Your `pyproject.toml` should follow this structure:

```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "your-project-name"
version = "0.1.0"
description = "Project description"
authors = ["Project LOGOS Contributors"]
readme = "README.md"
license = "MIT"
python = "^3.10"  # Minimum Python 3.10 for all LOGOS components

[tool.poetry.dependencies]
python = "^3.10"
# Add your core runtime dependencies here
# Example: rdflib = "^7.0.0"

[tool.poetry.group.dev.dependencies]
# Development and testing dependencies
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"
mypy = "^1.7.0"

[tool.poetry.scripts]
# Define CLI entry points here if needed
# Example: my-command = "my_package.module:main"
```

### 4. Update .gitignore

Ensure your `.gitignore` excludes Poetry artifacts:

```gitignore
# Virtual environments
.venv/
venv/
env/

# Poetry
poetry.lock  # Include this if you want deterministic builds
.poetry/

# Python
__pycache__/
*.py[cod]
dist/
build/
*.egg-info/
```

**Note**: For libraries intended for distribution, commit `poetry.lock` to ensure reproducible builds. For applications, `poetry.lock` should always be committed.

## Best Practices

### Adding Dependencies

```bash
# Add a core runtime dependency
poetry add package-name

# Add with version constraint
poetry add "package-name>=1.0.0,<2.0.0"

# Add to a specific dependency group
poetry add --group dev pytest

# Add from git repository
poetry add git+https://github.com/user/repo.git
```

### Dependency Groups

Use Poetry's dependency groups to organize dependencies:

- **Main dependencies** (`[tool.poetry.dependencies]`): Core runtime requirements
- **dev** (`[tool.poetry.group.dev.dependencies]`): Development tools (linters, formatters, type checkers)
- **test** (`[tool.poetry.group.test.dependencies]`): Testing frameworks and utilities
- **docs** (`[tool.poetry.group.docs.dependencies]`): Documentation generation tools

Example:

```toml
[tool.poetry.group.test.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-mock = "^3.11.0"

[tool.poetry.group.docs.dependencies]
sphinx = "^7.0.0"
sphinx-rtd-theme = "^1.3.0"
```

### Installing Dependencies

```bash
# Install all dependencies (including dev)
poetry install

# Install only production dependencies
poetry install --only main

# Install with specific groups
poetry install --with test,docs

# Update dependencies to latest compatible versions
poetry update

# Update specific package
poetry update package-name
```

### Managing the Lock File

```bash
# Generate/update poetry.lock without installing
poetry lock

# Update lock file and install
poetry lock && poetry install

# Show outdated packages
poetry show --outdated
```

### Virtual Environment Management

```bash
# Create virtual environment (happens automatically on poetry install)
poetry env use python3.10

# Activate the virtual environment
poetry shell

# Run commands in the virtual environment without activating
poetry run python script.py
poetry run pytest

# Show virtual environment info
poetry env info

# List all virtual environments
poetry env list

# Remove virtual environment
poetry env remove python3.10
```

### Version Constraints

Use semantic versioning constraints:

- `^1.2.3` - Compatible with 1.2.3, allows >=1.2.3 and <2.0.0
- `~1.2.3` - Compatible with 1.2.3, allows >=1.2.3 and <1.3.0
- `>=1.2.3,<2.0.0` - Explicit range
- `*` - Any version (avoid in production)

## Integration with LOGOS Ecosystem

### Python Version Requirements

All LOGOS components must support **Python 3.10 or higher**. Configure this in your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.10"
```

### Common Dependencies Across Components

While each component manages its own dependencies, some common patterns exist:

- **HCG-related components** (Sophia): Neo4j drivers, RDF libraries
- **Language utilities** (Hermes): NLP libraries, embedding models
- **Hardware abstraction** (Talos): Hardware interface libraries
- **UI components** (Apollo): Web frameworks, UI libraries

### Dependency Security

Always validate dependencies for security vulnerabilities:

```bash
# Use Poetry's built-in audit (requires Poetry 1.2+)
poetry check

# Export requirements for security scanning
poetry export -f requirements.txt | safety check --stdin
```

## Workflow Examples

### Starting a New LOGOS Component

```bash
# 1. Create repository and navigate to it
cd my-new-component

# 2. Initialize Poetry
poetry init

# 3. Configure Python version requirement
# Edit pyproject.toml and set python = "^3.10"

# 4. Add initial dependencies
poetry add rdflib pyshacl  # Example core dependencies

# 5. Add development dependencies
poetry add --group dev pytest ruff mypy black

# 6. Install everything
poetry install

# 7. Update .gitignore
echo ".venv/" >> .gitignore
echo "poetry.lock" >> .gitignore  # Optional, see note above

# 8. Commit
git add pyproject.toml .gitignore
git commit -m "Initialize Poetry dependency management"
```

### Daily Development Workflow

```bash
# Activate the environment
poetry shell

# Or run commands directly
poetry run pytest
poetry run ruff check .
poetry run mypy src/

# Add new dependency when needed
poetry add new-package

# Keep dependencies updated
poetry update
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Install Poetry
  run: pip install poetry

- name: Install dependencies
  run: poetry install --only main

- name: Run tests
  run: poetry run pytest
```

## Troubleshooting

### Poetry Lock File Conflicts

If you encounter merge conflicts in `poetry.lock`:

```bash
# Regenerate the lock file
git checkout --ours poetry.lock  # or --theirs
poetry lock --no-update
```

### Dependency Resolution Issues

```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Verbose output for debugging
poetry install -vvv
```

### Virtual Environment Issues

```bash
# Remove and recreate environment
poetry env remove python3.10
poetry install
```

## Migration from setuptools/pip

If you're converting an existing repository from setuptools:

1. **Backup existing files**: `cp pyproject.toml pyproject.toml.backup`
2. **Convert dependencies**: Map `install_requires` → `[tool.poetry.dependencies]`
3. **Convert dev dependencies**: Map `extras_require['dev']` → `[tool.poetry.group.dev.dependencies]`
4. **Update build system**: Replace setuptools with Poetry in `[build-system]`
5. **Test**: Run `poetry install` and verify all packages install correctly
6. **Update CI/CD**: Replace `pip install` with `poetry install` in workflows

## References

- [Poetry Documentation](https://python-poetry.org/docs/)
- [PEP 518 - Specifying Minimum Build System Requirements](https://peps.python.org/pep-0518/)
- [PEP 517 - A build-system independent format for source trees](https://peps.python.org/pep-0517/)
- [Semantic Versioning](https://semver.org/)

## Maintenance

This document should be reviewed and updated:
- When Poetry releases major version updates
- When LOGOS ecosystem Python version requirements change
- When new best practices emerge from team experience
- At the start of each new development epoch

---

**Last Updated**: 2025-11-17  
**Maintainer**: Project LOGOS Contributors  
**Status**: Active
