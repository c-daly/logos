# Phase 1 Prototype Expectations

Scope: A working, demonstrable prototype for Phase 1 (Hybrid Cognitive Graph foundation) that can be stood up locally or in CI with clear guardrails. This is not the full autonomous agent; it is the infrastructure + data-plane proof of concept.

## Core capabilities
- **HCG data plane running**: Neo4j (with n10s) up via `infra/docker-compose.hcg.dev.yml`; Milvus available for vectors.
- **Ontology and data loaded**: `ontology/core_ontology.cypher` plus pick-and-place test data (`ontology/test_data_pick_and_place.cypher`) seeded and queryable.
- **SHACL validation**: Shapes (`ontology/shacl_shapes.ttl`) validated against fixtures. Default via pyshacl; optional Neo4j+n10s validation when enabled.
- **Interfaces present (stub-level OK)**:
  - Apollo entrypoint (CLI/API) to create a goal or query state.
  - Sophia planner stub/API to return a simple plan graph.
  - Talos simulation hook to apply a plan step (e.g., grasp/place) and update state in Neo4j.
- **End-to-end smoke**: A scripted flow (M4) that:
  1) Starts infra
  2) Loads ontology + test data
  3) Creates a goal
  4) Gets a plan from the planner stub
  5) Applies at least one step via the Talos/executor shim
  6) Verifies resulting state/relationships in Neo4j

## Optional/advanced (nice-to-have in Phase 1)
- **Milvus integration smoke**: Store a test embedding, confirm metadata/UUID linkage in Neo4j, and run a health check on collections.
- **Neo4j SHACL gate**: Opt-in CI job that runs n10s SHACL validation against the live DB (`RUN_NEO4J_SHACL=1`).

## Success criteria
- Infra stands up cleanly; constraints/indexes and seed data are present.
- Shapes catch invalid fixtures (pyshacl) and can be validated in Neo4j when enabled.
- Goal → plan → (simulated) execution → state verification runs end to end in the M4 test/script without manual intervention.
- Clear docs for how to run locally and how to enable the optional Neo4j/Milvus checks.

## Tracking the remaining work
The remaining polish and documentation needed before we call Phase 1 complete are tracked with the `phase 1 closers` label:

- #200 Neo4j SHACL opt-in workflow + docs
- #201 Sophia planner stub surface
- #202 Executor/Talos shim updates
- #203 Apollo CLI/API entrypoint
- #204 Milvus smoke/health check
- #205 Stronger M4 assertions using the RobotArm fixtures
- #206 CI/test cleanup + docs about opt-in heavy tests
- #208 Apollo CLI prototype wiring for the goal → plan → execute loop
