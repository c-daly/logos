# ADR-0005: Vector Embedding Strategy

**Status:** Accepted

**Date:** 2024-01 (Phase 1 Foundation)

**Decision Makers:** Project LOGOS Core Team

**Related Issues:** Phase 1 HCG Foundation, Semantic Search

## Context and Problem Statement

The Hybrid Causal Graph (HCG) combines symbolic reasoning (Neo4j) with semantic similarity search (Milvus). To enable semantic search, we need to generate vector embeddings for:
- HCG nodes (Entity, Concept, State, Process descriptions)
- Natural language queries from Apollo
- Future perceptual inputs (images, audio, sensor data)

The embedding strategy must address:
- Which embedding model(s) to use
- How to generate embeddings for structured graph data
- When to create/update embeddings (synchronous vs. asynchronous)
- How to maintain consistency between Neo4j and Milvus
- Tradeoffs between embedding quality, dimensionality, and performance

What strategy should we use for generating and managing vector embeddings in the HCG?

## Decision Drivers

* **Semantic accuracy**: Embeddings must capture meaningful similarity for HCG content
* **Dimension flexibility**: Support different embedding models (384d to 1536d)
* **Hermes integration**: Leverage Hermes stateless embedding endpoint
* **Graph structure awareness**: Consider how to embed nodes with relationships
* **Synchronization strategy**: Keep Neo4j and Milvus consistent
* **Phase 1 simplicity**: Start with pragmatic approach, plan for future sophistication
* **Multi-modal future**: Architecture must extend to images, audio, sensor data

## Considered Options

* **Option 1**: Stateless embedding via Hermes with text-based node descriptions
* **Option 2**: Graph neural network (GNN) embeddings trained on HCG structure
* **Option 3**: Large language model (LLM) contextualized embeddings
* **Option 4**: Hybrid approach combining multiple embedding types

## Decision Outcome

Chosen option: "Stateless embedding via Hermes with text-based node descriptions", because it provides immediate value with minimal complexity. Each HCG node is serialized to a text description (name + properties + relationship context) and embedded via Hermes's `/embed_text` endpoint. This approach:
- Leverages existing Hermes infrastructure
- Works with any embedding model backend
- Keeps Sophia decoupled from embedding model choice
- Provides foundation for future enhancements

### Positive Consequences

* Simple to implement and reason about (text → vector pipeline)
* Hermes's stateless API makes embedding generation testable without infrastructure
* Can swap embedding models by reconfiguring Hermes (no Sophia changes)
* Works with any sentence-transformer compatible model
* Clear synchronization model: embed when node is created/updated
* Text serialization is human-readable for debugging
* Supports gradual enhancement (add relationship context, multi-hop descriptions, etc.)

### Negative Consequences

* Text serialization may lose graph structure information
* Synchronous embedding on write may add latency
* Must decide what to include in text descriptions (may need tuning)
* Embedding consistency requires careful synchronization logic
* Simple concatenation may not optimally represent structured data
* No inherent awareness of causal relationships in embeddings

## Pros and Cons of the Options

### Stateless embedding via Hermes

* Good, because leverages existing Hermes infrastructure
* Good, because decouples Sophia from embedding model choice
* Good, because text serialization is human-readable and debuggable
* Good, because works with any sentence-transformer model
* Good, because simple synchronization model (embed on write)
* Good, because testable without running embedding models locally
* Bad, because text serialization may not capture graph structure
* Bad, because naive concatenation may not be optimal representation
* Bad, because synchronous embedding adds write latency

### Graph neural network (GNN) embeddings

* Good, because learns structural patterns from HCG graph
* Good, because embeddings capture multi-hop relationships
* Good, because can incorporate causal relationship types (CAUSES, etc.)
* Good, because state-of-the-art for graph representation learning
* Bad, because requires training on HCG data (cold start problem)
* Bad, because training pipeline adds significant complexity
* Bad, because embeddings are opaque (hard to debug)
* Bad, because requires GPU infrastructure for training
* Bad, because overkill for Phase 1 scope

