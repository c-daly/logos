# Issue #15: Provenance Metadata - Intake Summary

**Date:** 2026-01-02
**Status:** Intake complete, pending approval

## What
Add provenance metadata (authorship, tool/capability info, audit trail) to HCG nodes so we can trace where knowledge came from.

## Why
Phase 2 governance requires audit trail for plans and state changes. Currently we cannot tell:
- Which service authored a node (Sophia, Hermes, Talos, human)
- What tool/capability was used
- How to audit LLM-generated plans

## Key Insight from Architecture
**Provenance lives on HCG nodes, not the CWMState envelope.**

CWMState is a transport/event envelope for change notifications. The actual provenance should be persisted on the HCG Node itself, not the envelope. The envelope already has `source` and `timestamp` for transport-level tracking.

## Proposed Fields (on HCG Node)

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `source_service` | string | Service that created the node (sophia, hermes, talos, apollo, human) | Yes |
| `author` | string | User or system identifier | No (default: service name) |
| `tool_type` | string | Type of tool used (planner, llm, ingestion, manual) | No |
| `capability_id` | string | Capability/tool that produced this (if applicable) | No |
| `created_at` | datetime | When node was created | Yes |
| `updated_at` | datetime | When node was last modified | Yes |

## Affected Components

### logos repo (contracts, ontology, SHACL)
1. **core_ontology.cypher** - Add provenance fields to Node structure comments
2. **shacl_shapes.ttl** - Add validation for new required fields
3. **sophia.openapi.yaml** - Consider surfacing provenance in responses (optional)

### sophia repo (HCG client, API endpoints)
1. **hcg_client/client.py** - `add_node()` to accept/populate provenance fields
2. **/plan endpoint** - Pass `source_service=sophia`, `tool_type=planner`
3. **/state endpoint** - Include provenance in responses
4. **Migration script** - Backfill existing nodes with defaults

### hermes repo (ingestion)
1. **main.py /ingest/media** - Pass `source_service=hermes`, `tool_type=ingestion`

## Success Criteria
1. New HCG nodes have provenance fields populated automatically
2. SHACL validates required fields (source_service, created_at, updated_at)
3. API responses include provenance when querying nodes
4. Migration script backfills existing dev/test data
5. SDK regenerated with provenance field access
6. Tests verify provenance is set and validated

## Constraints
- Backward compatible: existing nodes continue working (migration fills defaults)
- Provenance on HCG nodes, NOT on CWMState envelope
- Keep it simple: start with core fields, expand later if needed
- Don't break existing tests

## Relevant Capabilities
- Serena (activated for sophia) - symbolic code exploration
- Context7 - for Neo4j/SHACL documentation if needed
- Bash/Read/Write - file operations

## Workflow Classification
**Complex** - Multi-repo, schema changes, API changes, migration needed
- Full workflow: Design → Spec Review → Implement → Verify → Review

## Open Questions for Design Phase
1. Should `provenance_tags` be a separate array field or use existing `tags`?
2. Should we add `expected_output` field or defer to later?
3. Default value for `author` when service creates automatically?
4. Should CWMState envelope also surface provenance for convenience?
