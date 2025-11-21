# ADR-0001: Use Neo4j for Graph Database

**Status:** Accepted

**Date:** 2024-01 (Phase 1 Foundation)

**Decision Makers:** Project LOGOS Core Team

**Related Issues:** Phase 1 HCG Foundation

## Context and Problem Statement

Project LOGOS requires a graph database to implement the Hybrid Causal Graph (HCG), which represents the agent's knowledge as nodes (Entity, Concept, State, Process) and relationships (IS_A, HAS_STATE, CAUSES, PART_OF). The database must support:
- Complex graph queries with multiple hops
- Causal relationship traversal
- Temporal ordering of states and processes
- Property constraints and uniqueness guarantees
- Integration with validation frameworks
- Development and production scalability

Which graph database technology should we use as the foundation for the HCG?

## Decision Drivers

* **Causal reasoning requirements**: Need to efficiently traverse and query causal relationships (CAUSES, PRECEDES)
* **Cypher query language**: Expressive graph query language reduces implementation complexity
* **Constraint support**: Built-in uniqueness constraints and indexing for UUID-based identity
* **SHACL integration**: Ability to integrate with RDF/SHACL validation through plugins
* **Developer experience**: Mature tooling, documentation, and community support
* **Deployment flexibility**: Docker-based development with cloud deployment options
* **Performance**: Sub-millisecond query performance for small-to-medium graphs (Phase 1 scope)

## Considered Options

* **Option 1**: Neo4j (labeled property graph database)
* **Option 2**: Amazon Neptune (managed graph database, supports both property graph and RDF)
* **Option 3**: PostgreSQL with recursive CTEs (relational with graph query capabilities)
* **Option 4**: ArangoDB (multi-model database with graph support)

## Decision Outcome

Chosen option: "Neo4j", because it provides the most mature labeled property graph implementation with excellent Cypher query language support, built-in constraint enforcement, and proven integration patterns for SHACL validation via the neosemantics (n10s) plugin.

### Positive Consequences

* Cypher query language aligns naturally with HCG ontology structure
* Built-in uniqueness constraints enforce UUID requirements (see `ontology/core_ontology.cypher`)
* Neo4j Browser provides visual debugging for graph structure during development
* Extensive documentation and community resources available
* neosemantics (n10s) plugin enables RDF/SHACL integration (see ADR-0003)
* Docker-based deployment simplifies Phase 1 infrastructure (`infra/docker-compose.hcg.dev.yml`)
* Strong Python driver support via official `neo4j` package

### Negative Consequences

* Adds Neo4j as a mandatory infrastructure dependency
* Licensing considerations for production deployment (Community vs. Enterprise)
* Learning curve for team members unfamiliar with Cypher
* Vendor-specific query language (less portable than SQL or SPARQL)

## Pros and Cons of the Options

### Neo4j (labeled property graph)

* Good, because Cypher is purpose-built for graph traversal and reads like pseudocode
* Good, because constraint system enforces HCG invariants at database level
* Good, because n10s plugin provides SHACL validation integration path
* Good, because Neo4j Browser provides excellent visual debugging
* Good, because mature Python driver with connection pooling and transaction support
* Bad, because introduces vendor-specific query language
* Bad, because Community Edition has limitations on clustering/high availability
* Bad, because licensing costs for Enterprise features in production

### Amazon Neptune

* Good, because fully managed service reduces operational overhead
* Good, because supports both property graph (Gremlin) and RDF (SPARQL)
* Good, because automatic backups and high availability built-in
* Bad, because requires AWS infrastructure commitment
* Bad, because less mature Gremlin/SPARQL tooling compared to Cypher
* Bad, because local development requires emulators or cloud access
* Bad, because higher cost for Phase 1 experimental/research workload

### PostgreSQL with recursive CTEs

* Good, because already familiar to most developers
* Good, because mature, battle-tested technology
* Good, because no additional infrastructure dependency
* Bad, because recursive CTE syntax is verbose and error-prone for complex graph queries
* Bad, because no native graph visualization tools
* Bad, because performance degrades significantly with deep graph traversals
* Bad, because constraint modeling for graph structures is awkward in relational schema

### ArangoDB (multi-model)

* Good, because supports multiple data models (document, graph, key-value)
* Good, because AQL query language is familiar to SQL users
* Good, because flexible schema evolution
* Bad, because less mature than Neo4j for pure graph workloads
* Bad, because smaller community and fewer learning resources
* Bad, because no established SHACL integration pattern
* Bad, because multi-model flexibility adds complexity we don't need

## Links

* Related to [ADR-0002](0002-use-milvus-for-vector-storage.md) - HCG hybrid architecture
* Related to [ADR-0003](0003-shacl-for-level-1-validation.md) - Validation integration
* Implemented in `ontology/core_ontology.cypher`
* Infrastructure defined in `infra/docker-compose.hcg.dev.yml`

## References

* [Neo4j Graph Database](https://neo4j.com/)
* [Cypher Query Language](https://neo4j.com/developer/cypher/)
* [neosemantics (n10s) Plugin](https://neo4j.com/labs/neosemantics/)
* Project LOGOS Specification: Section 4.1 (Core Ontology and Data Model)
* Project LOGOS Specification: Section 5.2 (Infrastructure and Deployment)
