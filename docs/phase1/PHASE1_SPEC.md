# Phase 1 Specification — HCG & Abstract Pipeline

This document captures the authoritative Phase 1 scope now that historical notes live under `docs/old/`. Treat this as the concise, forward-looking contract for finishing the “phase 1 closers” and demonstrating the prototype baseline.

## Objectives
- Stand up the Hybrid Cognitive Graph (Neo4j + Milvus) with SHACL validation (pySHACL + optional Neo4j).
- Ship the opt-in heavy tests/gates (M1–M4 workflows, Neo4j SHACL, full M4 end-to-end).
- Deliver the Apollo CLI + Talos simulation shim that power the current prototype scripts.
- Close the remaining `phase 1 closers` tickets (#200–#208) and attach evidence to `docs/PHASE1_VERIFY.md` (archived under `docs/old/`).

## Deliverables
1. **Infrastructure & Data Plane** — Compose environment, ontology, SHACL, Milvus schema, helper scripts.
2. **Testing & Verification** — `tests/phase1/*`, GitHub Actions gates, opt-in heavy jobs.
3. **Prototype Flow (M4)** — `scripts/e2e_prototype.sh`, CLI goal→plan→execute loop, documentation of logs/artifacts.
4. **Documentation** — References now live in `docs/old/PHASE1_VERIFY.md`, `docs/old/PHASE1_PROTOTYPE_EXPECTATIONS.md`, etc. Update them only for archival purposes; all new edits belong here.

## Outstanding Work
- Neo4j SHACL opt-in job docs (#200).
- Planner/executor shims + documentation (#201/#202).
- Apollo entrypoint/CLI polish (#203/#208).
- Milvus smoke tests (#204/#169).
- Test/CI cleanup (#206).
- Stronger M4 assertions (#205) and final demo artifacts (#161/#133).

## Evidence Requirements
- Screenshots/logs linked from this file for each M1–M4 gate.
- Reference persona when describing demo behavior to keep Phase 1 audit trail intact.

> Historical material (e.g., `PHASE1_VERIFY.md`, `PHASE1_ISSUES.md`, etc.) is preserved in `docs/old/` for traceability but should not be updated; treat this document as the living Phase 1 spec going forward.
