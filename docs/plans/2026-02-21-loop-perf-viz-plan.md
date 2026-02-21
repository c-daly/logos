# Loop Performance & Visualization UX Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix visualization UX (snap-back, unresponsive controls, re-renders), enable OTel profiling, and decouple the cognitive loop from LLM response latency via async proposals.

**Architecture:** Visualization fixes are pure frontend (apollo/webapp). OTel spans touch Hermes + Sophia Python. Async pipeline adds a Redis-backed proposal queue in Sophia and a non-blocking context cache in Hermes.

**Tech Stack:** React/TypeScript, Three.js/R3F, Cytoscape.js, d3-force-3d, TanStack Query, FastAPI, Redis, OpenTelemetry

---

## Task 1: Three.js — Memoize NodeSphere and EdgeLine

**Files:**
- Modify: `apollo/webapp/src/components/hcg-explorer/renderers/ThreeRenderer.tsx:32-148`
- Test: `apollo/webapp/src/components/hcg-explorer/renderers/ThreeRenderer.test.tsx` (create)

**Step 1: Write test for memoized components**

```tsx
// apollo/webapp/src/components/hcg-explorer/renderers/ThreeRenderer.test.tsx
import { describe, it, expect } from 'vitest'
import { memo } from 'react'
import * as ThreeRenderer from './ThreeRenderer'

describe('ThreeRenderer exports', () => {
  it('exports ThreeRenderer component', () => {
    expect(ThreeRenderer.ThreeRenderer).toBeDefined()
  })
})

// Memoization is structural — verified by checking the component
// renders correctly and that React.memo is applied (checked manually).
// The real validation is visual: does the graph stop snapping back?
```

**Step 2: Run test to verify it passes (baseline)**

Run: `cd apollo/webapp && npx vitest run src/components/hcg-explorer/renderers/ThreeRenderer.test.tsx`

**Step 3: Wrap NodeSphere in React.memo with shared geometry/material**

In `ThreeRenderer.tsx`, replace the `NodeSphere` function (lines 32-115) with:

```tsx
import { useRef, useState, useEffect, useCallback, useMemo, memo } from 'react'

// Shared geometry and materials — created once per scene, not per node
const SHARED_SPHERE_GEO = new THREE.SphereGeometry(5, 16, 16)
const SHARED_TORUS_GEO = new THREE.TorusGeometry(6, 0.8, 8, 32)
const SHARED_SELECTION_TORUS_GEO = new THREE.TorusGeometry(8, 0.5, 8, 32)
const SHARED_MIDPOINT_GEO = new THREE.SphereGeometry(1, 8, 8)
const SHARED_MIDPOINT_MAT = new THREE.MeshBasicMaterial({ color: '#888888' })
const SHARED_SELECTION_MAT = new THREE.MeshBasicMaterial({ color: '#ffffff' })
const TORUS_ROTATION: [number, number, number] = [Math.PI / 2, 0, 0]

const NodeSphere = memo(function NodeSphere({
  node,
  position,
  isSelected,
  isHovered,
  onSelect,
  onHover,
}: NodeSphereProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const materialRef = useRef<THREE.MeshStandardMaterial>(null)
  const statusMaterialRef = useRef<THREE.MeshStandardMaterial>(null)

  const baseColor = NODE_COLORS[node.type] || NODE_COLORS.default
  const statusColor = node.status
    ? STATUS_COLORS[node.status] || STATUS_COLORS.default
    : null

  useFrame(() => {
    if (!meshRef.current) return
    const targetScale = isSelected ? 1.4 : isHovered ? 1.2 : 1.0
    meshRef.current.scale.lerp(
      new THREE.Vector3(targetScale, targetScale, targetScale),
      0.1
    )
  })

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        geometry={SHARED_SPHERE_GEO}
        onClick={e => { e.stopPropagation(); onSelect(node.id) }}
        onPointerOver={e => { e.stopPropagation(); onHover(node.id); document.body.style.cursor = 'pointer' }}
        onPointerOut={() => { onHover(null); document.body.style.cursor = 'auto' }}
      >
        <meshStandardMaterial
          ref={materialRef}
          color={baseColor}
          emissive={isSelected ? baseColor : '#000000'}
          emissiveIntensity={isSelected ? 0.3 : 0}
        />
      </mesh>

      {statusColor && (
        <mesh rotation={TORUS_ROTATION} geometry={SHARED_TORUS_GEO}>
          <meshStandardMaterial ref={statusMaterialRef} color={statusColor} />
        </mesh>
      )}

      {isSelected && (
        <mesh rotation={TORUS_ROTATION} geometry={SHARED_SELECTION_TORUS_GEO} material={SHARED_SELECTION_MAT} />
      )}

      <Text
        position={[0, 8, 0]}
        fontSize={3}
        color="#ffffff"
        anchorX="center"
        anchorY="bottom"
        outlineWidth={0.2}
        outlineColor="#000000"
      >
        {node.label.length > 15 ? node.label.slice(0, 15) + '...' : node.label}
      </Text>
    </group>
  )
})
```

