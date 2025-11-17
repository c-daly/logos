# Dependency Management Issues - Usage Guide

This document explains how to create dependency management issues for LOGOS component repositories using the `logos-generate-dependency-issues` tool.

## Overview

The `logos-generate-dependency-issues` tool generates GitHub issues for setting up dependency management in each of the LOGOS ecosystem repositories:

- **sophia** (Python): Set up Poetry or pipenv
- **hermes** (Python): Set up Poetry or pipenv
- **talos** (Python): Set up Poetry or pipenv
- **apollo** (JavaScript/TypeScript): Set up npm or yarn

## Installation

First, install the LOGOS foundry tools:

```bash
pip install -e ".[dev]"
```

> **Note:** If you've already installed the package and are seeing a `command not found` error for `logos-generate-dependency-issues`, you may need to reinstall it to register the new console script entry point:
> ```bash
> pip install -e ".[dev]" --force-reinstall --no-deps
> ```

## Usage

### Generate GitHub CLI Commands

The easiest way to create issues is using the GitHub CLI format:

```bash
# Generate the script
logos-generate-dependency-issues --format gh-cli --output create_dependency_issues.sh

# Review the script
cat create_dependency_issues.sh

# Make it executable
chmod +x create_dependency_issues.sh

# Run it (requires gh CLI to be installed and authenticated)
./create_dependency_issues.sh
```

### Generate JSON Format

To get machine-readable output:

```bash
logos-generate-dependency-issues --format json --output dependency_issues.json
```

### Generate Markdown Format

To get human-readable documentation:

```bash
logos-generate-dependency-issues --format markdown --output dependency_issues.md
```

## Issue Template

Each generated issue includes:

### For Python Repositories (sophia, hermes, talos)

- **Title**: Set up dependency management (Poetry or pipenv)
- **Component**: Repository description
- **Options**: 
  - Poetry (Recommended) with pyproject.toml
  - Pipenv with Pipfile
- **Requirements**:
  - Python >=3.11
  - Virtual environment isolation
  - Lock files for reproducibility
  - Development dependencies (pytest, ruff, mypy)
  - Documentation in README.md

### For JavaScript Repository (apollo)

- **Title**: Set up dependency management (npm or yarn)
- **Component**: Repository description
- **Options**:
  - npm with package-lock.json
  - yarn with yarn.lock
- **Requirements**:
  - Node.js >=18.x
  - Scripts for build, test, lint, dev
  - Lock files for reproducibility
  - Development dependencies (typescript, eslint, prettier, jest)
  - Documentation in README.md

## Labels

All issues are tagged with:
- `component:<repo-name>` (e.g., component:sophia)
- `priority:high`
- `type:infrastructure`
- `phase:1`

## Milestone

All issues are assigned to: **M1: HCG Store & Retrieve**

## Example Output

Here's an example of the generated GitHub CLI command:

```bash
gh issue create \
  --repo c-daly/sophia \
  --title "Set up dependency management (Poetry or pipenv)" \
  --body "## Set up Dependency Management for Sophia..." \
  --label "component:sophia,priority:high,type:infrastructure,phase:1"
```

## Manual Issue Creation

If you prefer to create issues manually, you can:

1. Generate the markdown format to see the full issue templates
2. Copy the content for each repository
3. Create issues through the GitHub web interface

## Next Steps

After creating these issues:

1. Each component repository team can choose their preferred dependency manager
2. Follow the acceptance criteria in each issue
3. Document the setup in the respective README.md files
4. Update CI/CD configurations to use the chosen tools

## References

- Action Items: `docs/action_items.md` (Section 1.1)
- Project Specification: `docs/spec/project_logos_full.md`
- LOGOS Foundry: https://github.com/c-daly/logos
