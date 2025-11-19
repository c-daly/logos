# Prototype Capabilities (Post-Phase-1 Slice)

This document summarizes what the initial prototype delivers once the Phase 1 issues and prototype tickets are implemented. Scope is intentionally minimal to validate the end-to-end architecture, not a full feature set.

## What the Prototype Does
- **HCG Data Plane**: Neo4j + Milvus running via `infra/docker-compose.hcg.dev.yml`, loaded with the pick-and-place ontology, SHACL shapes, and seeded domain data.
- **SHACL Enforcement**: Shapes loaded through n10s; writes to Neo4j are validated so malformed updates fail fast.
- **Hermes Embeddings**: `/embed_text` implemented with a lightweight model; embeddings are stored in Milvus and `embedding_id` + model metadata are returned.
- **Sophia Plan/State API**: Minimal service exposing `/plan` and `/state`. `/plan` returns a template-based pick-and-place plan over the seeded HCG; `/state` returns a snapshot of relevant graph state. All writes go through SHACL.
- **Talos Execution Shim**: Deterministic simulation accepts a plan, steps through it, and updates HCG state (e.g., `is_grasped`, positions) via Sophia.
- **Apollo Thin Client**: CLI wiring to call Sophia (`send` → `/plan`, `state` → `/state`, `plans` → cached plan); text output is sufficient for the prototype. Web view is optional/minimal.
- **End-to-End Script**: A scripted flow runs compose, loads ontology/shapes/test data, calls Apollo to request a plan, lets Talos shim execute, and shows the updated state.

## What It Does Not Do (Yet)
- No full planner/search (plan can be template-based for the seeded scenario).
- No real STT/TTS or advanced NLP; those endpoints may be thin stubs.
- No rich Apollo visualization—graph UI can follow later.
- No real hardware; Talos remains simulated and deterministic.
- Limited robustness: happy-path only, minimal error recovery.

## Success Criteria for the Prototype
- End-to-end command → plan → simulated execution → state update is demonstrable with the seeded pick-and-place data.
- SHACL validation blocks malformed writes during the flow.
- Hermes persists embeddings to Milvus and returns `embedding_id`.
- Apollo outputs the plan and the updated state after Talos runs.

## How to Run (Conceptual)
1. Start infra: `docker compose -f infra/docker-compose.hcg.dev.yml up -d`.
2. Load ontology, SHACL, and seeded test data.
3. Start Hermes, Sophia (prototype API), Talos shim, and Apollo CLI with default local config.
4. Run the E2E script: request a pick-and-place goal, observe plan output, then verify state updates.

## Related Issues
- Core Phase 1: #153, #154, #155, #167, #168, #169.
- Prototype slice: #172 (Sophia API), #173 (Hermes embeddings), #174 (Talos shim), #175 (Apollo wiring), #176 (E2E script).
- Phase 1 readiness polish (`phase 1 closers` label):
  - #200 Neo4j SHACL opt-in job/docs
  - #201 Planner stub API
  - #202 Executor/Talos shim hardening
  - #203 Apollo entrypoint (CLI/API)
  - #204 Milvus smoke
  - #205 Stronger M4 assertions
  - #206 Test/CI cleanup
  - #208 Apollo CLI prototype wiring
