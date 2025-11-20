# Unified CWM State Contract — Rollout Plan

## 1. Purpose

Phase 2 now specifies a single `CWMState` envelope for every world-model emission (CWM-A, CWM-G, CWM-E). This document explains **why** the change is important, **what** needs to shift across the stack, and **how/when** we implement it without regressing the existing CLI, browser, or APIs.

## 2. Why It Matters

1. **Consistent APIs** – One schema for `/state`, `/plan`, and `/simulate` removes bespoke payloads, making the shared SDK and Apollo clients dramatically simpler.
2. **Traceable diagnostics** – Structured logging, OpenTelemetry, and persona diary entries can correlate events by `state_id`/`model_type`, unlocking richer dashboards and verification evidence.
3. **Storage parity** – Neo4j nodes, Milvus embeddings, and archived artifacts stay in sync because each payload carries the same metadata (`links`, `status`, `confidence`).
4. **Future models** – Adding CWM-Future layers (safety, trust, etc.) becomes plug-and-play if they simply emit the envelope.

## 3. Scope

The rollout covers:

- **Backend schemas** – FastAPI response models, Pydantic schemas, and Neo4j/Milvus persistence.
- **API contracts** – Sophia/Hermes OpenAPI specs + generated SDKs (TypeScript + Python).
- **Clients** – Apollo CLI + web, plus any test harnesses.
- **Observability** – Structured logs, OTel exporters, demo capture scripts.

Out of scope: fundamental planner/JEPA logic changes. The focus is serialization + storage consistency.

## 4. Implementation Plan

### Phase A — Contract Finalization (Week 0–1)
1. Freeze the schema in `docs/phase2/PHASE2_SPEC.md` (done).
2. Create Pydantic models (`logos_sophia/api/models/cwm_state.py`) that represent the envelope plus model-specific payloads.
3. Update Neo4j Cypher helpers to emit `(:CWMState)` nodes with the documented fields.

### Phase B — API + Storage Updates (Week 1–2)
1. Modify `/state`, `/plan`, `/simulate` handlers to serialize lists of `CWMState` objects.
2. Ensure JEPA runner and CWM-E reflection job wrap their outputs in the new models.
3. Adjust Milvus writers to persist the same metadata envelope.
4. Update structured logs + OTel exporters to include `state_id`, `model_type`, `status`.

### Phase C — Contract Publication (Week 2)
1. Regenerate Sophia/Hermes OpenAPI specs.
2. Regenerate SDKs (`npm run generate:sdk`, `poetry run logos-generate-sdk`).
3. Update Apollo CLI/browser to consume the `states` array everywhere (graph panels, diagnostics, persona diary).
4. Refresh example payloads in documentation (README, developer guides).

### Phase D — Verification (Week 3)
1. Add integration tests that call `/state`, `/plan`, `/simulate` and validate the new structure.
2. Update `docs/phase2/VERIFY.md` evidence checklists to point at the new artifacts.
3. Record demo capture showing the browser rendering mixed CWM-A/G/E timelines from the shared envelope.

## 5. Timeline + Ownership

| Phase | Dates (target) | Owner(s) |
|-------|----------------|----------|
| A | Week 0–1 | Sophia platform |
| B | Week 1–2 | Sophia platform + CWM teams |
| C | Week 2 | Apollo team + SDK maintainers |
| D | Week 3 | QA/Verification |

## 6. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Clients temporarily expect old payloads | Roll out behind feature flag + versioned SDK; keep legacy endpoints until Apollo update merges. |
| Neo4j / Milvus data drift | Backfill scripts convert historical nodes/documents to the new label/property structure. |
| Telemetry gaps | Add validation to logging pipeline to reject events missing `state_id`/`model_type`. |

## 7. Success Criteria

- All `/state`, `/plan`, `/simulate` responses include `states[]`.
- Apollo CLI/web render data without custom mappers per model type.
- Structured logs and OTel traces include `state_id`, `model_type`, `status`.
- Neo4j graph contains `(:CWMState)` nodes linked to processes/entities/persona entries.
- Verification evidence (screenshots/logs/tests) references the new contract.

Keep this document updated as tasks land; link GitHub issues and PRs per phase so the rollout stays synchronized across the repositories.
