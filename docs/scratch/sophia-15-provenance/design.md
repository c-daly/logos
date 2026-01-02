# Issue #15: Provenance Metadata - Design Spec

**Date:** 2026-01-02
**Status:** Draft
**Approach:** Minimal core fields with flexible extensions

## Overview

Add provenance metadata fields to HCG nodes to track origin, derivation, and context. Fields are optional with sensible defaults for backward compatibility. The envelope (CWMState) remains a thin transport wrapper - all meaningful metadata lives on the node.

## Design Principles

1. **Provenance lives on nodes, not the envelope** - CWMState is just transport
2. **Envelope is cheap** - wraps node verbatim, no computation required
3. **Flexible extensions via tags/links** - avoid rigid schemas for evolving needs
4. **Source is granular** - module/job level, not service level

## Base Node Schema

### Identity (existing)
| Field | Type | Description |
|-------|------|-------------|
| `uuid` | string | Unique identifier |
| `name` | string | Human-readable name |
| `type` | string | Node type |
| `ancestors` | list[string] | Type hierarchy |
| `is_type_definition` | bool | Whether this defines a type |

### Provenance (new)
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | string | `"unknown"` | Module/job that created it (e.g., `jepa_runner`, `planner`, `ingestion`, `orchestrator`, `reflection_job`, `human`, `bootstrap`) |
| `derivation` | string | `"observed"` | How it was derived: `observed`, `imagined`, `reflected` |
| `confidence` | float | `null` | 0.0-1.0 certainty score (optional, set when applicable) |
| `created` | ISO8601 string | Current time | When node was created |
| `updated` | ISO8601 string | Current time | When node was last modified |

### Flexible (new)
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tags` | list[string] | `[]` | Free-form labels (e.g., `["llm-generated", "user-verified"]`) |
| `links` | dict | `{}` | Related entity IDs known at creation (e.g., `{"process_ids": [...], "plan_id": "...", "media_sample_id": "..."}`) |

## CWMState Envelope (minimal wrapper)

The envelope is a thin transport wrapper. All substance is in the node.

| Field | Source | Description |
|-------|--------|-------------|
| `state_id` | `node.uuid` | Identifies the record |
| `model_type` | Derived from `node.type` | `CWM_A`, `CWM_G`, `CWM_E` |
| `timestamp` | Now | When response was generated |
| `data` | `node.properties` | Verbatim node properties |

No `source`, `tags`, `links`, or `confidence` on the envelope - those live on the node.

## Components

### 1. sophia/src/sophia/hcg_client/client.py

**Responsibility:** Accept provenance fields in `add_node()` and populate defaults.

**Current signature:**
```python
def add_node(
    self,
    name: str,
    node_type: str,
    uuid: Optional[str] = None,
    ancestors: Optional[List[str]] = None,
    is_type_definition: bool = False,
    properties: Optional[Dict[str, Any]] = None,
) -> str:
```

**New signature:**
```python
def add_node(
    self,
    name: str,
    node_type: str,
    uuid: Optional[str] = None,
    ancestors: Optional[List[str]] = None,
    is_type_definition: bool = False,
    properties: Optional[Dict[str, Any]] = None,
    *,
    source: str = "unknown",
    derivation: str = "observed",
    confidence: Optional[float] = None,
    tags: Optional[List[str]] = None,
    links: Optional[Dict[str, Any]] = None,
) -> str:
```

Note: `uuid` is optional (auto-generated if None), `ancestors` auto-computed from type definition.

**Behavior:**
1. Generate `created` = current UTC ISO8601 timestamp
2. Generate `updated` = same as `created` for new nodes
3. Merge provenance fields into properties dict before storage
4. Execute existing MERGE query (provenance stored as node properties)

**Example:**
```python
client.add_node(
    uuid="state-123",
    name="block_position",
    node_type="entity_state",
    ancestors=["concept"],
    source="jepa_runner",
    derivation="imagined",
    confidence=0.85,
    tags=["simulation"],
    links={"process_ids": ["sim_abc"], "media_sample_id": "vid_xyz"}
)
# Creates node with properties:
# {
#   source: "jepa_runner",
#   derivation: "imagined",
#   confidence: 0.85,
#   tags: ["simulation"],
#   links: {"process_ids": ["sim_abc"], "media_sample_id": "vid_xyz"},
#   created: "2026-01-02T15:30:00Z",
#   updated: "2026-01-02T15:30:00Z"
# }
```

### 2. sophia/src/sophia/hcg_client/client.py - update_node()

**Responsibility:** Update `updated` timestamp on node modifications.

**New method:**
```python
def update_node(
    self,
    uuid: str,
    properties: Optional[Dict[str, Any]] = None,
) -> str:
```

**Behavior:**
1. Verify node exists (raise `ValueError` if not found)
2. Set `updated` = current UTC ISO8601 timestamp
3. Merge with provided properties (if any)
4. Execute SET query on existing node
5. Return uuid of updated node

**Example:**
```python
client.update_node(
    uuid="state-123",
    properties={"confidence": 0.95}
)
# Updates node, sets updated timestamp, returns "state-123"
# Raises ValueError if node doesn't exist
```

**Query:**
```cypher
MATCH (n:Node {uuid: $uuid})
SET n.updated = $updated
SET n += $properties
RETURN n.uuid as uuid
```

### 3. sophia API endpoints

**File:** `src/sophia/api/app.py`

**/plan endpoint:**
- Pass `source="planner"`, `derivation="imagined"` when creating plan nodes

**/state endpoint:**
- Returns CWMState envelope with `data` containing verbatim node properties
- Provenance fields (`source`, `derivation`, `confidence`, `created`, `updated`, `tags`, `links`) are in `data`
- No extra work needed - envelope wraps node verbatim

**/simulate endpoint:**
- Pass `source="jepa_runner"`, `derivation="imagined"` when creating imagined states

### 4. hermes /ingest/media endpoint

**File:** `src/hermes/main.py`

**Behavior:**
- When forwarding to Sophia, include `source="ingestion"`, `derivation="observed"`
- Include `links={"media_sample_id": "..."}` when applicable

### 5. Migration Script

**File:** `logos/scripts/migrate_provenance.py`

**Behavior:**
1. Connect to Neo4j
2. Find all nodes missing `source` property
3. Set defaults:
   - `source = "unknown"`
   - `derivation = "observed"`
   - `created = "1970-01-01T00:00:00Z"` (epoch for pre-existing)
   - `updated = created`
   - `tags = []`
   - `links = {}`
4. Log count of migrated nodes

**Query:**
```cypher
MATCH (n:Node)
WHERE n.source IS NULL
SET n.source = "unknown",
    n.derivation = COALESCE(n.derivation, "observed"),
    n.created = COALESCE(n.created, "1970-01-01T00:00:00Z"),
    n.updated = COALESCE(n.updated, n.created, "1970-01-01T00:00:00Z"),
    n.tags = COALESCE(n.tags, []),
    n.links = COALESCE(n.links, {})
