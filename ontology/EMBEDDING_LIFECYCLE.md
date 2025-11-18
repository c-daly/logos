# HCG Embedding Lifecycle Documentation

## Overview

This document describes the lifecycle of vector embeddings in the Hybrid Causal Graph (HCG), implementing Section 4.2 of the Project LOGOS specification.

The HCG uses a **hybrid storage architecture**:
- **Neo4j**: Stores graph structure, relationships, and node properties
- **Milvus**: Stores vector embeddings for semantic similarity search

Each graph node maintains **bidirectional sync** with its vector representation through metadata fields.

## Embedding Metadata Fields

Each HCG node type (Entity, Concept, State, Process) includes three metadata fields:

| Field | Type | Description |
|-------|------|-------------|
| `embedding_id` | String | Reference to vector in Milvus (matches node UUID) |
| `embedding_model` | String | Model used to generate the embedding (e.g., "sentence-transformers/all-MiniLM-L6-v2") |
| `last_sync` | DateTime | Timestamp of last synchronization with Milvus |

These fields are **optional** and only populated when semantic search is needed for a node.

## Milvus Collection Schema

Milvus stores embeddings in four collections (one per node type):

- `hcg_entity_embeddings`
- `hcg_concept_embeddings`
- `hcg_state_embeddings`
- `hcg_process_embeddings`

### Collection Fields

Each collection has the following schema:

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | VARCHAR(256) | Primary key, matches Neo4j node UUID |
| `embedding` | FLOAT_VECTOR(384) | Vector embedding for semantic search |
| `embedding_model` | VARCHAR(128) | Model used to generate the embedding |
| `last_sync` | INT64 | Unix timestamp of last synchronization |

**Note**: The default embedding dimension is 384, suitable for sentence-transformers models like `all-MiniLM-L6-v2`. This can be configured during initialization.

## Lifecycle Stages

### 1. Node Creation (Neo4j)

When a new node is created in Neo4j:

```python
from logos_hcg import HCGClient

client = HCGClient(uri="bolt://localhost:7687", user="neo4j", password="password")

# Create node (embedding fields initially None)
# Node is created without embedding
```

**State**: Node exists in Neo4j, no embedding in Milvus yet.

### 2. Embedding Generation

Generate embeddings using Hermes (or other embedding service):

```python
# Call Hermes /embed_text endpoint (see contracts/hermes.openapi.yaml)
# POST /embed_text
# {
#   "text": "Entity description or relevant text",
#   "model": "sentence-transformers/all-MiniLM-L6-v2"
# }
# Response: {"embedding": [0.1, 0.2, ...], "model": "..."}
```

**State**: Embedding vector computed but not yet stored.

### 3. Embedding Upsert (Milvus)

Store the embedding in Milvus and update Neo4j metadata:

```python
from logos_hcg import HCGMilvusSync

# Sync embedding to Milvus
with HCGMilvusSync(milvus_host="localhost", milvus_port="19530") as sync:
    metadata = sync.upsert_embedding(
        node_type="Entity",
        uuid="entity-uuid-here",
        embedding=[0.1, 0.2, ...],  # From Hermes
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    
# Update Neo4j node with metadata
# SET node.embedding_id = metadata["embedding_id"],
#     node.embedding_model = metadata["embedding_model"],
#     node.last_sync = metadata["last_sync"]
```

**State**: Node has embedding in both Neo4j (metadata) and Milvus (vector).

### 4. Semantic Search

Query Milvus for similar nodes:

```python
from pymilvus import Collection

# Search for similar entities
collection = Collection("hcg_entity_embeddings")
results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param={"metric_type": "L2", "params": {"nprobe": 10}},
    limit=10,
    output_fields=["uuid", "embedding_model", "last_sync"]
)

# Retrieve full node data from Neo4j using UUIDs from results
```

**State**: Semantic similarity search returns related nodes.

### 5. Node Update

When a node's semantic content changes (e.g., description updated):

1. **Mark for re-embedding**: The `last_sync` field can be used to track staleness
2. **Regenerate embedding**: Call Hermes again with updated text
3. **Upsert to Milvus**: Use `upsert_embedding()` to replace the old vector
4. **Update Neo4j metadata**: Update `last_sync` timestamp

