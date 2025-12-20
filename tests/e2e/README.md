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
# Start the test stack
./tests/e2e/run_e2e.sh up

# Seed test data (load ontology, init Milvus collections)
./tests/e2e/run_e2e.sh seed

# Run tests
./tests/e2e/run_e2e.sh test

# Check status
./tests/e2e/run_e2e.sh status

# Stop the stack
./tests/e2e/run_e2e.sh down

# Full cleanup (including volumes)
./tests/e2e/run_e2e.sh clean
```

## Regenerating Stack Files

The stack files are generated from the shared template in `infra/test_stack/`:

```bash
poetry run render-test-stacks --repo logos
```

## Services

The test stack includes:

- **Neo4j 5.13.0** - Graph database (ports 7474, 7687)
- **Milvus v2.4.15** - Vector database (ports 37530 gRPC, 37091 metrics)
  - etcd v3.5.15 - Milvus metadata store
  - MinIO - Milvus object storage (ports 9000, 9001)