RETURN count(n) as migrated
```

## Edge Cases

| Case | Behavior |
|------|----------|
| `add_node()` called without provenance args | Uses defaults: `source="unknown"`, `derivation="observed"`, timestamps=now |
| `add_node()` called for existing uuid | MERGE overwrites all properties including timestamps (use `update_node()` for updates) |
| `update_node()` on non-existent node | Raises `ValueError` |
| Migration on empty DB | No-op, returns 0 migrated |
| Invalid `source` value | Accept any string (no enum validation in storage) |
| `confidence` not provided | Stored as `null`, not 0 |

## Testing Strategy

### Unit Tests (sophia)

1. **test_add_node_with_provenance**
   - Input: `add_node(..., source="planner", derivation="imagined", confidence=0.9)`
   - Assert: Returned node has provenance fields set

2. **test_add_node_default_provenance**
   - Input: `add_node(...)` with no provenance args
   - Assert: Node has `source="unknown"`, `derivation="observed"`, timestamps set

3. **test_update_node_updates_timestamp**
   - Input: Create node, wait 1ms, update node
   - Assert: `updated` > `created`

### Integration Tests (sophia)

1. **test_plan_endpoint_sets_provenance**
   - Call POST /plan
   - Query resulting node from Neo4j
   - Assert: `source="planner"`, `derivation="imagined"`

### Migration Tests (logos)

1. **test_migration_backfills_nodes**
   - Create nodes without provenance
   - Run migration
   - Assert: All nodes have provenance fields

## Files Affected

| File | Action | Description |
|------|--------|-------------|
| `logos/contracts/sophia.openapi.yaml` | Modify | Simplify CWMState envelope, document node schema |
| `sophia/src/sophia/hcg_client/client.py` | Modify | Add provenance params to add_node, add update_node |
| `sophia/src/sophia/cwm_a/state_service.py` | Modify | Update CWMState model, remove redundant fields |
| `sophia/src/sophia/api/app.py` | Modify | Pass provenance to HCG client calls |
| `hermes/src/hermes/main.py` | Modify | Pass provenance when calling Sophia |
| `logos/scripts/migrate_provenance.py` | Create | Migration script |
| `logos/ontology/core_ontology.cypher` | Modify | Document provenance fields in comments |
| `sophia/tests/unit/test_hcg_client.py` | Modify | Add provenance tests |
| `sophia/tests/integration/test_api.py` | Modify | Add provenance integration tests |
| SDK regeneration | Run | Regenerate logos_sophia_sdk after contract change |

## CWMState Envelope Simplification

The current CWMState envelope has redundant fields. Since provenance now lives on nodes, the envelope can be simplified.

**Current CWMState model** (`src/sophia/cwm_a/state_service.py`):
```python
class CWMState(BaseModel):
    state_id: str           # Keep
    model_type: str         # Keep
    source: str             # Remove - now on node
    timestamp: datetime     # Keep
    confidence: float       # Remove - now on node
    status: str             # Remove - now node.derivation
    links: CWMStateLinks    # Remove - now on node
    tags: List[str]         # Remove - now on node
    data: CWMAGraphPayload  # Keep (becomes Dict[str, Any])
```

**Simplified CWMState:**
```python
class CWMState(BaseModel):
    state_id: str                      # Globally unique identifier
    model_type: str                    # CWM_A, CWM_G, CWM_E
    timestamp: datetime                # When response was generated
    data: Dict[str, Any]               # Verbatim node properties
```

**Field migration:**
| Removed Field | Now Located At |
|---------------|----------------|
| `source` | `data["source"]` |
| `confidence` | `data["confidence"]` |
| `status` | `data["derivation"]` |
| `links` | `data["links"]` |
| `tags` | `data["tags"]` |

This is a **breaking contract change** - requires:
1. Update `sophia.openapi.yaml`
2. Update `state_service.py` CWMState model
3. Update all code that creates CWMState objects
4. Regenerate SDKs
5. Update consumers (Apollo, Hermes if any)

## Out of Scope

- SHACL validation of provenance fields
- Provenance history tracking (who changed what when)
- `expected_output` field (defer to future issue)
- Predefined source/tag vocabulary (accept any string)
- UI for viewing provenance
- Neo4j edge relationships for links (using node properties for now)
