# Agent Instructions

This guidance applies to the Logos repository and governs how AI agents interact with the codebase.

## Repository context

### Ecosystem overview
Logos is the **foundry** for the LOGOS cognitive architecture—home to canonical contracts, shared ontology, reusable SDKs, and ecosystem-wide standards.

| Repo | Purpose |
|------|---------|
| **logos** (this repo) | Foundry—canonical contracts, ontology, SDKs, shared tooling, ecosystem standards |
| **sophia** | Non-linguistic cognitive core (Orchestrator, CWM-A/G, Planner, Executor) |
| **hermes** | Stateless language & embedding utility (STT, TTS, NLP, embeddings) |
| **talos** | Hardware abstraction layer for sensors/actuators |
| **apollo** | Thin client UI and command layer |

Logos is the **upstream source of truth** for contracts, ontology, and standards. Changes here ripple to all downstream repos.

### This repository
Logos provides shared infrastructure for the ecosystem:
- **Contracts** – OpenAPI specs defining service interfaces
- **Ontology** – Core ontology and SHACL shapes for the HCG
- **SDKs** – Python packages (`logos_hcg`, `logos_sophia`, etc.)
- **Standards** – Testing, Git, and project conventions
- **Reusable CI** – GitHub Actions workflows consumed by all repos

Key directories:
- `contracts/` – OpenAPI specifications
- `ontology/` – Cypher schemas and SHACL shapes
- `logos_hcg/` – Hybrid Causal Graph client library
- `logos_config/` – **Shared configuration utilities** (env, ports, settings, health)
- `docs/` – Ecosystem-wide documentation and standards
- `.github/workflows/` – Reusable CI workflows

### Key documentation
- `README.md` – Project overview and getting started
- `docs/TESTING_STANDARDS.md` – Ecosystem testing conventions
- `docs/GIT_PROJECT_STANDARDS.md` – Git workflow and cross-repo patterns
- `docs/standards/INTENT_FRAMEWORK.md` – Intent Framework for agent direction

---

## Intent Framework

This repository uses the **Intent Framework** for providing consistent direction to AI agents across sessions and models. The framework is based on cascading direction artifacts (`INTENT.md` files).

### Quick summary

- **Direction artifacts** (`INTENT.md`) define what must not change
- Files cascade from repo root → subsystem → feature (hard inheritance)
- Local files may override parent invariants with explicit justification
- Agents operate in **modes**: Explore, Propose, Execute, Critique, Reevaluate
- **Reevaluation** is mandatory and confidence-driven

### Key files

| File | Purpose |
|------|---------|
| `/INTENT.md` | Root direction artifact (global invariants) |
| `docs/standards/INTENT_FRAMEWORK.md` | Full framework specification |
| `docs/templates/INTENT_FEATURE_TEMPLATE.md` | Template for feature-level intents |
| `docs/templates/AGENT_MODE_GUARDS.md` | Mode guard prompt templates |
| `docs/templates/CRITIC_OUTPUT_SCHEMA.md` | Critic output format |

### Using the framework

1. **Check for `INTENT.md`** files from your working directory up to repo root
2. **All parent intents apply** — constraints accumulate
3. **Create feature-level intents** for non-trivial tasks
4. **Use mode guards** to bound agent behavior
5. **Reevaluate** when triggers are met (step budget, assumption drift, etc.)

See `docs/standards/INTENT_FRAMEWORK.md` for the complete specification.

---

## Ecosystem standards

This repository defines the canonical standards for the entire LOGOS ecosystem. When working in any repo, reference these:

| Standard | Document |
|----------|----------|
| Testing conventions | `docs/TESTING_STANDARDS.md` |
| Git workflow | `docs/GIT_PROJECT_STANDARDS.md` |
| Port allocation | `docs/TESTING_STANDARDS.md` (Port Allocation section) |

### Port allocation (prefix-based)

Each repo has a unique prefix to prevent conflicts when running test stacks in parallel:

| Repo | Prefix | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Health | API |
|------|--------|------------|------------|-------------|---------------|-----|
| hermes | 17xxx | 17474 | 17687 | 17530 | 17091 | 17000 |
| apollo | 27xxx | 27474 | 27687 | 27530 | 27091 | 27000 |
| logos | 37xxx | 37474 | 37687 | 37530 | 37091 | 37000 |
| sophia | 47xxx | 47474 | 47687 | 47530 | 47091 | 47000 |
| talos | 57xxx | 57474 | 57687 | 57530 | 57091 | 57000 |

### Shared configuration (`logos_config`)

The `logos_config` package is the **source of truth** for configuration across all LOGOS repos. All repos should use it instead of duplicating config helpers.

```python
from logos_config import get_env_value, get_repo_ports, Neo4jConfig, SOPHIA_PORTS

# Environment variables
db_host = get_env_value("DB_HOST", default="localhost")

# Port allocation
ports = get_repo_ports("sophia")
print(ports.neo4j_http)  # 47474

# Service configuration
neo4j = Neo4jConfig()  # Reads from NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
```

See `logos_config/README.md` for full documentation.

---

## Communication and transparency

### Announce intent before acting
Do not take impactful actions—large refactors, dependency bumps, new features, contract changes—without first describing your intent and waiting for acknowledgment. Explain *what* you plan to change and *why*.

### Surface uncertainty early
If a task is ambiguous, ask clarifying questions rather than guessing. When multiple reasonable interpretations exist, list them and ask which to pursue.

### No silent side effects
If your change will affect behavior, contracts, or downstream repos, call it out explicitly before proceeding.

---

## Workflow safety

### Never work directly on `main`
Always create a feature branch before making any changes. Branch naming convention:
```
{kind}/{repo}{issue-number}-{short-kebab}
# e.g., feature/logos420-testing-standards
# e.g., fix/logos88-ontology-constraint
# e.g., docs/logos15-api-documentation
```

The repo prefix (`logos`) makes branches identifiable across the ecosystem.

### Never push without a pull request
All changes—no matter how small—must go through a PR. Direct pushes to any shared branch are forbidden.

### Cross-repository changes
Logos often contains tracking issues for ecosystem-wide changes. When implementing cross-repo changes:

1. **Create a tracking issue in logos** describing the full scope
2. **Create branches in each affected repo** with consistent naming: `chore/logos420-testing-standards`
3. **Reference the tracking issue** from each PR using `Part of c-daly/logos#N`
4. **Merge logos changes first** (they define the standard)
5. **Close the tracking issue** only after all downstream PRs merge

See `docs/GIT_PROJECT_STANDARDS.md` for complete documentation.

### Contract changes require coordination
Before modifying any contract in `contracts/`:
1. Identify all repos that implement or consume the contract
2. Create a tracking issue describing the migration
3. Update contracts in logos first
4. Coordinate downstream updates via linked issues/PRs

---

## Code quality and professional practices

### Elevate code you touch
When modifying existing code, lift the surrounding area toward current best practices—improved typing, clearer error handling, better logging, more readable structure.

### Small, composable functions
Prefer small, focused functions over monolithic blocks. Each function should do one thing well.

### Type hints and docstrings
Add or update type hints and docstrings whenever you introduce or modify public functions, classes, or methods. Prefer explicit types over `Any`.

### Backward compatibility
Maintain backward compatibility unless the task explicitly calls for a breaking change. If you must break compatibility:
- Call it out clearly in your summary
- Ensure tests cover the migration path
- File coordination tickets in downstream repos

### Security and privacy hygiene
- Never log secrets, tokens, or PII
- Use parameterized queries for Neo4j to prevent injection
- Sanitize user inputs; assume external data is hostile

---

## Reflection and course correction

### Pause when things aren't working
If you encounter repeated errors, persistent friction, or uncertainty—**stop**. Do not push forward blindly.

### Reassess and gather context
- Reread relevant files, docs, or specs
- Search for related patterns in the codebase
- Check if assumptions you made earlier are still valid
- Ask for clarification if needed

### Adjust your approach
If the same strategy keeps failing, try a different angle. Document what you tried and why it didn't work.

---

## Do's and Don'ts

