# LOGOS Test Stack Port Reference

**Quick reference for test environment port assignments.**

## Port Map (current logos test stack)

| Service | Port |
|---------|------|
| **Neo4j HTTP** | 7474 |
| **Neo4j Bolt** | 7687 |
| **Milvus gRPC** | 19530 |
| **Milvus Metrics** | 9091 |
| **OTLP gRPC (collector)** | 4319 |
| **OTLP HTTP (collector)** | 4320 |
| **Prometheus UI** | 9090 |
| **Jaeger UI** | 16686 |

> Ports reflect the generated test stack (`infra/test_stack/repos.yaml` and `tests/e2e/stack/logos/docker-compose.test.yml`). If you regenerate stacks for other repos, confirm the rendered ports in the compose output instead of relying on old offsets.

## Connection Strings (logos test stack)
```bash
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest
MILVUS_HOST=milvus
MILVUS_PORT=19530
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4319
```

## Container Name Prefixes

- `logos-phase2-test-*` (logos repo)

## Finding Your Containers

```bash
# See all LOGOS test containers
docker ps --filter "name=test"

# Check specific repo
docker ps --filter "name=apollo-test"
```

## Why These Ports?

- **logos**: Standard ports (7xxx, 19xxx) - "home base"
- **apollo**: 2xxxx range - easy to remember "2=Apollo"
- **hermes**: Uses logos' Milvus (no Neo4j in tests)
- **sophia**: 3xxxx range
- **talos**: 4xxxx range (only Neo4j)

## Common Issues

### Port Already in Use
```bash
# Find what's using a port
lsof -i :7687

# Stop conflicting container
docker stop $(docker ps -q --filter "name=test")
```

### Can't Connect to Service
```bash
# Check service is running
docker compose -f tests/e2e/stack/logos/docker-compose.test.yml ps

# Check health
docker inspect logos-phase2-test-neo4j | grep -A 10 Health
```

## Quick Start Commands

```bash
# Start your repo's test stack
docker compose -f tests/e2e/docker-compose.test.{REPO}.yml up -d

# Run tests
poetry run pytest tests/

# Stop stack
docker compose -f tests/e2e/docker-compose.test.{REPO}.yml down
```
