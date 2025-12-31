# Session Handoff - 2025-12-31

## Current Task
CWM (Causal World Model) persistence implementation complete. Ready for SDK regeneration when needed.

## Status
- Phase: CWM persistence implemented
- Progress: GET /cwm endpoint added to Sophia, persistence layer complete
- Blockers: None

## What Was Done This Session

### CWM Persistence Implementation

1. **`sophia/src/sophia/cwm/persistence.py`** - Refactored to:
   - Reuse existing `CWMState` model from `cwm_a.state_service` (no duplication)
   - `persist()` - Writes CWMState envelope to Neo4j using flexible ontology
   - `find_states()` - Queries Neo4j with type/timestamp/limit filters
   - Added proper type annotations

2. **`sophia/src/sophia/cwm/__init__.py`** - Simplified exports to `CWMPersistence` only

3. **`logos/logos_hcg/queries.py`** - Updated `create_cwm_state()`:
   - Added `links` field for CWMStateLinks serialization
   - Added `tags` field for state tagging

4. **`sophia/src/sophia/api/app.py`** - Added:
   - Import and initialization of `CWMPersistence` in lifespan
   - **New endpoint `GET /cwm`** for querying persisted states

### New Endpoint: GET /cwm

Query parameters:
- `types` - Comma-separated CWM types (cwm_a, cwm_g, cwm_e)
- `after_timestamp` - ISO timestamp filter
- `limit` - Max results (1-100, default 20)

Purpose: Hermes can query historical cognitive states for LLM context.

### Architecture

```
Sophia API
├── /state/cwm - In-memory CWM-A history (ephemeral)
└── /cwm - Neo4j persisted states (long-term) ← NEW
         ↓
    CWMPersistence
         ↓
    Neo4j (via HCGQueries.create_cwm_state / find_cwm_states)
```

## Branch
`feature/logos458-flexible-ontology`

## Key Files Modified
- `sophia/src/sophia/cwm/persistence.py`
- `sophia/src/sophia/cwm/__init__.py`
- `sophia/src/sophia/api/app.py`
- `logos/logos_hcg/queries.py`

## Previous Session Work (2025-12-30)

### Ticket Consolidation
- Closed #408, #393 (superseded/merged)
- Created sub-issues #460-#465 under #458

### Neo4j/n10s Compatibility
- Changed Neo4j 5.14.0 → 5.11.0 for n10s compatibility

### HCGQueries Methods
Added 14 methods for flexible ontology support.

## Next Steps
1. SDK regeneration when API changes finalized
2. **#462** - Update pick-and-place test data
3. **#460** - Update sophia planner queries
4. **#463** - Validate M4 demo end-to-end
5. **#464** - Un-skip and fix M3 planning tests

## Open Design Questions

### Ephemeral nodes and session boundaries
- Ephemeral CWM nodes need real graph relationships to persisted nodes
- Current in-memory model breaks when edges to Neo4j nodes are needed
- Proposed: Write ephemeral to Neo4j with `status: ephemeral`, cleanup on "session end"
- **Undefined**: What constitutes a "session"? (process lifetime, conversation boundary, time-based, explicit ID?)
- Consider: Unified `/cwm` endpoint that shows both ephemeral and persisted states

## Notes
- CWM = Causal World Model (not Continuous Working Memory)
- Status values: `observed`, `imagined`, `reflected`, `ephemeral` (provenance)
- CWM-A is the only subsystem with real implementation; CWM-G is stub, CWM-E doesn't exist yet
