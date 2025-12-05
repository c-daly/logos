# LOGOS Ecosystem Git & Project Standards

This document defines the canonical Git workflow and project conventions for the entire LOGOS ecosystem. All repositories must follow these patterns.

**Canonical Location:** `logos/docs/GIT_PROJECT_STANDARDS.md`  
**Last Updated:** December 2025

---

## Overview

The LOGOS ecosystem consists of five repositories that share contracts, ontology, and standards. This document ensures consistent workflows across all repos.

| Repo | Purpose |
|------|---------|
| **logos** | Foundry—canonical contracts, ontology, SDKs, shared tooling, ecosystem standards |
| **sophia** | Non-linguistic cognitive core (Orchestrator, CWM-A/G, Planner, Executor) |
| **hermes** | Stateless language & embedding utility (STT, TTS, NLP, embeddings) |
| **talos** | Hardware abstraction layer for sensors/actuators |
| **apollo** | Thin client UI and command layer |

**Logos is upstream.** Changes to contracts, ontology, or standards in logos ripple to all downstream repos.

---

## Branch Strategy

### Never Work Directly on `main`

All changes—no matter how small—require a feature branch and pull request.

### Branch Naming Convention

```
{kind}/{repo}{issue-number}-{short-kebab}
```

**Examples:**
```
feature/logos420-testing-standards
fix/sophia88-cwm-state-sync
docs/hermes15-api-documentation
chore/apollo32-dependency-update
refactor/talos99-executor-cleanup
```

**Why include the repo prefix?**
- Branches are identifiable when working across multiple repos
- GitHub search works across the org
- Easy to correlate branches with tracking issues

### Branch Kinds

| Kind | When to Use |
|------|-------------|
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `chore/` | Dependencies, CI, tooling |
| `refactor/` | Code restructuring without behavior change |
| `test/` | Test additions or fixes |

---

## Commit Messages

### Format

```
{type}: {short description}

{optional body with more detail}

{optional footer with issue references}
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `test` | Adding/fixing tests |
| `chore` | Dependencies, CI, tooling |

### Examples

```
feat: add retry logic to HCG client

Implements exponential backoff for Neo4j connection failures.
Max retries: 3, base delay: 1s.

Closes #420
```

```
fix: handle null values in CWM state sync

Part of c-daly/logos#350
```

---

## Pull Requests

### Title Format

```
[{repo}] {Short imperative description}
```

**Examples:**
```
[logos] Add testing standards documentation
[sophia] Fix CWM state synchronization
[hermes] Update embedding model configuration
```

### Body Template

```markdown
## Summary
Brief description of what this PR does.

Closes #420

## Changes
- Added `docs/TESTING_STANDARDS.md`
- Updated cross-references in AGENTS.md

## Testing
- `./scripts/run_tests.sh unit` – ✅
- `poetry run ruff check .` – ✅
- `poetry run mypy src/` – ✅

## Downstream Impact
_Does this change affect other repos?_

None / List affected repos and describe impact
```

### Requirements

- [ ] Branch is up to date with `main`
- [ ] All tests pass
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy src/`)
- [ ] PR description is complete
- [ ] Issue is linked (`Closes #N`)

---

## Cross-Repository Changes

Many changes in LOGOS span multiple repositories. These require coordination.

### Workflow

1. **Create a tracking issue in logos**
   - Describe the full scope of the change
   - List all affected repositories
   - Define the rollout order

2. **Create branches in each affected repo**
   - Use consistent naming: `chore/logos420-feature-name`
   - Reference the tracking issue in each branch

3. **Merge logos first**
   - Logos defines contracts, ontology, and standards
   - Downstream repos depend on these definitions

4. **Create linked PRs in downstream repos**
   - Reference the tracking issue: `Part of c-daly/logos#420`
   - Reference the logos PR if it contains the contract/standard

5. **Close the tracking issue**
   - Only after all downstream PRs are merged
   - Add a summary comment listing all merged PRs

### Example: Contract Change

```markdown
# Tracking Issue: logos#420

## Summary
Update the HCG API contract to add media node support.

## Affected Repos
- [x] logos – Contract definition (#420)
- [ ] sophia – Implement new endpoints (#XX)
- [ ] hermes – Update SDK (#XX)
- [ ] apollo – Update client (#XX)

## Rollout Order
1. logos – Define contract
2. hermes – Update SDK (depends on contract)
3. sophia – Implement API (depends on SDK)
4. apollo – Update UI (depends on API)

## Related PRs
- c-daly/logos#421 – Contract definition
- c-daly/hermes#XX – SDK update
- c-daly/sophia#XX – API implementation
- c-daly/apollo#XX – Client update
```

---

## Issue Management

### Issue Title Format

```
[{repo}] {Short description}
```

**Examples:**
```
[logos] Add testing standards documentation
[sophia] CWM state not syncing on restart
[hermes] Support for new embedding model
```

### Labels

Standard labels across all repos:

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature request |
| `documentation` | Documentation only |
| `infrastructure` | CI, tooling, deployment |
| `testing` | Test-related changes |
| `breaking-change` | Requires coordination |
| `cross-repo` | Spans multiple repositories |

### Linking Issues

```markdown
# In commit messages
Closes #420
Fixes #420
Part of c-daly/logos#420

# In PR descriptions
Closes #420
Related to c-daly/sophia#64
Part of c-daly/logos#420
```

---

## Contract Changes

Contracts in `logos/contracts/` define the API interfaces between services. Changes require extra coordination.

### Before Modifying a Contract

1. **Identify consumers** – Which repos implement or call this API?
2. **Create a tracking issue** – Document the migration plan
3. **Design for backward compatibility** – Add fields, don't remove
4. **Coordinate the rollout** – Logos first, then downstream

### Breaking Changes

If a breaking change is unavoidable:

1. Add a `breaking-change` label to the issue
2. Document the migration path in the PR
3. Create issues in all affected repos
4. Coordinate deployment timing
5. Update the contract version

---

## Code Review

### Reviewer Checklist

- [ ] Code is clear and well-documented
- [ ] Tests cover the changes
- [ ] No unrelated changes included
- [ ] Backward compatibility maintained (or breaking change documented)
- [ ] Cross-repo impact documented (if applicable)

### Author Responsibilities

- Keep PRs focused and small when possible
- Respond to review comments promptly
- Update the PR based on feedback
- Don't merge without approval

---

## Release Process

### Versioning

All repos follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

MAJOR – Breaking changes
MINOR – New features (backward compatible)
PATCH – Bug fixes (backward compatible)
```

### Tagging

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

### Changelog

Maintain a `CHANGELOG.md` in each repo:

```markdown
## [1.2.3] - 2025-12-05

### Added
- New feature X

### Fixed
- Bug in Y

### Changed
- Updated Z behavior
```

---

## Quick Reference

### Daily Workflow

```bash
# Start work
git checkout main
git pull
git checkout -b feature/logos420-my-feature

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "feat: add my feature"

# Push
git push -u origin feature/logos420-my-feature

# Create PR via GitHub
```

### Before Pushing

```bash
# Run tests
./scripts/run_tests.sh unit

# Check linting
poetry run ruff check .
poetry run ruff format --check .

# Check types
poetry run mypy src/
```

### Sync with Main

```bash
git checkout main
git pull
git checkout feature/logos420-my-feature
git rebase main
# or: git merge main
```

---

## Related Documentation

- [Testing Standards](TESTING_STANDARDS.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [CI/CD Documentation](operations/ci/README.md)

---

## Changelog

| Date | Change |
|------|--------|
| Dec 2025 | Created from AGENTS.md git workflow content |