### Definitely Do
- **Create a branch before any changes** – Never work directly on `main`
- **Run tests before pushing** – At minimum: `./scripts/run_tests.sh unit`
- **Ask before large refactors** – Describe intent, wait for acknowledgment
- **Reference issues in commits/PRs** – Use `Closes #N` or `Part of #N`
- **Update tests when changing behavior** – Tests document expectations
- **Coordinate contract changes** – All downstream repos depend on logos
- **Use consistent branch names across repos** – `chore/logos420-feature` everywhere
- **Update the standards docs when patterns change** – This repo defines the rules
- **Commit `poetry.lock` with `pyproject.toml`** – Always together
- **Create tracking issues for cross-repo work** – One issue, multiple PRs

### Definitely Don't
- **Don't push directly to `main`** – All changes require a PR
- **Don't ignore failing tests** – Fix them or explain why they're skipped
- **Don't make unrelated changes in a PR** – Keep PRs focused; file follow-up tickets
- **Don't change contracts without coordination** – Downstream repos will break
- **Don't commit secrets or tokens** – Ever. Check your diffs.
- **Don't skip the PR description** – Reviewers need context
- **Don't merge without CI passing** – If CI is broken, fix it first
- **Don't update reusable workflows without testing** – All repos use them
- **Don't leave zombie containers running** – `./scripts/run_tests.sh down`
- **Don't define repo-specific standards here** – Only ecosystem-wide conventions

---

## Testing and linting

### Test infrastructure
Logos follows its own testing standards (see `docs/TESTING_STANDARDS.md`):

| Test Type | Location | Command |
|-----------|----------|---------|
| Unit | `tests/unit/` | `./scripts/run_tests.sh unit` |
| Integration | `tests/integration/` | `./scripts/run_tests.sh integration` |
| E2E | `tests/e2e/` | `./scripts/run_tests.sh e2e` |

### Quick commands
```bash
./scripts/run_tests.sh all      # Run all tests
./scripts/run_tests.sh unit     # Unit tests only
./scripts/run_tests.sh up       # Start infrastructure
./scripts/run_tests.sh down     # Stop infrastructure
./scripts/run_tests.sh ci       # Full CI parity
```

---

## Linting and formatting

All code must pass linting before merge. The ecosystem uses **ruff** for linting and formatting, **mypy** for type checking.

### Ruff (linting and formatting)
Ruff replaces flake8, isort, and black in a single fast tool:

```bash
# Check for linting errors
poetry run ruff check .

# Check specific path
poetry run ruff check src/logos_hcg/

# Auto-fix safe issues
poetry run ruff check --fix .

# Format code (replaces black)
poetry run ruff format .

# Check formatting without changing files
poetry run ruff format --check .
```

Common ruff rules enforced:
- `E` / `W` – pycodestyle errors and warnings
- `F` – pyflakes
- `I` – isort (import sorting)
- `UP` – pyupgrade (modern Python syntax)
- `B` – bugbear (common bugs)
- `SIM` – simplify (code simplification)

### Mypy (type checking)
```bash
# Check all source code
poetry run mypy src/

# Check specific module
poetry run mypy src/logos_hcg/

# Stricter checking (if configured)
poetry run mypy --strict src/
```

Mypy expectations:
- Public functions should have type hints
- Avoid `Any` unless absolutely necessary
- Use `Optional[X]` or `X | None` for nullable types
- Generic collections should be typed (`list[str]`, not `list`)

### Pre-commit workflow
Before pushing, run the full lint suite:
```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy src/
```

Or use the CI script which runs everything:
```bash
./scripts/run_tests.sh ci
```

### Fixing common issues

**Import sorting (ruff I001):**
```bash
poetry run ruff check --select I --fix .
```

**Line too long (E501):**
- Ruff's formatter handles most cases
- For strings, use implicit concatenation or textwrap
- For function calls, break at arguments

**Missing type hints:**
- Add return types: `def foo() -> str:`
- Add parameter types: `def foo(x: int, y: str) -> bool:`
- Use `from __future__ import annotations` for forward references

**Unused imports (F401):**
```bash
poetry run ruff check --select F401 --fix .
```