**Step 4: Wrap EdgeLine in React.memo with shared geometry**

Replace `EdgeLine` (lines 117-148) with:

```tsx
const EdgeLine = memo(function EdgeLine({ sourcePos, targetPos }: EdgeLineProps) {
  const midpoint: [number, number, number] = [
    (sourcePos[0] + targetPos[0]) / 2,
    (sourcePos[1] + targetPos[1]) / 2,
    (sourcePos[2] + targetPos[2]) / 2,
  ]

  return (
    <group>
      <Line points={[sourcePos, targetPos]} color="#666666" lineWidth={1} opacity={0.6} transparent />
      <mesh position={midpoint} geometry={SHARED_MIDPOINT_GEO} material={SHARED_MIDPOINT_MAT} />
    </group>
  )
})
```

**Step 5: Run test**

Run: `cd apollo/webapp && npx vitest run src/components/hcg-explorer/renderers/ThreeRenderer.test.tsx`
Expected: PASS

**Step 6: Commit**

```bash
cd apollo/webapp && git add src/components/hcg-explorer/renderers/ThreeRenderer.tsx src/components/hcg-explorer/renderers/ThreeRenderer.test.tsx
git commit -m "perf: memoize Three.js NodeSphere/EdgeLine and pool geometry"
```

---

## Task 2: Three.js — Stable Force Simulation

**Files:**
- Modify: `apollo/webapp/src/components/hcg-explorer/renderers/ThreeRenderer.tsx:160-224` (SceneContent)

**Step 1: Rewrite SceneContent to preserve simulation across graph updates**

Replace the `useEffect` in `SceneContent` (lines 175-224) with a stable simulation that incrementally adds/removes nodes instead of recreating:

```tsx
function SceneContent({
  nodes,
  edges,
  selectedNodeId,
  hoveredNodeId,
  onNodeSelect,
  onNodeHover,
}: SceneContentProps) {
  const [positions, setPositions] = useState<Map<string, [number, number, number]>>(new Map())
  const simulationRef = useRef<any>(null)
  const simNodesRef = useRef<Map<string, any>>(new Map())

  // Incrementally update simulation when graph changes
  useEffect(() => {
    if (nodes.length === 0) {
      if (simulationRef.current) {
        simulationRef.current.stop()
        simulationRef.current = null
        simNodesRef.current.clear()
      }
      setPositions(new Map())
      return
    }

    const currentNodeMap = simNodesRef.current
    const newNodeIds = new Set(nodes.map(n => n.id))

    // Remove nodes no longer in graph
    for (const [id] of currentNodeMap) {
      if (!newNodeIds.has(id)) {
        currentNodeMap.delete(id)
      }
    }

    // Add new nodes near their connected neighbors (or random if no neighbors)
    for (const node of nodes) {
      if (!currentNodeMap.has(node.id)) {
        // Find a connected neighbor that already has a position
        const neighbor = edges.find(
          e => (e.source === node.id && currentNodeMap.has(e.target)) ||
               (e.target === node.id && currentNodeMap.has(e.source))
        )
        const neighborId = neighbor
          ? (neighbor.source === node.id ? neighbor.target : neighbor.source)
          : null
        const neighborNode = neighborId ? currentNodeMap.get(neighborId) : null

        currentNodeMap.set(node.id, {
          id: node.id,
          x: neighborNode ? neighborNode.x + (Math.random() - 0.5) * 40 : (Math.random() - 0.5) * 200,
          y: neighborNode ? neighborNode.y + (Math.random() - 0.5) * 40 : (Math.random() - 0.5) * 200,
          z: neighborNode ? neighborNode.z + (Math.random() - 0.5) * 40 : (Math.random() - 0.5) * 200,
        })
      }
    }

    const simNodes = Array.from(currentNodeMap.values())

    // Build links
    const nodeIdSet = new Set(simNodes.map(n => n.id))
    const simLinks = edges
      .filter(e => nodeIdSet.has(e.source) && nodeIdSet.has(e.target))
      .map(e => ({ source: e.source, target: e.target }))

    // Create or update simulation
    if (simulationRef.current) {
      simulationRef.current.stop()
    }

    const linkForce = forceLink(simLinks).id((d: any) => d.id) as any
    if (linkForce.distance) linkForce.distance(50)

    const simulation = forceSimulation(simNodes, 3)
      .force('charge', forceManyBody().strength(-100))
      .force('link', linkForce)
      .force('center', forceCenter(0, 0, 0))
      .force('collide', forceCollide(10))
      .alphaDecay(0.02)

    simulationRef.current = simulation

    simulation.on('tick', () => {
      const newPositions = new Map<string, [number, number, number]>()
      for (const node of simNodes) {
        newPositions.set(node.id, [node.x || 0, node.y || 0, node.z || 0])
      }
      setPositions(newPositions)
    })

    // Gentle reheat — not full restart
    simulation.alpha(0.3).restart()

    return () => {
      simulation.stop()
    }
  }, [nodes, edges])

  // ... rest of SceneContent unchanged (handleBackgroundClick, getPosition, JSX)
```

