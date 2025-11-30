# LOGOS Test Stack Port Reference

**Quick reference for test environment port assignments.**

## Port Map

| Service | logos (default) | apollo | hermes | sophia | talos |
|---------|----------------|--------|--------|--------|-------|
| **Neo4j HTTP** | 7474 | 27474 | N/A | 37474 | 47474 |
| **Neo4j Bolt** | 7687 | 27687 | N/A | 37687 | 47687 |
| **Milvus gRPC** | 19530 | 29530 | 19530 | 39530 | N/A |
| **Milvus Metrics** | 9091 | 29091 | 19091 | 39091 | N/A |

## Connection Strings by Repo

### logos (default/dev)
```bash
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest
MILVUS_HOST=milvus
MILVUS_PORT=19530
```

### apollo
```bash
NEO4J_URI=bolt://neo4j:27687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest
MILVUS_HOST=milvus
MILVUS_PORT=29530
```

### hermes
```bash
# Hermes only uses Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530
```

### sophia
```bash
NEO4J_URI=bolt://neo4j:37687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest
MILVUS_HOST=milvus
MILVUS_PORT=39530
```

### talos
```bash
# Talos only uses Neo4j
NEO4J_URI=bolt://neo4j:47687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jtest
```

## Container Name Prefixes

- `logos-phase2-test-*` (logos repo)
- `apollo-test-*` (apollo repo)
- `hermes-test-*` (hermes repo)
- `sophia-test-*` (sophia repo)
- `talos-test-*` (talos repo)

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
docker compose -f tests/e2e/docker-compose.test.apollo.yml ps

# Check health
docker inspect apollo-test-neo4j | grep -A 10 Health
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