### Configuration
Ruff and mypy are configured in `pyproject.toml`. Do not override settings in individual files unless there's a documented reason.

### Always note what you ran
In your summary, explicitly list which checks you executed.

---

## Pull request expectations

### Issue format
**Title:** `[logos] Short imperative description`
```
[logos] Add testing standards documentation
[logos] Update HCG client retry logic
```

### Pull request format
**Title:** `[logos] Short imperative description (#issue)`

**Body:**
```markdown
## Summary
Brief description of what this PR does.

Closes #420

## Changes
- Added `docs/TESTING_STANDARDS.md`
- Updated reusable CI workflow

## Testing
- `./scripts/run_tests.sh unit` – ✅
- `poetry run ruff check .` – ✅

## Downstream impact
This change affects: sophia, hermes, apollo, talos
Related PRs will be created in each repo.
```

### Cross-repo PRs
For PRs that are part of a multi-repo change:
```markdown
## Cross-Repository Change
This PR defines standards that will be implemented across all repos.

### Related PRs
- c-daly/sophia#64 - Implement standards
- c-daly/hermes#XX - Implement standards
- c-daly/apollo#XX - Implement standards
- c-daly/talos#XX - Implement standards
```

---

## Troubleshooting

### Port conflicts
If services fail to start with "port already in use":
```bash
# Check what's using the port (logos uses +30000 offset)
lsof -i :37474

# Stop any existing test containers
./scripts/run_tests.sh down
docker ps | grep logos-test | awk '{print $1}' | xargs docker stop
```

### Neo4j won't start
```bash
# Check container logs
docker logs logos-test-neo4j

# Common fix: clear volumes and restart
./scripts/run_tests.sh clean
./scripts/run_tests.sh up
```

### Milvus health check failing
Milvus can take 60-90 seconds to become healthy. If it times out:
```bash
# Check etcd and minio are healthy first
docker logs logos-test-milvus-etcd
docker logs logos-test-milvus-minio

# Then check milvus
docker logs logos-test-milvus
```

### Tests can't connect to services
Ensure environment variables match the port allocation:
```bash
export NEO4J_URI=bolt://localhost:37687
export MILVUS_HOST=localhost
export MILVUS_PORT=37530
```
Or use `./scripts/run_tests.sh` which sets these automatically.

### GitHub MCP authentication errors
```bash
# Refresh the GitHub token
~/mcp
# Then retry the operation
```

### Cross-repo changes: wrong ports
Each repo has its own port prefix. Check `docs/TESTING_STANDARDS.md` for the full table:
| Repo | Prefix |
|------|--------|
| hermes | 17xxx |
| apollo | 27xxx |
| logos | 37xxx |
| sophia | 47xxx |
| talos | 57xxx |

### Import errors after pulling
```bash
poetry install
```

---

## GitHub Access

**You have full access to GitHub.** Do not claim otherwise. If one method doesn't work, try another.

### Available access methods

| Method | Best For | How to Use |
|--------|----------|------------|
| **MCP tools** | Most operations | `mcp_github_*` function calls |
| **GitHub CLI** | Complex queries, bulk operations | `gh` command in terminal |
| **GraphQL API** | Advanced queries, projects | `gh api graphql` |
| **REST API** | Simple operations | `gh api` or `curl` |

### MCP GitHub Tools (preferred)
The MCP provides direct GitHub integration. Common tools:

```
# Issues
mcp_github_list_issues          # List issues in a repo
mcp_github_search_issues        # Search with GitHub query syntax
mcp_github_issue_read           # Get issue details, comments, labels
mcp_github_issue_write          # Create or update issues

# Pull Requests  
mcp_github_list_pull_requests   # List PRs
mcp_github_search_pull_requests # Search PRs
mcp_github_pull_request_read    # Get PR details, diff, files
mcp_github_create_pull_request  # Create a new PR
mcp_github_merge_pull_request   # Merge a PR

# Repository
mcp_github_get_file_contents    # Read files from GitHub
mcp_github_create_or_update_file # Push file changes
mcp_github_push_files           # Push multiple files in one commit
mcp_github_list_branches        # List branches
mcp_github_create_branch        # Create a new branch

# Code Search
mcp_github_search_code          # Search code across repos
mcp_github_search_repositories  # Find repos
```

