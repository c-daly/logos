# LOGOS Stack Integration Plan

## Goal
Full Apollo → Hermes → Sophia → HCG integration with standardization per-repo.

## Critical Issue
**sophia #14** - CWM read APIs (G/A/E) are the linchpin. CWM-E supports persona system.

## Phases
- Phase 1: Sophia (logos_config, CWM APIs, /execute, feedback)
- Phase 2: Hermes (run_tests.sh, receive feedback, /llm with context)  
- Phase 3: Apollo (configurable URLs, connect APIs)
- Phase 4: Flexible ontology tickets

## Key Issues
- sophia: #14 ✅, #15 ✅, #16 ✅, #65 ✅, #74 ✅ — **Phase 1 COMPLETE**
- hermes: #50+#26, #66, #17 — **Phase 2 IN PROGRESS**
  - Order: standardization → provenance → feedback
  - Deferred: #38, #42 (test infra, post-stack)
- logos: #279, #423, #433
- apollo: (no active tickets)

## Artifacts
- docs/scratch/stack-integration/IMPLEMENTATION_PLAN.md
- docs/scratch/stack-integration/HANDOFF.md

## Context7 Library IDs
- FastAPI: /websites/fastapi_tiangolo
- Neo4j Python: /neo4j/neo4j-python-driver
- Cypher Manual: /websites/neo4j_cypher-manual_25


## CWM Schema Design (2025-12-31)

Type hierarchy added to core_ontology.cypher:
```
cognition (internal cognitive structures)
  ├── cwm [COMPONENT_OF]
  │     ├── cwm_a (abstract reasoning)
  │     ├── cwm_g (grounded/JEPA)
  │     └── cwm_e (emotional/persona)
  └── persona [COMPONENT_OF]
```

Edge types:
- IS_A: type inheritance
- COMPONENT_OF: structural grouping

API: Unified GET /cwm returns all types, Hermes filters as needed.

## CWM Persistence Implementation (2025-12-31) - COMPLETE

### PRs Merged
- logos #466 - CWM state queries in HCGQueries
- logos #468 - CWM ontology types + test fixes
- sophia #102 - CWM persistence layer and GET /cwm endpoint
- sophia #103 - Standardization (logging, middleware, API v1 routes)

### Files
- `sophia/src/sophia/cwm/persistence.py` - CWMPersistence class
- `sophia/src/sophia/api/app.py` - GET /cwm endpoint + standardization
- `logos/logos_hcg/queries.py` - create_cwm_state(), find_cwm_states()
- `logos/ontology/core_ontology.cypher` - CWM type definitions

### Test Infrastructure Fixes
- `logos/scripts/test_integration.sh` - Use logos_config.LOGOS_PORTS (was hardcoded)
- `logos/tests/integration/ontology/test_neo4j_crud.py` - Remove flawed assertion

### Key Decisions
- Reuse existing CWMState model from cwm_a.state_service (no duplication)
- Flexible ontology: Node label with type property (cwm_a, cwm_g, cwm_e)
- GET /cwm queries Neo4j; GET /state/cwm returns in-memory history

### Tickets Closed
- sophia #14 - CWM persistence (closed with #102)
- sophia #74 - Standardization (closed with #103)
- sophia #65 - Execute endpoint (closed 2025-12-31)

### In Progress
- sophia #16 - Feedback emission (PR #105 merged, closed)

---

## Provenance Metadata Implementation (2026-01-02) - COMPLETE

### PRs Merged
- sophia #106 - Add provenance metadata to HCG nodes
- logos #471 - Simplify CWMState envelope for provenance

### Implementation
- `add_node()` accepts provenance params: source, derivation, confidence, tags, links
- `update_node()` method for updating nodes with timestamp refresh
- Type definitions seeder (`seed_type_definitions()`)
- All API endpoints pass provenance to HCG client
- CWMState envelope simplified (provenance in `data`)
- Unit tests for provenance and seeder config

### Files Modified
- `sophia/src/sophia/hcg_client/client.py` - add_node provenance params, update_node method
- `sophia/src/sophia/hcg_client/seeder.py` - type definitions seeding
- `sophia/src/sophia/api/app.py` - all endpoints pass provenance
- `logos/contracts/sophia.openapi.yaml` - simplified CWMState schema

### Remaining
- Hermes ingestion should pass provenance when calling Sophia (new hermes ticket)

---

## State Architecture Design (2026-01-01) - COMPLETE

Design decisions documented, informed #15 provenance implementation.

### Design Decisions
- **Memory tiers:** Ephemeral → Mid-term (HCG + expires_at) → Long-term (HCG, no expiry)
- **No Redis tier:** Just `expires_at` field presence/absence
- **CWM layers:** A/G/E are lenses on same graph, not silos - cross-layer edges allowed
- **Promotion:** Via salience score (method TBD, factors identified)
- **Planning contracts:** Domain-specific content, common interface (PlanState, Action protocols)

### Key Files
- `logos/docs/plans/2026-01-01-state-architecture-design.md` - Full design doc
- `sophia/docs/scratch/sophia-15-provenance/` - Research and intake
- `sophia/.serena/memories/state_architecture_design_decisions.md` - Decision summary

### Next Steps
1. Define "session" more precisely (for #101)
2. Clarify attention/focus mechanism
3. Add cross-layer edge examples
4. Scope #15 to Plan provenance only
5. Define planning contracts formally in code
