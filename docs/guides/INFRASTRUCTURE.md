# Infrastructure Setup

## Overview

LOGOS requires two databases:
- **Neo4j** - Graph database for the Hybrid Cognitive Graph (HCG)
- **Milvus** - Vector database for semantic embeddings

Optional:
- **OpenTelemetry** - Observability (Jaeger, Prometheus)
- **SHACL Service** - RDF/SHACL validation

## Quick Start (Development)

```bash
cd ~/projects/LOGOS/logos

# Start Neo4j + Milvus
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Verify
docker compose -f infra/docker-compose.hcg.dev.yml ps
```

Services:
| Service | URL | Credentials |
|---------|-----|-------------|
| Neo4j Browser | http://localhost:7474 | neo4j / neo4jtest |
| Neo4j Bolt | bolt://localhost:7687 | neo4j / neo4jtest |
| Milvus gRPC | localhost:19530 | - |
| Milvus Health | http://localhost:9091/healthz | - |

## Initialize the HCG

After starting infrastructure, load the ontology:

```bash
# Load core ontology into Neo4j
./infra/load_ontology.sh

# Initialize Milvus collections
./infra/init_milvus.sh

# Verify everything
python3 infra/check_hcg_health.py
```

## Stopping Infrastructure

```bash
# Stop (preserves data)
docker compose -f infra/docker-compose.hcg.dev.yml down

# Stop and delete all data
docker compose -f infra/docker-compose.hcg.dev.yml down -v
```

## Test Infrastructure

For running integration tests, each repo has its own docker-compose with unique ports:

```bash
# Sophia tests (47xxx ports)
cd ~/projects/LOGOS/sophia
docker compose -f docker-compose.test.yml up -d

# Talos tests (57xxx ports)
cd ~/projects/LOGOS/talos
docker compose -f tests/e2e/stack/talos/docker-compose.test.yml up -d
```

See [Testing Guide](TESTING.md) for port allocation details.

## Neo4j

### Connection

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "neo4jtest")
)
```

### Useful Cypher Queries

```cypher
-- Count all nodes
MATCH (n) RETURN count(n);

-- Show node types
MATCH (n) RETURN DISTINCT labels(n), count(*);

-- Find entities
MATCH (e:Entity) RETURN e LIMIT 10;

-- Clear everything (careful!)
MATCH (n) DETACH DELETE n;
```

## Milvus

### Connection

```python
from pymilvus import connections

connections.connect(host="localhost", port="19530")
```

### Collections

LOGOS uses these collections:
| Collection | Dimension | Purpose |
|------------|-----------|---------|
| `entity_embeddings` | 768 | Entity semantic vectors |
| `concept_embeddings` | 768 | Concept semantic vectors |
| `state_embeddings` | 768 | State semantic vectors |
| `hermes_embeddings` | 384 | Hermes text embeddings |

### Useful Commands

```python
from pymilvus import utility, Collection

# List collections
utility.list_collections()

# Get collection info
col = Collection("entity_embeddings")
print(col.num_entities)
```

## Observability (Optional)

Start the observability stack:

```bash
docker compose -f docker-compose.otel.yml up -d
```

Services:
| Service | URL | Purpose |
|---------|-----|---------|
| Jaeger | http://localhost:16686 | Trace visualization |
| Prometheus | http://localhost:9090 | Metrics |
| OTEL Collector | localhost:4317 | Telemetry ingestion |

Configure services to export telemetry:
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

## Docker Resource Requirements

| Service | Min RAM | Recommended |
|---------|---------|-------------|
| Neo4j | 1GB | 2GB |
| Milvus | 2GB | 4GB |
| Total | 4GB | 8GB |

Allocate at least 4GB RAM to Docker Desktop.

## Troubleshooting

**Neo4j won't start**
```bash
# Check logs
docker logs logos-hcg-neo4j

# Common fix: remove corrupted data
docker compose -f infra/docker-compose.hcg.dev.yml down -v
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```

**Milvus health check fails**
```bash
# Milvus takes ~30-60s to initialize
# Wait and retry
sleep 60
curl http://localhost:9091/healthz
```

**Port already in use**
```bash
# Find the process
lsof -i :7474

# Kill it or change ports in docker-compose
```

**Out of disk space**
```bash
# Clean up Docker
docker system prune -a --volumes
```