```python
# After updating node description in Neo4j
with HCGMilvusSync() as sync:
    metadata = sync.upsert_embedding(
        node_type="Entity",
        uuid="entity-uuid",
        embedding=new_embedding,
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
# Update Neo4j with new last_sync
```

**State**: Embedding and metadata updated to reflect node changes.

### 6. Node Deletion

When a node is deleted from Neo4j, its embedding must be removed from Milvus:

```python
with HCGMilvusSync() as sync:
    sync.delete_embedding(
        node_type="Entity",
        uuid="entity-uuid"
    )

# Then delete from Neo4j
# MATCH (n:Entity {uuid: "entity-uuid"}) DELETE n
```

**State**: Node and embedding removed from both stores.

## Batch Operations

For efficiency, embeddings can be processed in batches:

### Batch Upsert

```python
embeddings = [
    {"uuid": "uuid-1", "embedding": [...], "model": "all-MiniLM-L6-v2"},
    {"uuid": "uuid-2", "embedding": [...], "model": "all-MiniLM-L6-v2"},
    # ...
]

with HCGMilvusSync() as sync:
    metadata_list = sync.batch_upsert_embeddings(
        node_type="Entity",
        embeddings=embeddings
    )
# Update Neo4j nodes with corresponding metadata
```

### Batch Delete

```python
uuids = ["uuid-1", "uuid-2", "uuid-3"]

with HCGMilvusSync() as sync:
    count = sync.batch_delete_embeddings(
        node_type="Entity",
        uuids=uuids
    )
print(f"Deleted {count} embeddings")
```

## Consistency Verification

Verify that Neo4j and Milvus are in sync:

```python
from logos_hcg import HCGClient, HCGMilvusSync

# Get all Entity UUIDs from Neo4j
client = HCGClient(...)
entities = client.find_all_entities()
neo4j_uuids = {str(e.uuid) for e in entities}

# Compare with Milvus
with HCGMilvusSync() as sync:
    report = sync.verify_sync(
        node_type="Entity",
        neo4j_uuids=neo4j_uuids
    )
    
if not report["in_sync"]:
    print(f"Found {len(report['orphaned_embeddings'])} orphaned embeddings")
    print(f"Found {len(report['missing_embeddings'])} missing embeddings")
```

Report structure:
```python
{
    "in_sync": bool,
    "neo4j_count": int,
    "milvus_count": int,
    "orphaned_embeddings": list[str],  # In Milvus but not Neo4j
    "missing_embeddings": list[str],   # In Neo4j but not Milvus
}
```

## Health Checks

Check Milvus connection and collection status:

```python
with HCGMilvusSync() as sync:
    health = sync.health_check()
    
print(f"Connected: {health['connected']}")
for node_type, status in health["collections"].items():
    print(f"{node_type}: {status['count']} embeddings")
```

Health report structure:
```python
{
    "connected": bool,
    "collections": {
        "Entity": {"exists": bool, "loaded": bool, "count": int},
        "Concept": {"exists": bool, "loaded": bool, "count": int},
        "State": {"exists": bool, "loaded": bool, "count": int},
        "Process": {"exists": bool, "loaded": bool, "count": int}
    }
}
```

## Integration with Hermes

The typical flow for semantic search integration:

1. **Node Creation**: Create node in Neo4j (via Sophia)
2. **Text Extraction**: Extract semantic content (name, description, etc.)
3. **Embedding Generation**: POST to Hermes `/embed_text` endpoint
4. **Embedding Storage**: Use `HCGMilvusSync.upsert_embedding()`
5. **Metadata Update**: Update Neo4j node with embedding metadata
6. **Semantic Query**: Use Milvus to find similar nodes by vector similarity
7. **Graph Enrichment**: Retrieve full node data from Neo4j using UUIDs

## Best Practices

### When to Generate Embeddings

- **Concepts**: Always embed (needed for semantic type matching)
- **Entities**: Embed if semantic search is needed for entity discovery
- **States**: Embed sparingly (states are temporal, embeddings less useful)
- **Processes**: Embed for action similarity and planning

### Model Selection