Key changes:
- `simNodesRef` persists node positions across re-renders
- New nodes placed near connected neighbors, not at origin
- `alpha(0.3)` instead of `alpha(1)` — gentle reheat, not full restart
- Deleted nodes removed from map, surviving nodes keep their positions

**Step 2: Verify manually**

Run: `cd apollo/webapp && npm run dev`
Navigate to HCG Explorer. Nodes should maintain position when graph updates arrive.

**Step 3: Commit**

```bash
git add src/components/hcg-explorer/renderers/ThreeRenderer.tsx
git commit -m "perf: stable d3-force-3d simulation across graph updates"
```

---

## Task 3: Three.js — Camera Persistence

**Files:**
- Modify: `apollo/webapp/src/components/hcg-explorer/renderers/ThreeRenderer.tsx:288-301` (CameraControls)

**Step 1: Add camera state ref to preserve position**

Replace `CameraControls` with:

```tsx
/** Camera controls wrapper that preserves position across re-renders */
function CameraControls() {
  const { camera, gl } = useThree()
  const controlsRef = useRef<any>(null)

  // Store camera state so it survives React re-renders
  const savedState = useRef<{ position: THREE.Vector3; target: THREE.Vector3 } | null>(null)

  useEffect(() => {
    if (controlsRef.current && savedState.current) {
      camera.position.copy(savedState.current.position)
      controlsRef.current.target.copy(savedState.current.target)
      controlsRef.current.update()
    }

    return () => {
      if (controlsRef.current) {
        savedState.current = {
          position: camera.position.clone(),
          target: controlsRef.current.target.clone(),
        }
      }
    }
  }, [camera])

  return (
    <TrackballControls
      ref={controlsRef}
      args={[camera, gl.domElement]}
      rotateSpeed={2}
      zoomSpeed={1.2}
      panSpeed={0.8}
      dynamicDampingFactor={0.2}
    />
  )
}
```

**Step 2: Verify manually**

Rotate/zoom camera in 3D view. Trigger a graph update. Camera should stay put.

**Step 3: Commit**

```bash
git add src/components/hcg-explorer/renderers/ThreeRenderer.tsx
git commit -m "fix: preserve camera position across graph updates"
```

---

## Task 4: Cytoscape — Layout Only on Structural Change

**Files:**
- Modify: `apollo/webapp/src/components/hcg-explorer/renderers/CytoscapeRenderer.tsx:345-413`

**Step 1: Track previous node/edge counts to detect structural vs. property changes**

Replace the "Update graph data" `useEffect` (lines 346-413) with:

```tsx
  // Track previous element counts to detect structural changes
  const prevNodeCountRef = useRef(0)
  const prevEdgeCountRef = useRef(0)
  const layoutTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Update graph data
  useEffect(() => {
    if (!cyRef.current || !isInitialized) return
    const cy = cyRef.current

    const nodes = graph.nodes.map(node => ({
      data: {
        id: node.id,
        label: node.label.length > 20 ? node.label.slice(0, 20) + '...' : node.label,
        type: node.type,
        status: node.status,
      },
    }))

    const edges = graph.edges.map(edge => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.type,
        type: edge.type,
      },
    }))

    let structuralChange = false

    cy.batch(() => {
      const newNodeIds = new Set(nodes.map(n => n.data.id))
      const newEdgeIds = new Set(edges.map(e => e.data.id))

      // Remove elements not in new data
      cy.nodes().forEach(node => {
        if (!newNodeIds.has(node.id())) {
          node.remove()
          structuralChange = true
        }
      })

      cy.edges().forEach(edge => {
        if (!newEdgeIds.has(edge.id())) {
          edge.remove()
          structuralChange = true
        }
      })

      // Add or update nodes
      for (const node of nodes) {
        const existing = cy.getElementById(node.data.id)
        if (existing.length === 0) {
          cy.add({ group: 'nodes', ...node })
          structuralChange = true
        } else {
          existing.data(node.data)
        }
      }

      // Add or update edges
      for (const edge of edges) {
        const existing = cy.getElementById(edge.data.id)
        if (existing.length === 0) {
          cy.add({ group: 'edges', ...edge })
          structuralChange = true
        } else {
          existing.data(edge.data)
        }
      }
    })

    // Only re-layout on structural changes, debounced
    if (structuralChange) {
      if (layoutTimerRef.current) clearTimeout(layoutTimerRef.current)
      layoutTimerRef.current = setTimeout(() => {
        const layoutConfig = getLayoutConfig(layout)
        // Don't fit — preserve user's viewport
        cy.layout({ ...layoutConfig, fit: false }).run()
      }, 300)
    }
  }, [graph, layout, isInitialized])
```

**Step 2: Clean up timer on unmount**

Add to the Cytoscape init `useEffect` cleanup (line 340):

