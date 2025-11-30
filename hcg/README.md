# Hybrid Cognitive Graph (HCG) Documentation

Ontology, SHACL constraints, and Causal World Model (CWM) schemas.

## Overview

The Hybrid Cognitive Graph (HCG) is LOGOS's graph-based knowledge representation that blends:
- **Symbolic reasoning** via Neo4j graph structures
- **Semantic search** via Milvus vector embeddings
- **Constraint validation** via SHACL shapes

## Documents

| Document | Description |
|----------|-------------|
| [CWM_STATE.md](CWM_STATE.md) | Unified CWMState envelope for CWM-A/G/E layers |

## CWM Layers

| Layer | Name | Purpose |
|-------|------|---------|
| CWM-A | Abstract | Symbolic entities, concepts, causal rules |
| CWM-G | Grounded | Sensor data, predictions, physics properties |
| CWM-E | Emotional | Diary entries, reflections, persona state |

## Related Resources

- [Architecture Specs](../architecture/) - Full system specifications
- [Ontology Files](../../ontology/) - Cypher and SHACL definitions
- [SDK Documentation](../sdk/) - Client library for HCG access