### GitHub CLI (for complex operations)
When MCP tools don't provide what you need:

```bash
# List open issues with labels
gh issue list --repo c-daly/logos --state open --label "testing"

# Create an issue
gh issue create --repo c-daly/logos --title "Title" --body "Body"

# Add labels to an issue
gh issue edit 420 --repo c-daly/logos --add-label "infrastructure,testing"

# Add issue to a project
gh project item-add 10 --owner c-daly --url https://github.com/c-daly/logos/issues/420

# List project items
gh project item-list 10 --owner c-daly --format json

# Create a PR
gh pr create --repo c-daly/sophia --title "Title" --body "Body" --base main --head feature-branch

# View PR diff
gh pr diff 64 --repo c-daly/sophia
```

### GraphQL API (for projects and advanced queries)
GitHub Projects (v2) require GraphQL:

```bash
# Get project ID
gh api graphql -f query='
  query {
    user(login: "c-daly") {
      projectV2(number: 10) {
        id
        title
      }
    }
  }
'

# Add an issue to a project (requires project ID and content ID)
gh api graphql -f query='
  mutation {
    addProjectV2ItemById(input: {
      projectId: "PVT_xxxx"
      contentId: "I_xxxx"
    }) {
      item { id }
    }
  }
'

# List issues with full details
gh api graphql -f query='
  query {
    repository(owner: "c-daly", name: "logos") {
      issues(first: 50, states: OPEN) {
        nodes {
          number
          title
          labels(first: 10) { nodes { name } }
          projectItems(first: 5) {
            nodes { project { title } }
          }
        }
      }
    }
  }
'
```

### REST API (simple and direct)
```bash
# Get issue details
gh api repos/c-daly/logos/issues/420

# Update issue labels
gh api repos/c-daly/logos/issues/420 -X PATCH -f labels='["testing","infrastructure"]'

# List all labels in a repo
gh api repos/c-daly/logos/labels

# Create a label
gh api repos/c-daly/logos/labels -X POST -f name="new-label" -f color="ededed"
```

### Common Tasks

**Add an issue to a project:**
```bash
gh project item-add 10 --owner c-daly --url https://github.com/c-daly/logos/issues/420
```

**Add labels to an issue:**
```bash
gh issue edit 420 --repo c-daly/logos --add-label "testing,infrastructure"
```

**Search across all repos:**
```bash
gh search issues "testing" --owner c-daly --state open
```

**Bulk operations (all open issues in a repo):**
```bash
gh issue list --repo c-daly/logos --state open --json number,title --limit 100
```

**Cross-reference issues:**
```bash
# Find all issues mentioning logos#420
gh search issues "logos#420" --owner c-daly
```

### Troubleshooting GitHub access

**"Not authenticated" errors:**
```bash
gh auth status          # Check current auth
gh auth login           # Re-authenticate if needed
```

**"Resource not found" errors:**
- Check the repo name spelling (case-sensitive)
- Verify you have access to the repo
- Try a simpler query first to isolate the issue

**MCP tool returns empty or error:**
- Try the equivalent `gh` CLI command
- Check if the resource exists first
- Use more specific query parameters

**Rate limiting:**
- Wait a few minutes and retry
- Use GraphQL to batch multiple queries
- Cache results when doing bulk operations

---

## Quick reference

| Task | Command |
|------|---------|
| Install deps | `poetry install` |
| Run all tests | `./scripts/run_tests.sh all` |
| Run unit tests | `./scripts/run_tests.sh unit` |
| Full CI locally | `./scripts/run_tests.sh ci` |
| Start infrastructure | `./scripts/run_tests.sh up` |
| Stop infrastructure | `./scripts/run_tests.sh down` |

### Ecosystem standards (defined here)
| Document | Purpose |
|----------|---------|
| `docs/TESTING_STANDARDS.md` | Testing conventions for all repos |
| `docs/GIT_PROJECT_STANDARDS.md` | Git workflow and cross-repo patterns |