### LLM contextualized embeddings

* Good, because LLMs have rich world knowledge
* Good, because can generate context-aware descriptions
* Good, because handles multi-hop graph context naturally
* Bad, because expensive (API costs or local GPU inference)
* Bad, because non-deterministic (same node may embed differently)
* Bad, because slower than lightweight embedding models
* Bad, because contradicts LOGOS philosophy (linguistic dependency)
* Bad, because adds complexity for marginal Phase 1 benefit

### Hybrid approach

* Good, because combines strengths of multiple methods
* Good, because can use different embeddings for different purposes
* Good, because future-proof (supports gradual enhancement)
* Bad, because significant implementation complexity
* Bad, because must manage multiple embedding spaces
* Bad, because harder to reason about and debug
* Bad, because premature optimization for Phase 1

## Implementation Strategy

### Node Serialization Format

```python
def serialize_node(node: HCGNode) -> str:
    """Serialize HCG node to text for embedding."""
    parts = [
        f"{node.type}: {node.name}",
        node.description or "",
    ]
    
    # Include key relationships for context
    if node.relationships:
        rel_context = ", ".join([
            f"{rel.type} {rel.target.name}" 
            for rel in node.relationships[:5]  # Limit context
        ])
        parts.append(f"Context: {rel_context}")
    
    return " | ".join(filter(None, parts))

# Example output:
# "Entity: blue_block | A small blue wooden block | Context: IS_A Block, LOCATED_AT Table, HAS_STATE Idle"
```

### Embedding Generation

```python
def embed_node(node: HCGNode) -> np.ndarray:
    """Generate embedding for HCG node via Hermes."""
    text = serialize_node(node)
    response = hermes_client.post("/embed_text", json={"text": text})
    return np.array(response.json()["embedding"])
```

### Synchronization Strategy

| Operation | Neo4j | Milvus | Timing |
|-----------|-------|--------|--------|
| **Create node** | Write node | Write embedding | Synchronous (atomic) |
| **Update node** | Update properties | Update embedding | Synchronous |
| **Delete node** | Delete node | Delete embedding | Synchronous |
| **Bulk import** | Batch write | Batch embed & write | Asynchronous (background job) |

### Embedding Model Selection (Phase 1)

Default: `all-MiniLM-L6-v2` (384 dimensions)
- Fast inference (~100ms per embedding)
- Good quality for general semantic similarity
- Lightweight (80MB model)
- Well-supported by sentence-transformers

Future options (configurable via Hermes):
- `all-mpnet-base-v2` (768d) - higher quality
- `multilingual-e5-large` (1024d) - multilingual support
- OpenAI `text-embedding-3-small` (1536d) - via API

## Future Extensions

Phase 2+ enhancements may include:
- **Asynchronous embedding**: Background workers for bulk operations
- **Multi-modal embeddings**: Vision transformers for images, audio embeddings
- **Graph-aware serialization**: Include multi-hop causal context
- **Learned serialization**: Train model to generate optimal text descriptions
- **Hierarchical embeddings**: Separate embeddings for different abstraction levels
- **Incremental updates**: Only re-embed changed portions of descriptions

## Links

* Related to [ADR-0002](0002-use-milvus-for-vector-storage.md) - Milvus integration
* Hermes embedding endpoint: `contracts/hermes.openapi.yaml` (POST /embed_text)
* Milvus initialization: `infra/init_milvus.sh`

## References

* [Sentence Transformers](https://www.sbert.net/) - Embedding model library
* [Milvus Documentation](https://milvus.io/docs) - Vector database integration
* [Hermes API Contract](../../contracts/hermes.openapi.yaml)
* Project LOGOS Specification: Section 3.4 (Hermes API endpoints)
* Project LOGOS Specification: Section 4.2 (Hybrid Causal Graph architecture)