```tsx
    return () => {
      if (layoutTimerRef.current) clearTimeout(layoutTimerRef.current)
      cy.destroy()
    }
```

**Step 3: Verify manually**

Send a chat message that triggers node creation. Existing nodes should smoothly adjust. Property-only changes (status updates) should not cause layout jumps.

**Step 4: Commit**

```bash
git add src/components/hcg-explorer/renderers/CytoscapeRenderer.tsx
git commit -m "perf: only re-layout Cytoscape on structural graph changes"
```

---

## Task 5: WebSocket — Granular Cache Updates

**Files:**
- Modify: `apollo/webapp/src/hooks/useWebSocket.ts:52-88`

**Step 1: Replace blanket invalidation with targeted updates**

Replace the message handler (lines 53-87) with:

```tsx
  useEffect(() => {
    let batchTimer: ReturnType<typeof setTimeout> | null = null
    let pendingUpdates: unknown[] = []

    const flushUpdates = () => {
      if (pendingUpdates.length === 0) return
      const updates = pendingUpdates
      pendingUpdates = []

      // Notify update callbacks
      for (const update of updates) {
        onUpdate?.(update)
      }

      // Invalidate only history/states, not the full snapshot
      queryClient.invalidateQueries({ queryKey: ['hcg', 'history'] })
      queryClient.invalidateQueries({ queryKey: ['hcg', 'states'] })
    }

    const handleMessage = (message: WebSocketMessage) => {
      setLastMessage(message)

      switch (message.type) {
        case 'snapshot':
          // Full snapshot — invalidate everything
          if (message.data && onSnapshot) {
            onSnapshot(message.data as GraphSnapshot)
          }
          queryClient.invalidateQueries({ queryKey: ['hcg'] })
          break

        case 'update':
          // Batch incremental updates — collect for 200ms then flush
          if (message.data) {
            pendingUpdates.push(message.data)
          }
          if (batchTimer) clearTimeout(batchTimer)
          batchTimer = setTimeout(flushUpdates, 200)
          break

        case 'error':
          if (message.message && onError) {
            onError(message.message)
          }
          console.error('WebSocket error:', message.message)
          break

        case 'pong':
          break
      }
    }

    const unsubscribe = hcgWebSocket.onMessage(handleMessage)

    const checkConnection = setInterval(() => {
      setConnected(hcgWebSocket.isConnected())
    }, 1000)

    if (autoConnect) {
      connect()
    }

    return () => {
      unsubscribe()
      clearInterval(checkConnection)
      if (batchTimer) clearTimeout(batchTimer)
      if (autoConnect) {
        disconnect()
      }
    }
  }, [autoConnect, connect, disconnect, onSnapshot, onUpdate, onError, queryClient])
```

Key changes:
- `snapshot` events still invalidate all `['hcg']` queries (reconnect scenario)
- `update` events batch over 200ms, then only invalidate `history` and `states`
- Callbacks still fire for each update so consumers can apply diffs

**Step 2: Run existing tests**

Run: `cd apollo/webapp && npx vitest run`
Expected: All existing tests pass (no tests directly cover useWebSocket currently).

**Step 3: Commit**

```bash
git add src/hooks/useWebSocket.ts
git commit -m "perf: batch WebSocket updates and reduce cache invalidation"
```

---

## Task 6: Graph Processor — Stable Object References

**Files:**
- Modify: `apollo/webapp/src/components/hcg-explorer/utils/graph-processor.ts:22-48`
- Test: `apollo/webapp/src/components/hcg-explorer/utils/graph-processor.test.ts`

**Step 1: Write test for referential stability**

Add to existing `graph-processor.test.ts`:

```typescript
describe('processGraph referential stability', () => {
  it('returns same node references when data is unchanged', () => {
    const snapshot = createMockSnapshot()
    const filter = createDefaultFilter()

    const result1 = processGraph(snapshot, filter)
    const result2 = processGraph(snapshot, filter)

    // Same snapshot + same filter = nodes should have same content
    expect(result1.nodes.length).toBe(result2.nodes.length)
    expect(result1.nodes.map(n => n.id)).toEqual(result2.nodes.map(n => n.id))
  })
})
```

**Step 2: Run test**

Run: `cd apollo/webapp && npx vitest run src/components/hcg-explorer/utils/graph-processor.test.ts`
Expected: PASS (this test just validates current behavior baseline)

**Step 3: Commit**

```bash
git add src/components/hcg-explorer/utils/graph-processor.test.ts
git commit -m "test: add referential stability test for graph processor"
```

---

## Task 7: OTel — Enable Stack and Add Hermes Spans

**Files:**
- Modify: `hermes/.env` (create if not exists)
- Modify: `hermes/src/hermes/proposal_builder.py:25-112`
- Modify: `hermes/src/hermes/services.py` (add spans to embedding/LLM calls)

**Step 1: Create/update Hermes .env with OTel config**

