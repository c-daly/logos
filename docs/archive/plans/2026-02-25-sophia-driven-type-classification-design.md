# Sophia-Driven Type Classification

**Date**: 2026-02-25
**Status**: Approved
**Scope**: hermes, sophia, logos (foundry)

## Problem

Hermes currently assigns HCG node types during NER extraction, using either spaCy label mapping or LLM classification against a fixed ontology vocabulary. This leads to misclassification (e.g., "13th century" tagged as `state` because spaCy maps DATE to state, conflating temporal references with CWM states). More fundamentally, type ownership belongs with Sophia — the cognitive core that understands the graph's structure — not with the language service.

## Design

Sophia takes ownership of type classification using the geometric structure of the embedding space. Hermes continues to extract entity names, spans, embeddings, and relationship labels, but stops being the type authority.

### Architecture: Hybrid Centroid + k-NN

Two different similarity mechanisms serve different goals:

- **Centroids** for type assignment — fast, coarse-grained categorical classification
- **k-NN** for relationship discovery — fine-grained cross-cluster proximity detection

### Component 1: Type Centroids

Each type_definition node is represented by a centroid embedding stored in a dedicated `hcg_type_centroids` Milvus collection. The centroid is the running average of all member node embeddings.

Seed types (location, object, entity, concept, etc.) are bootstrapped by embedding their descriptions via Hermes (e.g., embed "a geographic or spatial place" for the location type).

Neo4j type_definition nodes gain scalar properties:
- `member_count: int`
- `centroid_variance: float` (average L2 distance of members from centroid)
- `parent_type: str` (uuid of parent type_definition, for emerged sub-types)

Centroid update on node assignment:
```
new_centroid = (old_centroid * member_count + new_embedding) / (member_count + 1)
```

### Component 2: Ingestion-Time Classification

When Sophia receives a proposal, for each proposed node:

1. **Type assignment** — Search `hcg_type_centroids` for nearest centroid(s). Assign the closest type with confidence proportional to inverse L2 distance. If ambiguous (between centroids), assign closest with low confidence and flag `needs_reclassification = true`.

2. **Deduplication** — Search the assigned type's Milvus collection for nearest neighbors (existing L2 < 0.5 threshold). If match found, skip creation and map to existing node.

3. **Node creation** — Create node in Neo4j with assigned type, confidence, and IS_A edge to type_definition. Upsert embedding to type's Milvus collection. Update type centroid incrementally.

Node properties gain:
- `type_confidence: float` (0.0-1.0)
- `needs_reclassification: bool`

### Component 3: Cross-Cluster Relationship Discovery

Separate from type assignment, Sophia uses k-NN to discover candidate relationships:

1. **Cross-collection search** — For a given node, search all type Milvus collections except its own type for k nearest neighbors.

2. **Candidate filtering** — A cross-cluster neighbor is a relationship candidate if it's closer to the query node than it is to its own type centroid. This filters out nodes near cluster boundaries that aren't meaningfully related.

3. **Hermes naming** — For each candidate pair, ask Hermes to name the relationship via `POST /name-relationship`. Sophia creates the reified edge.

Runs opportunistically on ingestion (obvious cross-cluster neighbors) and more thoroughly during reflection passes.

### Component 4: Type Emergence

During reflection passes or when triggered by low-confidence ingestion:

1. **Variance monitoring** — When a type's `centroid_variance` exceeds a threshold, it signals the type may be too broad.

2. **Split detection** — Run k-means (k=2) on the high-variance type's member embeddings. If the two sub-clusters have significantly lower internal variance than the parent, it's a real split.

3. **Hermes naming** — Send node names from each sub-cluster to Hermes via `POST /name-type` to get a name for the new type.

4. **Type creation** — Create new type_definition with sub-cluster centroid, IS_A edge to parent type (preserving hierarchy), reassign member nodes, update Milvus collections.

5. **Low-confidence resolution** — Re-evaluate `needs_reclassification` nodes against updated centroids.

k=2 splits are deliberately conservative. Deeper splits emerge over multiple reflection cycles.

### Component 5: New Hermes Endpoints

Two new endpoints for Sophia to consult Hermes's linguistic capabilities:

- `POST /name-type` — Given a list of node names forming a cluster, return a descriptive type name.
- `POST /name-relationship` — Given two node names and optional context, return an edge label.

These are separate endpoints to allow independent method/model/prompt evolution.

### Component 6: Hermes Deprecations

- `proposed_nodes[].type` — Deprecated. Hermes continues sending it for backward compatibility and provenance, but Sophia ignores it for classification.
- `ONTOLOGY_TYPES` in `ner_provider.py` — No longer authoritative. Sophia owns the type vocabulary.
- LLM type classification instructions in the NER system prompt — Deprecated. Hermes extracts entity names and spans only.

### What Doesn't Change

- Hermes NER (entity name/span extraction)
- Hermes edge extraction from text (relation_extractor pipeline)
- Hermes embedding generation (all-MiniLM-L6-v2)
- Dedup threshold (L2 < 0.5), now applied within Sophia-assigned type collections
- Reified edge graph structure
- SHACL validation

## Data Model Changes

### New Milvus Collection
- `hcg_type_centroids` — one embedding per type_definition (uuid, embedding, embedding_model, last_sync)

### Neo4j type_definition Node Additions
- `member_count: int`
- `centroid_variance: float`
- `parent_type: str` (uuid)

### Neo4j Node Additions
- `type_confidence: float`
- `needs_reclassification: bool`

### New Hermes Endpoints
- `POST /name-type`
- `POST /name-relationship`

### Deprecated
- `proposed_nodes[].type` field (kept, ignored by Sophia)
