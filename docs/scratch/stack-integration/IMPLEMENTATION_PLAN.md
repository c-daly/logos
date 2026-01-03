# LOGOS Stack Integration Plan

## Goal
Fully functioning Apollo webapp that speaks to Hermes, with Hermes speaking to Sophia and receiving HCG annotations, and Sophia sending Cypher queries to update HCG.

## Architecture Target

```
┌─────────────────────────────────────────────────────────────────────┐
│                            APOLLO                                    │
│  React webapp + CLI                                                  │
│  - Calls Hermes /llm for conversations                              │
│  - Calls Sophia /plan, /execute, /state for cognitive ops           │
│  - WebSocket for real-time feedback                                  │
└─────────────────────┬───────────────────────────────────────────────┘
                      │ SDK calls
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────────┐   ┌─────────────────────────────────────────┐
│       HERMES        │   │                SOPHIA                    │
│  STT/TTS/NLP/LLM    │   │  Orchestrator + Planner + CWM (G/A/E)   │
│                     │   │                                          │
│  /llm (with context)│◄──┤  GET /cwm (unified), /api/v1/* routes   │
│  /embed_text        │   │  POST /plan, /execute, /state            │
│  /stt, /tts         │   │  Feedback events ──────────────────────►│
│                     │   │                                          │
│  (needs logos_hcg   │   │  Uses logos_hcg for all Neo4j ops       │
│   for annotations)  │   │                                          │
└─────────────────────┘   └────────────────┬──────────────────────────┘
                                           │
                                           ▼
                          ┌─────────────────────────────────────────┐
                          │              HCG (Neo4j + Milvus)        │
                          │  via logos_hcg from logos foundry        │
                          └─────────────────────────────────────────┘
```

---

## Phase 1: Sophia Foundation

### 1A: Standardization (sophia) - COMPLETE
**Issues**: #74 (closed), part of #433

**Completed via PR #103 (2025-12-31)**:
- [x] Add `logos_config` dependency to pyproject.toml
- [x] Replace manual env handling with `logos_config.env` helpers
- [x] Replace health endpoint with `LogosHealthResponse` schema
- [x] Adopt logging: `setup_logging("sophia")` from logos_test_utils
- [x] Add `RequestIDMiddleware` for request tracing
- [x] Add `/api/v1/` route aliases for all endpoints
- [x] Verify ruff/mypy configs match logos standards

### 1B: CWM Persistence & APIs (sophia #14) - PARTIAL
**The critical integration enabler**

**Completed via sophia PR #102 + logos PR #466 (2025-12-31)**:
- [x] Design CWM schema using flexible ontology (Node label with type property)
- [x] Implement persistence layer: `sophia/src/sophia/cwm/persistence.py`
  - `CWMPersistence` class wraps HCGClient
  - Methods: `save_state()`, `get_states()`, `get_latest_state()`
- [x] Implement `GET /cwm` endpoint (unified - returns all CWM types)
  - Queries Neo4j via HCGQueries.find_cwm_states()
  - Filters by cwm_type (cwm_a, cwm_g, cwm_e)
- [x] Add HCGQueries methods: `create_cwm_state()`, `find_cwm_states()`
- [x] CWM types bootstrapped in `ontology/core_ontology.cypher`:
  - cognition → cwm → cwm_a, cwm_g, cwm_e
  - Uses COMPONENT_OF edge for structural grouping

