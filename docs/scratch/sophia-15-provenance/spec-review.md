# Spec Review: Issue #15 Provenance Metadata

**Date:** 2026-01-02
**Reviewer:** Claude (spec-review phase)
**Spec:** `docs/scratch/sophia-15-provenance/design.md`

## Checklist Validation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| No pronouns without referents | PASS | Pronouns have clear antecedents |
| No vague quantities | PASS | Specific values: "0.0-1.0", explicit enums |
| No implied behavior | FAIL | `/state endpoint` behavior vague; preserve `created` logic unspecified |
| Concrete examples | PASS | Good add_node example (lines 101-124), migration query |
| Explicit edge cases | PASS | Edge cases table covers key scenarios |
| Defined interfaces | FAIL | Signature mismatch with implementation; `update_node` underspecified |
| Testable success criteria | PASS | Testing strategy has concrete inputs/assertions |

**Checklist Result:** 5/7 passed

## Implementer Dry-Run

### Behaviors Traced

| Behavior | Target File | Implementable? | Gaps |
|----------|-------------|----------------|------|
| add_node with provenance | hcg_client/client.py | PARTIAL | Signature mismatch: spec has `uuid` first, impl has `name` first |
| update_node | hcg_client/client.py | NO | Missing: example, query, return behavior |
| Preserve created on update | hcg_client/client.py | NO | Implementation overwrites `created` on MERGE |
| /plan endpoint provenance | api/app.py | YES | None |
| /state endpoint response | api/app.py | NO | "Include provenance" is vague - format unspecified |
| CWMState simplification | state_service.py | PARTIAL | Current model not shown, exact changes unclear |
| Migration script | scripts/migrate_provenance.py | YES | Query is concrete |

### Questions for Spec Author

1. **Signature order**: Spec shows `add_node(uuid, name, node_type, ancestors, ...)` but implementation has `add_node(name, node_type, uuid=None, ancestors=None, ...)`. Which is correct?

2. **Preserve `created` on existing nodes**: Edge case says preserve, but MERGE query overwrites. How should this work? Options:
   - Use `ON CREATE SET n.created = $now` vs `ON MATCH SET n.updated = $now`?
   - Or accept that `created` is set once and never changes (current behavior)?

3. **`update_node()` details**:
   - Should it fail if node doesn't exist, or create it?
   - What does it return?
   - Show example query?

4. **/state endpoint format**: "Include provenance fields in response" - does this mean:
   - Provenance is in CWMState.data (verbatim node props)?
   - Or separate top-level fields on response?

5. **CWMState current structure**: Can you confirm current CWMState model fields so simplification is clear?

### Implicit Dependencies Found

- `datetime` import needed in client.py (already added in implementation)
- OpenAPI contract must be updated BEFORE SDK regeneration
- Existing tests may break if signature changes

### Implementation Misalignment Found

**add_node() signature mismatch:**
- Spec: `def add_node(self, uuid: str, name: str, node_type: str, ancestors: List[str], ...)`
- Impl: `def add_node(self, name: str, node_type: str, uuid: Optional[str] = None, ancestors: Optional[List[str]] = None, ...)`

The implementation signature is more flexible (auto-generates uuid, auto-computes ancestors) which is better, but spec should be updated to match.

**Dry-Run Result:** NEEDS CLARIFICATION (5 questions)

## Overall Status

**Status: APPROVED** (after revision)

### Summary
- Checklist: 7/7 passed (after updates)
- Dry-run: All behaviors implementable
- All questions resolved

### Issues Resolved

1. **[INTERFACE]** ✓ Spec signature updated to match implementation (name first, uuid optional)
2. **[BEHAVIOR]** ✓ Clarified: `add_node()` always sets timestamps, use `update_node()` for updates
3. **[INTERFACE]** ✓ `update_node()` expanded with example, query, and error behavior
4. **[BEHAVIOR]** ✓ `/state endpoint` clarified: returns CWMState with verbatim node in `data`
5. **[INTERFACE]** ✓ Current CWMState fields documented with migration mapping

### Recommendation

Spec validated. Proceed to implementation.

### Implementation Alignment

The `add_node()` implementation already completed aligns with the updated spec. Continue with remaining tasks.