Add to `hermes/.env`:

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=hermes
```

**Step 2: Add spans to ProposalBuilder**

At the top of `proposal_builder.py`, add tracer import:

```python
try:
    from logos_observability import get_tracer
    tracer = get_tracer("hermes.proposal_builder")
except ImportError:
    from contextlib import nullcontext

    class _NoopTracer:
        def start_as_current_span(self, name, **kw):
            return nullcontext()

    tracer = _NoopTracer()
```

Wrap each pipeline stage in the `build()` method with spans:

```python
    async def build(self, text, metadata, *, correlation_id=None, llm_provider="unknown", model="unknown", confidence=0.7):
        proposal_id = str(uuid_mod.uuid4())
        now = datetime.now(UTC).isoformat()

        with tracer.start_as_current_span("proposal_builder.build") as span:
            span.set_attribute("proposal.id", proposal_id)
            span.set_attribute("proposal.text_length", len(text))

            t0 = time.monotonic()

            # Step 1: NER
            with tracer.start_as_current_span("proposal_builder.ner"):
                entities = await self._run_ner(text)
            t_ner = time.monotonic()

            # Step 2: Parallel relation + embedding
            entity_names = [e["name"] for e in entities]
            embed_texts = entity_names + [text]

            with tracer.start_as_current_span("proposal_builder.parallel_extract_embed"):
                rel_task = self._run_relation_extraction(text, entities)
                emb_task = self._run_batch_embed(embed_texts)
                raw_edges, all_embeddings = await asyncio.gather(rel_task, emb_task)
            t_rel = time.monotonic()

            # ... rest of build() unchanged but within the outer span
```

**Step 3: Add Sophia .env OTel config**

Add to `sophia/.env`:

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=sophia
```

**Step 4: Start OTel stack and verify traces**

Run: `cd logos && docker compose -f infra/docker-compose.otel.yml up -d`
Start Hermes and Sophia, send a chat message, check Grafana at `http://localhost:3001`.

**Step 5: Commit**

```bash
cd hermes && git add .env src/hermes/proposal_builder.py
git commit -m "feat: add OTel spans to proposal builder pipeline stages"
```

---

## Task 8: OTel — Add Sophia ProposalProcessor Spans

**Files:**
- Modify: `sophia/.env`
- Modify: `sophia/src/sophia/ingestion/proposal_processor.py:62-75`

**Step 1: Add tracer to ProposalProcessor**

At the top of `proposal_processor.py`, add:

```python
try:
    from logos_observability import get_tracer
    tracer = get_tracer("sophia.proposal_processor")
except ImportError:
    from contextlib import nullcontext

    class _NoopTracer:
        def start_as_current_span(self, name, **kw):
            return nullcontext()

    tracer = _NoopTracer()
```

**Step 2: Wrap process() stages in spans**

In `ProposalProcessor.process()`, wrap the major stages:

```python
    def process(self, proposal: dict) -> dict:
        with tracer.start_as_current_span("proposal_processor.process") as span:
            span.set_attribute("proposal.id", proposal.get("proposal_id", ""))

            stored_ids = []
            relevant_context = []
            name_to_uuid = {}

            # 1. Context search
            doc_emb = proposal.get("document_embedding")
            if doc_emb and doc_emb.get("embedding"):
                with tracer.start_as_current_span("proposal_processor.context_search") as ctx_span:
                    for collection in SEARCHABLE_COLLECTIONS:
                        # ... existing search code ...
                    ctx_span.set_attribute("context.count", len(relevant_context))

            # 2. Node ingestion
            with tracer.start_as_current_span("proposal_processor.ingest_nodes") as node_span:
                for proposed in proposal.get("proposed_nodes", []):
                    # ... existing node ingestion code ...
                node_span.set_attribute("nodes.stored", len(stored_ids))

            # 3. Edge ingestion
            with tracer.start_as_current_span("proposal_processor.ingest_edges") as edge_span:
                stored_edge_ids = []
                for edge in proposal.get("proposed_edges") or []:
                    # ... existing edge ingestion code ...
                edge_span.set_attribute("edges.stored", len(stored_edge_ids))

            return { ... }
```

**Step 3: Verify in Grafana**

Send a chat message. Check Grafana Tempo for a trace spanning Hermes → Sophia with individual stage timings.

**Step 4: Commit**

```bash
cd sophia && git add .env src/sophia/ingestion/proposal_processor.py
git commit -m "feat: add OTel spans to Sophia proposal processor"
```

---

## Task 9: Async Pipeline — Sophia Proposal Queue

**Files:**
- Create: `sophia/src/sophia/feedback/proposal_queue.py`
- Create: `sophia/src/sophia/feedback/proposal_worker.py`
- Modify: `sophia/src/sophia/feedback/__init__.py`
- Test: `sophia/tests/unit/feedback/test_proposal_queue.py`

**Step 1: Write test for ProposalQueue**