- **Default**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, fast)
- **High Quality**: `sentence-transformers/all-mpnet-base-v2` (768 dimensions)
- **Domain-Specific**: Fine-tuned models for robotics/manipulation domain

### Performance Considerations

- **Batch Operations**: Use `batch_upsert_embeddings()` for bulk loads
- **Lazy Embedding**: Only generate embeddings when semantic search is needed
- **Index Type**: Default `IVF_FLAT` is good for development; use `HNSW` for production
- **Staleness**: Regenerate embeddings when node semantic content changes significantly

### Error Handling

- **Connection Failures**: Use context managers (`with HCGMilvusSync()`) for automatic cleanup
- **Missing Collections**: Run `init_milvus_collections.py` to initialize
- **Sync Inconsistencies**: Run `verify_sync()` periodically and repair orphaned/missing embeddings

## Initialization Scripts

### Create Milvus Collections

```bash
# From repository root
python infra/init_milvus_collections.py --host localhost --port 19530

# Or use the shell script
./infra/init_milvus.sh
```

### Verify Collections

```bash
python infra/init_milvus_collections.py --verify-only
```

## Example: End-to-End Workflow

Complete example of creating a node with embedding:

```python
from uuid import uuid4
from datetime import datetime
from logos_hcg import HCGClient, HCGMilvusSync
import requests

# 1. Create node in Neo4j
entity_uuid = str(uuid4())
with HCGClient(uri="bolt://localhost:7687", user="neo4j", password="password") as client:
    query = """
    CREATE (e:Entity {
        uuid: $uuid,
        name: $name,
        description: $description,
        created_at: datetime()
    })
    RETURN e
    """
    client._execute_query(query, {
        "uuid": entity_uuid,
        "name": "Coffee Cup",
        "description": "A ceramic cup for holding hot beverages"
    })

# 2. Generate embedding via Hermes
response = requests.post(
    "http://hermes:8000/embed_text",
    json={
        "text": "Coffee Cup: A ceramic cup for holding hot beverages",
        "model": "sentence-transformers/all-MiniLM-L6-v2"
    }
)
embedding_data = response.json()

# 3. Store embedding in Milvus
with HCGMilvusSync(milvus_host="localhost", milvus_port="19530") as sync:
    metadata = sync.upsert_embedding(
        node_type="Entity",
        uuid=entity_uuid,
        embedding=embedding_data["embedding"],
        model=embedding_data["model"]
    )

# 4. Update Neo4j with embedding metadata
with HCGClient(uri="bolt://localhost:7687", user="neo4j", password="password") as client:
    query = """
    MATCH (e:Entity {uuid: $uuid})
    SET e.embedding_id = $embedding_id,
        e.embedding_model = $embedding_model,
        e.last_sync = $last_sync
    RETURN e
    """
    client._execute_query(query, {
        "uuid": entity_uuid,
        "embedding_id": metadata["embedding_id"],
        "embedding_model": metadata["embedding_model"],
        "last_sync": metadata["last_sync"].isoformat()
    })

print(f"Created entity {entity_uuid} with embedding")
```

## Troubleshooting

### Collection Not Found

```
MilvusSyncError: Collection for Entity not loaded
```

**Solution**: Initialize Milvus collections:
```bash
python infra/init_milvus_collections.py
```

### Connection Refused

```
MilvusSyncError: Failed to connect to Milvus: [Errno 111] Connection refused
```

**Solution**: Ensure Milvus is running:
```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d milvus-standalone
```

### Dimension Mismatch

```
Dimension mismatch: expected 384, got 768
```

**Solution**: Ensure embedding model output matches collection dimension (384 for default).

### Orphaned Embeddings

If `verify_sync()` reports orphaned embeddings:

```python
# Clean up orphaned embeddings
with HCGMilvusSync() as sync:
    sync.batch_delete_embeddings(
        node_type="Entity",
        uuids=report["orphaned_embeddings"]
    )
```

## References

- **Project LOGOS Spec**: See Section 4.2 (Vector Integration)
- **Milvus Documentation**: https://milvus.io/docs
- **Sentence Transformers**: https://www.sbert.net/
- **Hermes API Contract**: `contracts/hermes.openapi.yaml`
