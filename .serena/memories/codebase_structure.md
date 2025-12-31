# Codebase Structure

## Root Layout
```
logos/
├── contracts/           # OpenAPI specifications
├── ontology/            # Cypher schemas + SHACL shapes
├── docs/                # Documentation
│   ├── standards/       # TESTING_STANDARDS.md, GIT_PROJECT_STANDARDS.md
│   ├── architecture/    # Architecture docs
│   ├── api/             # API documentation
│   └── scratch/         # Temporary working docs
├── .github/workflows/   # Reusable CI workflows
├── scripts/             # Dev/test scripts
├── infra/               # Infrastructure configs
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests (require Docker)
│   └── e2e/             # End-to-end tests
├── config/              # Configuration files
├── examples/            # Example usage
└── experiments/         # Experimental notebooks/code
```

## Python Packages
```
logos_config/            # Shared config (env, ports, settings, health)
logos_hcg/               # HCG client (client.py, queries.py, models.py)
logos_sophia/            # Sophia SDK stubs
logos_perception/        # Perception utilities
logos_cwm_e/             # CWM-E (Episodic memory)
logos_persona/           # Persona management
logos_observability/     # OpenTelemetry helpers
logos_test_utils/        # Shared test utilities
logos_tools/             # CLI tools (generate_issues, create_issues_by_epoch)
planner_stub/            # Planner stub implementation
```

## Key Files
| File | Purpose |
|------|---------|
| `pyproject.toml` | Poetry config, tool settings |
| `AGENTS.md` | Agent instructions for this repo |
| `ontology/core_ontology.cypher` | Core HCG ontology |
| `ontology/shacl_shapes.ttl` | SHACL validation shapes |
| `logos_hcg/queries.py` | Pre-built Cypher queries |
| `logos_config/ports.py` | Port allocation per repo |

## Test Organization
- `tests/unit/` - Fast, mocked, no infrastructure
- `tests/integration/` - Real Neo4j/Milvus via Docker
- `tests/e2e/` - Full service stack

## Generated/Excluded
- `sdk/` - Generated Python SDK (excluded from lint)
- `sdk-web/` - Generated TypeScript SDK (excluded from lint)
- `.venv/` - Virtual environment
- `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` - Caches