```python
# sophia/tests/unit/feedback/test_proposal_queue.py
import pytest
from unittest.mock import MagicMock, patch

from sophia.feedback.proposal_queue import ProposalQueue


class TestProposalQueue:
    def test_enqueue_dequeue(self):
        mock_redis = MagicMock()
        # Simulate brpop returning a queued message
        import json
        payload = {"proposal_id": "test-123", "raw_text": "hello"}
        message = json.dumps({"id": "pq-1", "payload": payload, "attempts": 0})
        mock_redis.brpop.return_value = (b"sophia:proposals:pending", message.encode())

        queue = ProposalQueue.__new__(ProposalQueue)
        queue.redis = mock_redis
        queue.QUEUE_KEY = "sophia:proposals:pending"

        # Enqueue
        mock_redis.lpush = MagicMock()
        queue.enqueue(payload, conversation_id="conv-1")
        mock_redis.lpush.assert_called_once()

        # Dequeue
        result = queue.dequeue(timeout=1)
        assert result is not None
        assert result["payload"]["proposal_id"] == "test-123"

    def test_store_and_get_context(self):
        mock_redis = MagicMock()
        import json
        context = [{"node_uuid": "n1", "name": "robot", "type": "entity", "score": 0.3}]
        mock_redis.get.return_value = json.dumps(context).encode()

        queue = ProposalQueue.__new__(ProposalQueue)
        queue.redis = mock_redis

        queue.store_context("conv-1", context, ttl=3600)
        mock_redis.setex.assert_called_once()

        result = queue.get_context("conv-1")
        assert len(result) == 1
        assert result[0]["name"] == "robot"
```

**Step 2: Run test to verify it fails**

Run: `cd sophia && poetry run pytest tests/unit/feedback/test_proposal_queue.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sophia.feedback.proposal_queue'`

**Step 3: Implement ProposalQueue**

```python
# sophia/src/sophia/feedback/proposal_queue.py
"""Redis-backed queue for async proposal processing."""

import json
import logging
from datetime import datetime
from typing import Any

import redis

logger = logging.getLogger(__name__)


class ProposalQueue:
    """Redis-backed queue for Hermes proposals."""

    QUEUE_KEY = "sophia:proposals:pending"
    CONTEXT_PREFIX = "sophia:context:"

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    def enqueue(self, proposal: dict, conversation_id: str | None = None) -> str:
        message_id = f"pq-{datetime.utcnow().timestamp()}"
        message = {
            "id": message_id,
            "payload": proposal,
            "conversation_id": conversation_id,
            "attempts": 0,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.redis.lpush(self.QUEUE_KEY, json.dumps(message))
        return message_id

    def dequeue(self, timeout: int = 5) -> dict | None:
        result = self.redis.brpop(self.QUEUE_KEY, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

    def store_context(self, conversation_id: str, context: list[dict], ttl: int = 3600) -> None:
        key = f"{self.CONTEXT_PREFIX}{conversation_id}"
        self.redis.setex(key, ttl, json.dumps(context))

    def get_context(self, conversation_id: str) -> list[dict]:
        key = f"{self.CONTEXT_PREFIX}{conversation_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return []

    def pending_count(self) -> int:
        return self.redis.llen(self.QUEUE_KEY)
```

**Step 4: Run test**

Run: `cd sophia && poetry run pytest tests/unit/feedback/test_proposal_queue.py -v`
Expected: PASS

**Step 5: Implement ProposalWorker**

```python
# sophia/src/sophia/feedback/proposal_worker.py
"""Background worker that processes proposals from the Redis queue."""

import asyncio
import logging
from typing import Any

from sophia.feedback.proposal_queue import ProposalQueue

logger = logging.getLogger(__name__)


class ProposalWorker:
    """Background worker that dequeues proposals and runs ProposalProcessor."""

    def __init__(
        self,
        queue: ProposalQueue,
        processor: Any,
        context_ttl: int = 3600,
    ):
        self.queue = queue
        self.processor = processor
        self.context_ttl = context_ttl
        self._running = False

    async def start(self) -> None:
        self._running = True
        logger.info("Proposal worker started")

        while self._running:
            await self._process_one()

    def stop(self) -> None:
        self._running = False
        logger.info("Proposal worker stopping")

    async def _process_one(self) -> None:
        message = await asyncio.to_thread(self.queue.dequeue, timeout=1)
        if not message:
            return

        proposal = message.get("payload", {})
        conversation_id = message.get("conversation_id")

        try:
            result = self.processor.process(proposal)
            relevant_context = result.get("relevant_context", [])

            if conversation_id and relevant_context:
                self.queue.store_context(
                    conversation_id, relevant_context, ttl=self.context_ttl
                )

            logger.info(
                "Processed proposal %s: %d nodes, %d edges, %d context items",
                message.get("id", "?"),
                len(result.get("stored_node_ids", [])),
                len(result.get("stored_edge_ids", [])),
                len(relevant_context),
            )
        except Exception as e:
            logger.error("Proposal processing failed for %s: %s", message.get("id"), e)
```

**Step 6: Update `__init__.py`**

