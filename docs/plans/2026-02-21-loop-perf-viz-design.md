# Loop Performance & Visualization UX Design

**Date**: 2026-02-21
**Status**: Approved
**Scope**: Approach A (targeted fixes) with visualization frontloaded + async proposal pipeline

## Problem Statement

The cognitive loop is functional but too slow (OpenAI API calls dominate latency) and the visualization tools are hard to use (graph snaps back to default position, controls unresponsive, full re-renders on every update).

## Design Overview

| Phase | Section | What | Repos |
|-------|---------|------|-------|
| 1 | Three.js stabilization | Stable simulation, memoization, geometry pooling, camera persistence, debouncing | apollo |
| 2 | Cytoscape stabilization | Incremental element updates, layout-only-on-structural-change, position preservation, debouncing | apollo |
| 3 | WebSocket & data layer | Granular cache updates, graph diffing, event batching, stable object references | apollo |
| 4 | OTel profiling | Enable existing stack, add spans to OpenAI/Milvus/Neo4j calls, pipeline timing in Diagnostics Panel | hermes, sophia, apollo |
| 5 | Async proposal pipeline | Non-blocking `/llm`, Redis-queued proposals, background Sophia processing, context available next turn | hermes, sophia |

### Not in scope (Approach B/C for later)

- Local model switch (wait for OTel data)
- Redis pub/sub for graph events
- Instanced rendering / LOD (not needed at <100 nodes yet)
- Streaming architecture / progressive rendering

---

## Section 1: Three.js Renderer Stabilization

**Problem**: Graph snaps back to default position, controls feel unresponsive, full re-render on every update.

**Root causes** (ThreeRenderer.tsx):
- `SceneContent` creates a new d3-force-3d simulation on every graph change, resetting all node positions
- `NodeSphere` and `EdgeLine` are not memoized -- every parent re-render recreates all geometries/materials
- Camera position is not preserved across graph updates
- No debouncing between rapid WebSocket-triggered updates

**Fixes:**

1. **Stable simulation** -- keep the d3-force-3d simulation instance alive across graph updates. On new nodes, add them to the existing simulation at random positions near their connected neighbors (not origin). On removed nodes, remove from simulation. Never restart from scratch.

2. **React.memo + stable keys** -- wrap `NodeSphere` and `EdgeLine` in `React.memo` with proper comparison. Use node UUID as key (already available).

3. **Geometry/material pooling** -- create shared `SphereGeometry` and `MeshStandardMaterial` instances once (via `useMemo` at the scene level), pass as props. Same for edge `LineBasicMaterial`.

4. **Camera persistence** -- store camera position/target in a ref that survives re-renders. Only reset camera on explicit user action (e.g., "reset view" button), never on graph update.

5. **Update debouncing** -- debounce graph data changes with a 200ms window so rapid WebSocket events batch into a single render update.

**Files**: `ThreeRenderer.tsx`, `HCGExplorer.tsx`, `context.tsx`

---

## Section 2: Cytoscape Renderer Stabilization

**Problem**: Layout re-runs on every graph change (dagre is O(n^2)), same position-reset issue as Three.js.

**Fixes:**

1. **Incremental element updates** -- instead of replacing all Cytoscape elements on graph change, diff against current elements. Add new nodes/edges, remove deleted ones, update changed properties. Cytoscape's `cy.add()` / `cy.remove()` handle this natively.

2. **Layout only on structural change** -- only re-run layout when nodes are added or removed, not on property updates (e.g., status change, confidence update). Property changes just update styling in-place.

3. **Preserve positions on re-layout** -- when layout does need to re-run (new nodes), use `animate: true` with `fit: false` so existing nodes shift smoothly rather than snapping. Pin nodes the user has manually dragged.

4. **Layout debouncing** -- if multiple nodes arrive in quick succession (common during proposal ingestion), batch them and run layout once after a 300ms quiet period.

**Files**: `CytoscapeRenderer.tsx`, `HCGExplorer.tsx`

---

## Section 3: WebSocket & Data Layer Fixes

**Problem**: Any WebSocket event triggers full `['hcg']` TanStack Query cache invalidation, causing a complete re-fetch of all entities. This kicks off the cascade of re-renders that causes the snap-back.

**Fixes:**

1. **Granular cache updates** -- when WebSocket receives an `update` event (incremental), patch the TanStack Query cache directly with `queryClient.setQueryData()` instead of invalidating. Only invalidate on `snapshot` events (full reconnect).

2. **Graph diffing in `useWebSocket`** -- the hook should compute a diff (added/removed/modified nodes and edges) and expose it, so renderers can apply incremental changes rather than treating every update as a full replacement.

3. **Batch WebSocket events** -- if multiple `update` events arrive within 200ms, collect them and apply as a single diff. This aligns with the renderer debouncing from Sections 1 and 2.

