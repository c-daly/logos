# E2E Test Infrastructure

This directory contains end-to-end test infrastructure for LOGOS.

## Structure

```
tests/e2e/
├── README.md           # This file
├── run_e2e.sh          # Helper script to manage test stack
└── stack/
    ├── logos/          # LOGOS-specific stack (generated)
    │   ├── docker-compose.test.yml
    │   ├── .env.test
    │   └── STACK_VERSION
    └── shared/         # Shared resources (if any)
```

## Quick Start

```bash
# Full cycle: start stack, seed data, run pytest, and tear down
./tests/e2e/run_e2e.sh
# (equivalent to ./tests/e2e/run_e2e.sh test)

# Start the test stack only
./tests/e2e/run_e2e.sh up

# Seed test data (load ontology, init Milvus collections)
./tests/e2e/run_e2e.sh seed

# Check status
./tests/e2e/run_e2e.sh status

# Stop the stack
./tests/e2e/run_e2e.sh down

# Full cleanup (including volumes)
./tests/e2e/run_e2e.sh clean
```

## Environment Variables

`tests/e2e/stack/logos/.env.test` is the canonical schema used by Docker Compose,
helper scripts, and downstream repositories. The `run_e2e.sh` helper sources this
file automatically so the variables are available to `pytest`, seed scripts, and
any custom commands.

| Variable | Description | Default |
| --- | --- | --- |
| `NEO4J_URI` | Bolt endpoint exposed by the stack | `bolt://neo4j:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `logosdev` |
| `NEO4J_CONTAINER` | Neo4j docker container name | `logos-phase2-test-neo4j` |
| `MILVUS_HOST` | Milvus hostname inside the stack | `milvus` |
| `MILVUS_PORT` | Milvus gRPC port | `19530` |
| `MILVUS_HEALTHCHECK` | Milvus health endpoint | `http://milvus:9091/healthz` |
| `MILVUS_CONTAINER` | Milvus docker container name | `logos-phase2-test-milvus` |

> **Tip:** The integration tests also auto-detect the running container names. If
you prefer to keep the legacy dev stack running (`logos-hcg-neo4j`), set the
`NEO4J_CONTAINER` environment variable before invoking `pytest`.

## Regenerating Stack Files

The stack files are generated from the shared template in `infra/test_stack/`:

```bash
poetry run render-test-stacks --repo logos
```

## Services

The test stack includes:

- **Neo4j 5.13.0** - Graph database (ports 7474, 7687)
- **Milvus v2.4.15** - Vector database (port 19530)
  - etcd v3.5.15 - Milvus metadata store
  - MinIO - Milvus object storage (ports 9000, 9001)
