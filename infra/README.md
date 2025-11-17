# LOGOS Infrastructure

This directory contains the development infrastructure configuration for the LOGOS ecosystem.

## Overview

The `docker-compose.hcg.dev.yml` file provides a complete local development environment with:

- **Neo4j 5.13.0**: Graph database for the Hybrid Causal Graph (HCG)
  - HTTP interface: http://localhost:7474
  - Bolt protocol: bolt://localhost:7687
  - Default credentials: `neo4j/logosdev`
  - Plugins: APOC (graph-data-science and n10s will attempt to install if available)

- **Milvus v2.3.3**: Vector database for semantic search
  - gRPC endpoint: localhost:19530
  - Metrics endpoint: http://localhost:9091

## Quick Start

### Start the HCG Development Cluster

```bash
# From the repository root
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```

### Verify Services are Running

```bash
docker compose -f infra/docker-compose.hcg.dev.yml ps
```

Expected output:
```
NAME               IMAGE                    COMMAND                  STATUS
logos-hcg-milvus   milvusdb/milvus:v2.3.3   "/tini -- milvus run…"   Up
logos-hcg-neo4j    neo4j:5.13.0             "tini -g -- /startup…"   Up
```

### Load the Core Ontology

```bash
# Wait for Neo4j to be ready (may take 10-30 seconds on first start)
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "RETURN 1;"

# Load the ontology
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/core_ontology.cypher
```

### Access Neo4j Browser

Open http://localhost:7474 in your browser and connect with:
- URL: `bolt://localhost:7687`
- Username: `neo4j`
- Password: `logosdev`

### Stop the Cluster

```bash
docker compose -f infra/docker-compose.hcg.dev.yml down
```

### Remove All Data (Clean Slate)

```bash
docker compose -f infra/docker-compose.hcg.dev.yml down -v
```

## Verification

### Check Neo4j Constraints

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "SHOW CONSTRAINTS;"
```

You should see uniqueness constraints for:
- `logos_entity_uuid`
- `logos_concept_uuid`
- `logos_concept_name`
- `logos_state_uuid`
- `logos_process_uuid`

### Check Neo4j Indexes

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "SHOW INDEXES;"
```

You should see indexes for entity names, state timestamps, and process timestamps.

### Check APOC Procedures

```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc' RETURN count(name) AS apoc_count;"
```

## Plugin Notes

### APOC
APOC is installed automatically and provides essential graph algorithms and utilities.

### Graph Data Science (GDS) and Neosemantics (n10s)
These plugins may not auto-install for all Neo4j versions due to version compatibility. For Phase 1 development, APOC is sufficient for basic ontology operations. If you need these plugins:

1. Check compatibility at:
   - GDS: https://neo4j.com/docs/graph-data-science/current/installation/
   - n10s: https://neo4j.com/labs/neosemantics/

2. Manually download and install compatible versions into the Neo4j plugins directory

## Networking

All services run on a shared Docker bridge network `logos-hcg-dev-net` for inter-service communication.

## Data Persistence

Data is persisted in Docker volumes:
- `neo4j-data`: Graph database data
- `neo4j-logs`: Neo4j logs
- `milvus-data`: Vector database data

These volumes survive container restarts but can be removed with the `-v` flag.

## Troubleshooting

### Neo4j Won't Start

Check logs:
```bash
docker logs logos-hcg-neo4j
```

### Milvus Won't Start

Check logs:
```bash
docker logs logos-hcg-milvus
```

### Port Conflicts

If ports 7474, 7687, 19530, or 9091 are already in use, modify the port mappings in `docker-compose.hcg.dev.yml`.

### Performance Issues

For better performance, allocate more resources to Docker:
- Memory: At least 4GB recommended
- CPU: 2+ cores recommended

## Integration with LOGOS Components

- **Sophia**: Connects to Neo4j for HCG operations and Milvus for semantic search
- **Hermes**: Does not access HCG directly (stateless utilities)
- **Talos**: May log sensor data to HCG in future phases
- **Apollo**: Visualizes HCG state via Neo4j queries

See the main [README.md](../README.md) and specification in `docs/spec/project_logos_full.md` for more details.
