# ADR-0002: Use Milvus for Vector Storage

**Status:** Accepted

**Date:** 2024-01 (Phase 1 Foundation)

**Decision Makers:** Project LOGOS Core Team

**Related Issues:** Phase 1 HCG Foundation, Vector Embedding Strategy

## Context and Problem Statement

Project LOGOS implements a Hybrid Causal Graph (HCG) that combines symbolic reasoning (Neo4j) with semantic similarity search. The system needs to store and query high-dimensional vector embeddings for:
- Semantic search over HCG nodes and relationships
- Finding conceptually similar entities, states, and processes
- Grounding natural language queries to graph structures
- Perceptual similarity for future vision/audio inputs

The vector storage solution must support:
- High-dimensional embeddings (768-1536 dimensions typical for modern language models)
- Approximate nearest neighbor (ANN) search at scale
- Integration with Neo4j for hybrid symbolic-semantic queries
- Development and production deployment flexibility

Which vector database should we use to complement Neo4j in the HCG architecture?

## Decision Drivers

* **Hybrid architecture**: Must integrate cleanly with Neo4j for combined graph + vector queries
* **Similarity search performance**: Sub-second ANN queries for thousands of vectors
* **Embedding dimension flexibility**: Support for various embedding models (BERT, sentence-transformers, etc.)
* **Index types**: Multiple index options (FLAT, IVF, HNSW) for accuracy/speed tradeoffs
* **Scalability**: Horizontal scaling for future production workloads
* **Open source**: No vendor lock-in, deployable anywhere
* **Developer experience**: Simple API, good Python support, Docker deployment

## Considered Options

* **Option 1**: Milvus (open-source vector database)
* **Option 2**: Pinecone (managed vector database service)
* **Option 3**: Weaviate (vector database with built-in vectorization)
* **Option 4**: FAISS library + custom persistence layer
* **Option 5**: Neo4j native vector indexes (experimental in Neo4j 5+)

## Decision Outcome

Chosen option: "Milvus", because it provides a mature, open-source vector database with excellent ANN performance, multiple index types, Docker-based deployment, and strong Python SDK support. It allows us to keep vector storage separate from graph storage while maintaining clean integration patterns.

### Positive Consequences

* Purpose-built for vector similarity search with optimized ANN algorithms
* Multiple index types (FLAT, IVF_FLAT, IVF_SQ8, HNSW) for accuracy/speed tuning
* Clean separation of concerns between graph (Neo4j) and vector (Milvus) stores
* Docker-based development environment matches Neo4j deployment pattern
* Open-source with active community and regular releases
* Horizontal scaling via distributed architecture for production
* Python SDK (`pymilvus`) integrates naturally with project stack
* No vendor lock-in or cloud platform dependency

### Negative Consequences

* Adds Milvus as a second mandatory infrastructure dependency
* Requires synchronization logic to keep Neo4j and Milvus consistent
* Increases system complexity compared to single-database solution
* Dual-database queries require application-level orchestration
* Additional operational overhead for monitoring and backup

## Pros and Cons of the Options

### Milvus (open-source vector database)

* Good, because purpose-built for vector similarity search
* Good, because supports multiple ANN index types with tunable accuracy/speed
* Good, because Docker deployment matches Neo4j infrastructure pattern
* Good, because open-source with no licensing restrictions
* Good, because scales horizontally for production workloads
* Good, because active development and strong community
* Bad, because adds second database to infrastructure
* Bad, because requires application-level consistency management
* Bad, because steeper learning curve than embedding-as-service options

### Pinecone (managed vector database)

* Good, because fully managed service reduces operational burden
* Good, because auto-scaling and high availability built-in
* Good, because simple API with excellent documentation
* Bad, because vendor lock-in to cloud service
* Bad, because recurring costs scale with usage (expensive for research phase)
* Bad, because requires internet connectivity (no local-only development)
* Bad, because less control over index configuration and tuning

### Weaviate (vector database with built-in vectorization)

* Good, because includes built-in text-to-vector modules
* Good, because supports hybrid search (keyword + vector) natively
* Good, because open-source with Docker deployment
* Bad, because built-in vectorization couples us to specific embedding models
* Bad, because more complex than pure vector storage (features we don't need)
* Bad, because smaller community than Milvus
* Bad, because less mature ANN algorithms compared to Milvus

### FAISS library + custom persistence

* Good, because Facebook-backed with excellent performance
* Good, because most control over index configuration
* Good, because no database dependency (just a library)
* Bad, because requires building custom persistence layer
* Bad, because no built-in distributed architecture
* Bad, because significant engineering effort for production features
* Bad, because reinventing database functionality (backup, replication, etc.)

### Neo4j native vector indexes

* Good, because single database simplifies architecture
* Good, because no synchronization needed between graph and vectors
* Good, because unified query language
* Bad, because vector search is experimental/preview feature (as of Neo4j 5.13)
* Bad, because limited index types and configuration options
* Bad, because less mature than purpose-built vector databases
* Bad, because couples graph and vector scaling requirements

## Links

* Related to [ADR-0001](0001-use-neo4j-for-graph-database.md) - HCG hybrid architecture
* Related to [ADR-0005](0005-vector-embedding-strategy.md) - Embedding generation strategy
* Infrastructure defined in `infra/docker-compose.hcg.dev.yml`
* Initialization script in `infra/init_milvus.sh`

## References

* [Milvus Vector Database](https://milvus.io/)
* [Milvus Python SDK Documentation](https://milvus.io/docs/install-pymilvus.md)
* [ANN Benchmarks](http://ann-benchmarks.com/) - Vector search performance comparison
* Project LOGOS Specification: Section 4.2 (Hybrid Causal Graph Architecture)
* Project LOGOS Specification: Section 5.2 (Infrastructure and Deployment)
