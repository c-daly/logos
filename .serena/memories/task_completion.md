# Task Completion Checklist

## Before Committing

### Required Checks
```bash
# 1. Lint check
poetry run ruff check .

# 2. Format check
poetry run ruff format --check .

# 3. Type check
poetry run mypy <modified-packages>/

# 4. Unit tests (at minimum)
./scripts/run_tests.sh unit
```

### If Modifying Behavior
```bash
# Run integration tests
./scripts/run_tests.sh integration

# If affecting multiple services
./scripts/run_tests.sh e2e
```

### Full CI Parity
```bash
./scripts/run_tests.sh ci
```

## Commit Message Format
- Reference issue: `Closes #420` or `Part of #420`
- Use imperative mood: "Add feature" not "Added feature"
- Keep first line under 72 characters

## Pull Request Checklist
1. [ ] Tests pass locally
2. [ ] Code is linted and formatted
3. [ ] Type hints added for new public functions
4. [ ] PR description includes summary and testing notes
5. [ ] Issue referenced in PR body
6. [ ] Downstream impact noted (if applicable)

## Cross-Repo Changes
If change affects downstream repos (sophia, hermes, talos, apollo):
1. Create tracking issue in logos
2. Update contracts/ontology in logos first
3. Create consistent branch names across repos: `chore/logos420-feature`
4. Reference tracking issue from each PR: `Part of c-daly/logos#420`

## Infrastructure Cleanup
```bash
# Stop test containers when done
./scripts/run_tests.sh down
```

## Ontology Changes
If modifying `ontology/*.cypher` or `ontology/shacl_shapes.ttl`:
1. Run SHACL validation: `python ontology/validate_ontology.py`
2. Update SHACL_COVERAGE.md if adding new shapes
3. Test with load scripts: `python ontology/load_and_validate_shacl.py`
