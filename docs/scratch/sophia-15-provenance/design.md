# Issue #15: Provenance Metadata - Design Spec

**Date:** 2026-01-02
**Status:** Draft
**Approach:** B - Optional properties with defaults

## Overview

Add provenance metadata fields to HCG nodes to track authorship, tooling, and timestamps. Fields are optional with sensible defaults for backward compatibility. Writers populate automatically; migration backfills existing data.

## Provenance Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source_service` | string | `"unknown"` | Service that created: `sophia`, `hermes`, `talos`, `apollo`, `human`, `unknown` |
| `author` | string | `null` | User/system identifier (optional) |
| `tool_type` | string | `null` | Tool category: `planner`, `llm`, `ingestion`, `simulation`, `manual`, `null` |
| `capability_id` | string | `null` | Specific capability/tool ID if applicable |
| `tags` | list[string] | `[]` | Audit/classification tags (e.g., `["llm-generated", "user-verified"]`) |
| `created_at` | ISO8601 string | Current time | When node was created |
| `updated_at` | ISO8601 string | Current time | When node was last modified |

## Components

### 1. sophia/src/sophia/hcg_client/client.py

**Responsibility:** Accept provenance fields in `add_node()` and populate defaults.

**Current signature:**
```python
def add_node(
    self,
    uuid: str,
    name: str,
    node_type: str,
    ancestors: List[str],
    is_type_definition: bool = False,
    properties: Optional[Dict[str, Any]] = None,
) -> str:
```

**New signature:**
```python
def add_node(
    self,
    uuid: str,
    name: str,
    node_type: str,
    ancestors: List[str],
    is_type_definition: bool = False,
    properties: Optional[Dict[str, Any]] = None,
    *,
    source_service: str = "unknown",
    author: Optional[str] = None,
    tool_type: Optional[str] = None,
    capability_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> str:
```

**Behavior:**
1. Generate `created_at` = current UTC ISO8601 timestamp
2. Generate `updated_at` = same as `created_at` for new nodes
3. Merge provenance into properties dict before storage
4. Execute existing MERGE query (provenance stored as node properties)

**Example:**
```python
client.add_node(
    uuid="plan-123",
    name="pick_block_plan",
    node_type="plan",
    ancestors=["concept"],
    source_service="sophia",
    tool_type="planner",
)
# Creates node with properties:
# {
#   source_service: "sophia",
#   tool_type: "planner",
#   created_at: "2026-01-02T15:30:00Z",
#   updated_at: "2026-01-02T15:30:00Z"
# }
```

### 2. sophia/src/sophia/hcg_client/client.py - update_node()

**Responsibility:** Update `updated_at` on node modifications.

**New method:**
```python
def update_node(
    self,
    uuid: str,
    properties: Dict[str, Any],
) -> str:
```

**Behavior:**
1. Set `updated_at` = current UTC ISO8601 timestamp
2. Merge with provided properties
3. Execute SET query on existing node

### 3. sophia API endpoints

**File:** `src/sophia/api/` (or wherever endpoints live)

**/plan endpoint:**
- Pass `source_service="sophia"`, `tool_type="planner"` when creating plan nodes

**/state endpoint:**
- Include provenance fields in response when returning nodes

**/simulate endpoint:**
- Pass `source_service="sophia"`, `tool_type="simulation"` when creating imagined states

### 4. hermes /ingest/media endpoint

**File:** `src/hermes/main.py`

**Behavior:**
- When forwarding to Sophia, include `source_service="hermes"`, `tool_type="ingestion"`
- Pass through any `author` from request context if available

### 5. Migration Script

**File:** `logos/scripts/migrate_provenance.py`

**Behavior:**
1. Connect to Neo4j
2. Find all nodes missing `source_service` property
3. Set defaults:
   - `source_service = "unknown"`
   - `created_at = node creation time if available, else "1970-01-01T00:00:00Z"`
   - `updated_at = created_at`
4. Log count of migrated nodes

**Query:**
```cypher
MATCH (n:Node)
WHERE n.source_service IS NULL
SET n.source_service = "unknown",
    n.created_at = COALESCE(n.created_at, "1970-01-01T00:00:00Z"),
    n.updated_at = COALESCE(n.updated_at, n.created_at, "1970-01-01T00:00:00Z")
RETURN count(n) as migrated
```

## Edge Cases

| Case | Behavior |
|------|----------|
| `add_node()` called without provenance args | Uses defaults: `source_service="unknown"`, timestamps=now |
| Node already has `created_at` | Preserve existing, only update `updated_at` |
| Migration on empty DB | No-op, returns 0 migrated |
| Invalid `source_service` value | Accept any string (no enum validation in storage) |

## Testing Strategy

### Unit Tests (sophia)

1. **test_add_node_with_provenance**
   - Input: `add_node(..., source_service="sophia", tool_type="planner")`
   - Assert: Returned node has provenance fields set

2. **test_add_node_default_provenance**
   - Input: `add_node(...)` with no provenance args
   - Assert: Node has `source_service="unknown"`, timestamps set

3. **test_update_node_updates_timestamp**
   - Input: Create node, wait 1ms, update node
   - Assert: `updated_at` > `created_at`

### Integration Tests (sophia)

1. **test_plan_endpoint_sets_provenance**
   - Call POST /plan
   - Query resulting node from Neo4j
   - Assert: `source_service="sophia"`, `tool_type="planner"`

### Migration Tests (logos)

1. **test_migration_backfills_nodes**
   - Create nodes without provenance
   - Run migration
   - Assert: All nodes have provenance fields

## Files Affected

| File | Action | Description |
|------|--------|-------------|
| `sophia/src/sophia/hcg_client/client.py` | Modify | Add provenance params to add_node, add update_node |
| `sophia/src/sophia/api/*.py` | Modify | Pass provenance to HCG client calls |
| `hermes/src/hermes/main.py` | Modify | Pass provenance when calling Sophia |
| `logos/scripts/migrate_provenance.py` | Create | Migration script |
| `logos/ontology/core_ontology.cypher` | Modify | Document provenance fields in comments |
| `sophia/tests/unit/test_hcg_client.py` | Modify | Add provenance tests |
| `sophia/tests/integration/test_api.py` | Modify | Add provenance integration tests |

## Out of Scope

- SHACL validation of provenance fields
- Provenance history tracking (who changed what when)
- `expected_output` field (defer to future issue)
- Predefined tag vocabulary (accept any string)
- CWMState envelope changes (provenance is on nodes, not transport)
- UI for viewing provenance