4. **Stable object references** -- `processGraph()` in `graph-processor.ts` currently creates new arrays on every call, breaking referential equality for `useMemo` downstream. Switch to producing a stable graph object that reuses unchanged node/edge references.

**Files**: `useWebSocket.ts`, `graph-processor.ts`, `useHCG.ts`

---

## Section 4: OTel Profiling

**Problem**: OpenAI calls are known to be slow but exact bottleneck is unknown. Pipeline timing metadata is captured in proposals but not surfaced.

**Existing infrastructure** (already in `logos/infra/`):
- OTel Collector (`docker-compose.otel.yml`) -- OTLP gRPC on :4317, HTTP on :4318
- Grafana Tempo -- trace backend
- Grafana -- on :3001 with pre-built dashboards for Sophia, Hermes, Apollo
- Both Hermes and Sophia have optional `otel` extras with graceful fallback

**What's needed:**

1. **Enable the stack** -- `docker compose -f infra/docker-compose.otel.yml up -d` and set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` in Hermes/Sophia `.env` files.

2. **Add spans to OpenAI calls** -- wrap each OpenAI API call (embedding batch, NER extraction, LLM completion) in its own OTel span inside the existing tracer. This gives a waterfall view of exactly where time goes per request.

3. **Add spans to Sophia processing** -- wrap Milvus searches and Neo4j writes in `ProposalProcessor.process()` so the trace shows the full Hermes-to-Sophia roundtrip broken into stages.

4. **Surface pipeline timing in Diagnostics Panel** -- proposal metadata already contains `ner_duration_ms`, `relation_duration_ms`, `embedding_duration_ms`, `total_duration_ms`. Add a "Pipeline" section to the Diagnostics Panel telemetry tab showing these as metric cards with sparklines (same pattern as existing cards).

**Files**: Hermes/Sophia `.env`, `proposal_builder.py` (spans), `proposal_processor.py` (spans), `DiagnosticsPanel.tsx` (pipeline cards)

---

## Section 5: Async Proposal Pipeline

**Problem**: The `/llm` endpoint blocks on Sophia context retrieval. Hermes generates expensive OpenAI embeddings for every entity, sends proposal to Sophia, waits for response, then generates the LLM completion. The full round-trip dominates latency.

**Architectural insight**: Memory should take a moment. Context from the current turn's proposal enriches the *next* turn, not the current one. This is natural -- you process first, recall later.

**Current flow** (synchronous, blocking):
```
User message -> Hermes builds proposal -> waits for Sophia -> injects context -> LLM generates -> response
                                          ^^^^ blocks everything
```

**New flow** (async, context from previous turns):
```
User message -> Hermes checks Redis for context from PRIOR turns -> LLM generates -> response
                    \-> fire-and-forget: push proposal to Redis queue
                         -> Sophia worker dequeues and processes in background
                         -> stores context result in Redis (keyed by conversation)
                         -> available for next turn
```

**Implementation:**

1. **Hermes `/llm` becomes non-blocking** -- instead of `await _get_sophia_context()`, push the proposal onto a Redis queue (same pattern as existing `FeedbackQueue`). LLM response returns immediately.

2. **Sophia processes proposals from the queue** -- a new worker (sibling to `FeedbackWorker`) dequeues proposals and runs `ProposalProcessor`. Stores the `relevant_context` result in Redis keyed by conversation/correlation ID.

3. **Next turn, Hermes reads cached context** -- before generating, check `sophia:context:{conversation_id}` in Redis. If context exists from the prior turn's proposal, inject it as a system message. First message has no context. Second message has context from the first.

4. **Proposal building also goes async** -- NER + embedding generation happens in the background worker, not on the request path. The user gets their LLM response without waiting for any of it.

**Result**: LLM response latency = just the OpenAI completion call. Everything else (NER, embeddings, Sophia processing) happens between turns.

**Fallback**: If Redis is down, fall back to current synchronous behavior.

**Files**: New `sophia/src/sophia/feedback/proposal_queue.py`, new `sophia/src/sophia/feedback/proposal_worker.py`, `hermes/src/hermes/main.py` (`/llm` refactor), new `hermes/src/hermes/context_cache.py` (Redis read), `sophia/src/sophia/api/app.py` (new worker in lifespan)

---

## Redis Key Schema

| Key | Purpose | TTL |
|-----|---------|-----|
| `sophia:feedback:pending` | Existing feedback queue | None (consumed) |
| `sophia:feedback:failed` | Existing failed feedback | None |
| `sophia:proposals:pending` | New proposal queue | None (consumed) |
| `sophia:context:{conversation_id}` | Processed context for next turn | 1 hour |

---

## Execution Order

Visualization first (Sections 1-3), then observability (Section 4), then async pipeline (Section 5). Each section is independently deployable and testable.