**Sophia flexible ontology migration - COMPLETE (PR #104, merged 2026-01-01)**:
- [x] Update sophia internal code to use flexible ontology patterns
- [x] Audit sophia Cypher queries for old type-label references
- [x] Update sophia tests for flexible ontology
- [x] "Hermes proposes, Sophia disposes" - proposals logged, not stored
- [x] See logos #461 (sophia audit complete, can close)

**API Design Decision**: Single `GET /cwm` endpoint with type filter, not separate `/cwm/g`, `/cwm/a`, `/cwm/e`. Hermes can filter as needed.

**Key Files**:
- `sophia/src/sophia/cwm/persistence.py` - CWMPersistence class
- `sophia/src/sophia/api/app.py` - GET /cwm endpoint
- `logos/logos_hcg/queries.py` - CWM query methods
- `logos/ontology/core_ontology.cypher` - CWM type definitions

### 1C: Fix /execute Endpoint (sophia #65) - COMPLETE
**Verified 2026-01-01** - Endpoint works correctly:
- [x] Fetches plan from Neo4j by plan_id
- [x] Iterates through plan steps
- [x] Returns results for each step
- [x] Supports dry_run, step_index, state tracking
- [x] 10 integration tests pass
- [x] Simulation mode (appropriate - no Talos hardware yet)

**Commit**: 356bb22 (un-skipped test, closed #65)

### 1D: Emit Feedback to Hermes (sophia #16) - COMPLETE
**Completed 2026-01-02**:
- [x] Design feedback event schema
- [x] Implement event emission from planner/executor
- [x] Redis-backed feedback queue with exponential backoff
- [x] FeedbackDispatcher and FeedbackWorker components
- [x] Graceful degradation when Redis unavailable

---

## Phase 2: Hermes Integration - COMPLETE

### 2A: Standardization (hermes) - COMPLETE
**Issues**: #50, #55, #56, #60 (all closed)

**Completed 2025-12 to 2026-01**:
- [x] Adopt logos_config, health schema, logging (#50)
- [x] Standardize ports to +10000 offset (#55, #56)
- [x] Align CI/test stacks to logos_config ports (#60)
- [x] CI uses reusable workflows
- [x] Provenance metadata when calling Sophia APIs (#66)

### 2B: Receive Sophia Feedback (hermes #17) - COMPLETE
**Completed**: Integrated via Redis queue (sophia #16 provides, hermes consumes)

### 2C: LLM Endpoint with Context (logos #279) - COMPLETE
**Completed** (logos #279 still open - wasn't linked to PR):
- [x] `/llm` endpoint implemented in hermes/src/hermes/main.py
- [x] LLM provider abstraction in hermes/src/hermes/llm.py
- [x] LLMRequest/LLMResponse models

---

## Phase 3: Apollo Integration

### 3A: Standardization (apollo #131) - COMPLETE
**Completed 2026-01-03 via PR #141**:
- [x] Verify logos_config usage (apollo.env wraps it)
- [x] Make API URLs configurable via env/config (get_sophia_config, etc.)
- [x] Delete orphaned root docker files
- [x] Refactor e2e/conftest.py to use apollo.env
- [x] Fix container config (NEO4J_HOST, not NEO4J_URI)
- [x] CI uses reusable workflows
- [ ] Update vendored SDKs → use published from logos (still pending)

### 3B: Connect to New APIs
**Tasks**:
- [ ] Update hermes-client.ts to use /llm with context
- [ ] Update sophia-client.ts to use new CWM endpoints
- [ ] Implement real-time feedback display (WebSocket)
- [ ] Test full flow: user input → LLM response with context

---

## Phase 4: Flexible Ontology - COMPLETE FOR SOPHIA

**Base implementation merged (logos #459, #466, #468)**:
- [x] #458 - Flexible ontology base (merged)
- [x] #462 - Update pick-and-place test data (complete)
- [ ] #463 - Validate M4 demo end-to-end
- [x] #464 - M3 planning tests pass (15 integration tests verified 2026-01-01)
- [x] #461 - Audit downstream repos (sophia complete, close for sophia)
- [ ] #465 - Implement capability catalog

**Sophia migration (PR #104, merged 2026-01-01)**:
- [x] HCGClient.add_node() uses uuid, ancestors, type
- [x] E2E tests updated for "Hermes proposes, Sophia disposes"
- [x] All 177 unit tests + e2e tests pass

**Planner verification (2026-01-01)**:
- [x] 15 integration tests pass (9 in test_planner_integration.py, 6 in test_plan_api_pick_and_place.py)
- [x] Architecture: backward chaining with in-memory KnowledgeGraph, writes to Neo4j
- [x] Pick-and-place sequence works: move → grasp → move → release
- [ ] Evolution: wire planner to query HCG (not just write), add episode storage

---

## Test Infrastructure Fixes (2025-12-31)

**Completed via logos PR #468**:
- [x] `scripts/test_integration.sh` - Use `logos_config.LOGOS_PORTS` instead of hardcoded 7687
- [x] `tests/integration/ontology/test_neo4j_crud.py` - Remove flawed `type_count < instance_count` assertion
- [x] All 155 integration tests passing

---

## Cross-Cutting: SDK Distribution (#423)

**Current state**: Apollo vendors SDKs locally
**Target**: Publish SDKs from logos, consume as npm packages

**Tasks**:
- [ ] Set up SDK publishing in logos CI
- [ ] Update apollo to use published `@logos/hermes-sdk`, `@logos/sophia-sdk`
- [ ] Remove vendored copies
- [ ] Document SDK update process

---

## Execution Status

```
Phase 1A: COMPLETE (sophia standardization - PR #103)
Phase 1B: COMPLETE (CWM persistence + flexible ontology - PRs #102, #104)
Phase 1C: COMPLETE (execute endpoint - simulation mode, 10 tests pass)
Phase 1D: COMPLETE (feedback emission - sophia #16, 2026-01-02)
Phase 2:  COMPLETE (hermes integration - #50, #55, #56, #60, #66, #17)
Phase 3A: COMPLETE (apollo standardization - #131, PR #141)
Phase 3B: IN PROGRESS (connect to new APIs)
Phase 4:  COMPLETE for sophia (PR #104), other repos TBD
```

**Last Updated**: 2026-01-03 (Phase 1-2 complete, 3A complete, 3B in progress)

---

## Key Decisions Made

1. **CWM persistence**: Neo4j via flexible ontology (Node label with type property)
2. **CWM API**: Single `GET /cwm` with type filter, not separate endpoints
3. **Type hierarchy**: cognition → cwm → cwm_a/cwm_g/cwm_e using COMPONENT_OF edges
4. **Test ports**: Read from logos_config, not hardcoded

## Key Decisions Still Needed

1. **Feedback transport**: WebSocket vs SSE vs polling?
2. **LLM context strategy**: Full CWM dump vs. semantic retrieval?
3. **SDK publishing**: npm registry vs GitHub packages?

---

## Success Criteria

- [ ] Apollo user can type message → Hermes /llm responds with CWM context
- [x] Sophia /plan works end-to-end (15 integration tests pass)
- [x] Sophia /execute works end-to-end (10 integration tests pass, simulation mode)
- [x] Feedback flows Sophia → Hermes (Redis queue, sophia #16 + hermes #17)
- [x] All repos pass CI with standardized test infrastructure (logos, sophia, hermes, apollo done)
- [ ] SDKs published and consumed (not vendored)
- [ ] Apollo webapp connected to new APIs (3B)
