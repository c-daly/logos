# Suggested Commands for Logos Development

## Installation
```bash
poetry install                    # Install all dependencies
poetry install --with dev,test   # Include dev and test groups
```

## Testing
```bash
./scripts/run_tests.sh unit         # Run unit tests only
./scripts/run_tests.sh integration  # Run integration tests
./scripts/run_tests.sh e2e          # Run end-to-end tests
./scripts/run_tests.sh all          # Run all tests
./scripts/run_tests.sh ci           # Full CI parity (lint + test)
./scripts/run_tests.sh up           # Start test infrastructure
./scripts/run_tests.sh down         # Stop test infrastructure
./scripts/run_tests.sh clean        # Clean volumes and restart

poetry run pytest tests/unit/       # Direct pytest (unit)
poetry run pytest -m integration    # Direct pytest (integration marker)
```

## Linting and Formatting
```bash
poetry run ruff check .             # Check for linting errors
poetry run ruff check --fix .       # Auto-fix safe issues
poetry run ruff format .            # Format code
poetry run ruff format --check .    # Check formatting only
poetry run mypy logos_hcg/ logos_config/  # Type check specific packages
```

## Git Workflow
```bash
# Branch naming: {kind}/{repo}{issue-number}-{short-kebab}
git checkout -b feature/logos420-new-feature

# Never push directly to main - always use PRs
```

## Docker/Infrastructure
```bash
docker logs logos-test-neo4j        # Check Neo4j logs
docker logs logos-test-milvus       # Check Milvus logs
lsof -i :37474                      # Check port usage

# Environment for manual testing
export NEO4J_URI=bolt://localhost:37687
export MILVUS_HOST=localhost
export MILVUS_PORT=37530
```

## GitHub CLI
```bash
gh issue list --repo c-daly/logos --state open
gh pr create --title "Title" --body "Body"
gh project item-add 10 --owner c-daly --url <issue-url>
```

## Utility
```bash
poetry run python -m logos_tools.generate_issues  # Generate issues
render-test-stacks                                 # Render infra stacks
```
