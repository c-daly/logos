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

- **SHACL Validation Service**: REST API for RDF/SHACL validation
  - HTTP API: http://localhost:8081
  - Interactive docs: http://localhost:8081/docs
  - Health check: http://localhost:8081/health
  - Validates data against LOGOS SHACL shapes (ontology/shacl_shapes.ttl)

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
NAME                      IMAGE                    COMMAND                  STATUS
logos-hcg-milvus          milvusdb/milvus:v2.3.3   "/tini -- milvus run…"   Up
logos-hcg-neo4j           neo4j:5.13.0             "tini -g -- /startup…"   Up
logos-shacl-validation    logos-shacl-validation   "python -m uvicorn…"     Up (healthy)
```

### Load the Core Ontology

#### Option 1: Using the Automated Script (Recommended)

```bash
# From the repository root
./infra/load_ontology.sh
```

This script will:
- Check if Neo4j is running and wait for it to be ready
- Load the core ontology constraints, indexes, and concepts
- Verify successful loading with detailed output
- Provide helpful error messages if something goes wrong

#### Option 2: Manual Loading

```bash
# Wait for Neo4j to be ready (may take 10-30 seconds on first start)
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "RETURN 1;"

# Load the ontology
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < ontology/core_ontology.cypher
```

### Initialize Milvus Collections

After starting the cluster, initialize the Milvus collections for HCG embeddings:

```bash
# From the repository root
./infra/init_milvus.sh
```

This script will:
- Check if Milvus is accessible
- Create collections for Entity, Concept, State, and Process embeddings
- Configure indexes for efficient similarity search
- Verify successful creation

The collections use 384-dimensional embeddings by default (suitable for sentence-transformers models). To use a different dimension:

```bash
EMBEDDING_DIM=768 ./infra/init_milvus.sh
```

To force recreation of collections:

```bash
./infra/init_milvus.sh --force
```

To verify collections without creating them:

```bash
./infra/init_milvus.sh --verify-only
```

### Access Neo4j Browser

Open http://localhost:7474 in your browser and connect with:
- URL: `bolt://localhost:7687`
- Username: `neo4j`
- Password: `logosdev`

### Use SHACL Validation Service

The SHACL validation service provides a REST API for validating RDF data:

```bash
# Check service health
curl http://localhost:8081/health

# View interactive API documentation
open http://localhost:8081/docs

# Validate RDF data (example)
curl -X POST http://localhost:8081/validate \
  -H "Content-Type: application/json" \
  -d '{
    "data": "@prefix logos: <http://logos.ontology/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nlogos:entity-test-001 a logos:Entity ;\n    logos:uuid \"entity-test-001\" ;\n    logos:name \"Test Entity\" .",
    "format": "turtle"
  }'

# Get information about loaded SHACL shapes
curl http://localhost:8081/shapes
```

For detailed API documentation and examples, visit http://localhost:8081/docs when the service is running.

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

### Check Milvus Collections

After initializing Milvus collections, verify they exist:

```bash
# Using the Python script
python3 infra/init_milvus_collections.py --verify-only

# Or using pytest
pytest tests/infra/test_milvus_collections.py -v
```

You should see four collections:
- `hcg_entity_embeddings`
- `hcg_concept_embeddings`
- `hcg_state_embeddings`
- `hcg_process_embeddings`

Each collection has the following schema:
- `uuid` (VARCHAR, primary key): Matches Neo4j node UUID
- `embedding` (FLOAT_VECTOR): Vector representation for semantic search
- `embedding_model` (VARCHAR): Model used to generate the embedding
- `last_sync` (INT64): Unix timestamp of last synchronization

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

## Backup and Restore (Development)

**⚠️ Development Use Only**: These scripts are designed for local development snapshots and experimentation. They are NOT suitable for production use.

### Creating a Backup

Create a timestamped backup of all development data (Neo4j + Milvus volumes):

```bash
# From the repository root
./infra/scripts/backup_dev_data.sh
```

This will:
- Pause services cleanly to ensure data consistency
- Backup Neo4j volumes (neo4j-data, neo4j-logs, neo4j-plugins)
- Backup Milvus volume (milvus-data)
- Create a timestamped tarball in `infra/backups/` (e.g., `backup-20240118-1430.tar.gz`)
- Resume services automatically
- Print backup location and size

**Custom output location:**
```bash
./infra/scripts/backup_dev_data.sh --output /tmp/my-backup.tar.gz
```

**Expected downtime:** Services are paused for the duration of the backup (typically 10-30 seconds for small dev datasets, longer for larger data).

### Restoring from a Backup

Restore data from a previous backup archive:

```bash
# From the repository root
./infra/scripts/restore_dev_data.sh infra/backups/backup-20240118-1430.tar.gz
```

This will:
- Verify the backup archive is valid and contains all required volumes
- Display backup metadata (timestamp, volumes included)
- Ask for confirmation before overwriting existing data
- Stop services
- Restore all volumes from the archive
- Restart services and wait for them to be ready
- Verify services are accessible

**Skip confirmation prompt:**
```bash
./infra/scripts/restore_dev_data.sh infra/backups/backup-20240118-1430.tar.gz --force
```

**Expected downtime:** Services are stopped during restore (typically 30-60 seconds plus service startup time).

### Typical Workflow

```bash
# 1. Create a baseline backup before experiments
./infra/scripts/backup_dev_data.sh

# 2. Run experiments, make changes, test things out
# ... work with your data ...

# 3. If something goes wrong, restore from the backup
./infra/scripts/restore_dev_data.sh infra/backups/backup-YYYYMMDD-HHMM.tar.gz

# 4. Or create another backup after successful changes
./infra/scripts/backup_dev_data.sh
```

### Requirements

- Docker and Docker Compose must be installed and running
- Services must be running for backup (they will be paused automatically)
- Services will be stopped for restore (they will be restarted automatically)
- Sufficient disk space for backup archives (size depends on data volume)

### Notes

- Backups are stored in `infra/backups/` which is gitignored
- Backup archives include metadata (timestamp, volume names, compose file used)
- Restore validates archive contents before overwriting data
- Both scripts use POSIX shell features only (no bash-specific features for portability)
- Scripts handle errors gracefully and always attempt to resume/restart services

## Integration with LOGOS Components

- **Sophia**: Connects to Neo4j for HCG operations and Milvus for semantic search; can use SHACL validation endpoint to validate graph updates
- **Hermes**: Does not access HCG directly (stateless utilities)
- **Talos**: May log sensor data to HCG in future phases
- **Apollo**: Visualizes HCG state via Neo4j queries; can use SHACL validation endpoint to validate user inputs

The SHACL validation service provides programmatic validation for any component that needs to validate RDF data against the LOGOS ontology shapes.

See the main [README.md](../README.md) and specification in `docs/spec/project_logos_full.md` for more details.