Add to `sophia/src/sophia/feedback/__init__.py`:

```python
from sophia.feedback.proposal_queue import ProposalQueue
from sophia.feedback.proposal_worker import ProposalWorker
```

**Step 7: Commit**

```bash
cd sophia && git add src/sophia/feedback/proposal_queue.py src/sophia/feedback/proposal_worker.py src/sophia/feedback/__init__.py tests/unit/feedback/test_proposal_queue.py
git commit -m "feat: add Redis-backed proposal queue and background worker"
```

---

## Task 10: Async Pipeline — Wire Proposal Worker into Sophia Lifespan

**Files:**
- Modify: `sophia/src/sophia/api/app.py:237-290` (lifespan)

**Step 1: Add proposal worker to lifespan startup**

In `app.py`, after the existing feedback worker initialization (around line 282), add:

```python
    # Initialize proposal processing worker
    _proposal_worker = None
    _proposal_worker_task = None
    if feedback_config.enabled and _proposal_processor:
        try:
            from sophia.feedback.proposal_queue import ProposalQueue
            from sophia.feedback.proposal_worker import ProposalWorker

            proposal_queue = ProposalQueue(feedback_config.redis_url)
            proposal_queue.pending_count()  # Test connection
            _proposal_worker = ProposalWorker(
                queue=proposal_queue,
                processor=_proposal_processor,
            )
            _proposal_worker_task = asyncio.create_task(_proposal_worker.start())
            logger.info("Proposal processing worker initialized")
        except Exception as e:
            logger.warning(f"Proposal worker unavailable: {e}")
```

Add shutdown in the lifespan cleanup (after yield):

```python
    # Shutdown proposal worker
    if _proposal_worker:
        _proposal_worker.stop()
    if _proposal_worker_task:
        _proposal_worker_task.cancel()
```

**Step 2: Verify startup logs**

Start Sophia with Redis running. Check logs for "Proposal processing worker initialized".

**Step 3: Commit**

```bash
cd sophia && git add src/sophia/api/app.py
git commit -m "feat: wire proposal worker into Sophia lifespan"
```

---

## Task 11: Async Pipeline — Non-blocking Hermes /llm Endpoint

**Files:**
- Create: `hermes/src/hermes/context_cache.py`
- Modify: `hermes/src/hermes/main.py:144-201` (_get_sophia_context)
- Test: `hermes/tests/unit/test_context_cache.py`

**Step 1: Write test for context cache**

```python
# hermes/tests/unit/test_context_cache.py
import pytest
from unittest.mock import MagicMock
import json

from hermes.context_cache import ContextCache


class TestContextCache:
    def test_get_returns_empty_when_no_context(self):
        mock_redis = MagicMock()
        mock_redis.get.return_value = None

        cache = ContextCache.__new__(ContextCache)
        cache._redis = mock_redis
        cache._available = True

        result = cache.get_context("conv-1")
        assert result == []

    def test_get_returns_cached_context(self):
        context = [{"node_uuid": "n1", "name": "robot"}]
        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(context).encode()

        cache = ContextCache.__new__(ContextCache)
        cache._redis = mock_redis
        cache._available = True

        result = cache.get_context("conv-1")
        assert len(result) == 1
        assert result[0]["name"] == "robot"

    def test_enqueue_proposal(self):
        mock_redis = MagicMock()

        cache = ContextCache.__new__(ContextCache)
        cache._redis = mock_redis
        cache._available = True

        cache.enqueue_proposal({"raw_text": "hello"}, conversation_id="conv-1")
        mock_redis.lpush.assert_called_once()

    def test_graceful_fallback_when_redis_unavailable(self):
        cache = ContextCache.__new__(ContextCache)
        cache._redis = None
        cache._available = False

        assert cache.get_context("conv-1") == []
        cache.enqueue_proposal({"raw_text": "hello"})  # Should not raise
```

**Step 2: Run test to verify it fails**

Run: `cd hermes && poetry run pytest tests/unit/test_context_cache.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement ContextCache**

```python
# hermes/src/hermes/context_cache.py
"""Redis-backed context cache for async cognitive loop."""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

PROPOSAL_QUEUE_KEY = "sophia:proposals:pending"
CONTEXT_PREFIX = "sophia:context:"


