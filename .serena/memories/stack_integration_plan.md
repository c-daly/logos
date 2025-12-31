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
- sophia: #14, #16, #65, #74
- hermes: #17, #50
- logos: #279, #423, #433
- apollo: #314

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

## CWM Persistence Implementation (2025-12-31)

Files:
- `sophia/src/sophia/cwm/persistence.py` - CWMPersistence class
- `sophia/src/sophia/api/app.py` - GET /cwm endpoint
- `logos/logos_hcg/queries.py` - create_cwm_state(), find_cwm_states()

Key decisions:
- Reuse existing CWMState model from cwm_a.state_service (no duplication)
- Flexible ontology: Node label with type property (cwm_a, cwm_g, cwm_e)
- GET /cwm queries Neo4j; GET /state/cwm returns in-memory history