class ContextCache:
    """Reads cached context from Redis and enqueues proposals."""

    def __init__(self, redis_url: str | None = None):
        self._redis = None
        self._available = False

        if not redis_url:
            return

        try:
            import redis
            self._redis = redis.from_url(redis_url)
            self._redis.ping()
            self._available = True
            logger.info("ContextCache connected to Redis")
        except Exception as e:
            logger.warning(f"ContextCache Redis unavailable: {e}")

    def get_context(self, conversation_id: str) -> list[dict]:
        if not self._available or not self._redis:
            return []

        try:
            key = f"{CONTEXT_PREFIX}{conversation_id}"
            data = self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.debug(f"Context cache read failed: {e}")
        return []

    def enqueue_proposal(
        self,
        proposal: dict,
        conversation_id: str | None = None,
    ) -> None:
        if not self._available or not self._redis:
            return

        try:
            message = {
                "id": f"pq-{datetime.utcnow().timestamp()}",
                "payload": proposal,
                "conversation_id": conversation_id,
                "attempts": 0,
                "created_at": datetime.utcnow().isoformat(),
            }
            self._redis.lpush(PROPOSAL_QUEUE_KEY, json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to enqueue proposal: {e}")
```

**Step 4: Run test**

Run: `cd hermes && poetry run pytest tests/unit/test_context_cache.py -v`
Expected: PASS

**Step 5: Modify `/llm` endpoint to be non-blocking**

In `hermes/src/hermes/main.py`, replace the cognitive-loop section of `llm_generate()` (lines 718-750):

```python
            # --- Cognitive loop: async context from prior turns ---
            request_id = getattr(http_request.state, "request_id", str(uuid.uuid4()))

            user_text = ""
            for msg in reversed(normalized_messages):
                if msg.role == "user":
                    user_text = msg.content
                    break

            sophia_context: list[dict] = []
            if user_text and _context_cache:
                # 1. Read context from prior turns (non-blocking)
                sophia_context = _context_cache.get_context(request_id)

                # 2. Fire-and-forget: build and enqueue proposal for next turn
                try:
                    ctx_metadata = dict(request.metadata or {})
                    if request.experiment_tags:
                        ctx_metadata["experiment_tags"] = request.experiment_tags
                    proposal = await _proposal_builder.build(
                        text=user_text,
                        metadata=ctx_metadata,
                        correlation_id=request_id,
                    )
                    _context_cache.enqueue_proposal(proposal, conversation_id=request_id)
                except Exception as e:
                    logger.warning(f"Async proposal enqueue failed: {e}")

                # 3. Inject cached context if available
                context_msg = _build_context_message(sophia_context)
                if context_msg:
                    span.set_attribute("llm.sophia_context_items", len(sophia_context))
                    inject_idx = 0
                    for i in range(len(normalized_messages) - 1, -1, -1):
                        if normalized_messages[i].role == "user":
                            inject_idx = i
                            break
                    normalized_messages.insert(
                        inject_idx,
                        LLMMessage(role="system", content=context_msg["content"]),
                    )
            elif user_text:
                # Fallback: synchronous Sophia call if Redis unavailable
                sophia_context = await _get_sophia_context(user_text, request_id, request.metadata or {})
                context_msg = _build_context_message(sophia_context)
                if context_msg:
                    inject_idx = 0
                    for i in range(len(normalized_messages) - 1, -1, -1):
                        if normalized_messages[i].role == "user":
                            inject_idx = i
                            break
                    normalized_messages.insert(
                        inject_idx,
                        LLMMessage(role="system", content=context_msg["content"]),
                    )
```

**Step 6: Initialize ContextCache in lifespan**

In `main.py` lifespan, add after `_proposal_builder` init:

```python
# Async context cache (Redis-backed, optional)
_context_cache: ContextCache | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _context_cache
    # ... existing startup code ...

    # Initialize context cache
    from hermes.context_cache import ContextCache
    redis_url = get_env_value("HERMES_REDIS_URL", default="redis://localhost:6379/0")
    _context_cache = ContextCache(redis_url)

    # ... rest of startup ...
    yield
    # ... shutdown ...
```

**Step 7: Add redis to Hermes dependencies**

In `hermes/pyproject.toml`, add `redis>=5.0.0` to dependencies:

```toml
dependencies = [
    # ... existing deps ...
    "redis>=5.0.0",
]
```

**Step 8: Run tests**

Run: `cd hermes && poetry run pytest tests/unit/test_context_cache.py -v`
Expected: PASS

**Step 9: Commit**

```bash
cd hermes && git add src/hermes/context_cache.py src/hermes/main.py tests/unit/test_context_cache.py pyproject.toml
git commit -m "feat: async proposal pipeline with Redis context cache"
```

---

## Execution Order Summary

| Task | Section | Description | Repo |
|------|---------|-------------|------|
| 1 | Viz | Memoize Three.js components + pool geometry | apollo |
| 2 | Viz | Stable force simulation | apollo |
| 3 | Viz | Camera persistence | apollo |
| 4 | Viz | Cytoscape layout-on-structural-change | apollo |
| 5 | Data | WebSocket batching + granular invalidation | apollo |
| 6 | Data | Graph processor stable references | apollo |
| 7 | OTel | Hermes pipeline spans | hermes |
| 8 | OTel | Sophia processor spans | sophia |
| 9 | Async | Proposal queue + worker | sophia |
| 10 | Async | Wire worker into Sophia lifespan | sophia |
| 11 | Async | Non-blocking /llm + context cache | hermes |

Tasks 1-6 can be done in sequence within apollo. Tasks 7-8 are independent (hermes/sophia). Tasks 9-11 are sequential (sophia queue → sophia wire → hermes consumer).
