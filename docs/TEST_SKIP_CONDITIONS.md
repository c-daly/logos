# Test Skip Conditions (logos)

Tracking issue: **logos#529** — *de-vacuum integration tests + run them in CI.*

This document records every module-scope skip in the `logos` test suite and
*why* it exists. The rule (enforced by code review, not yet by lint) is:

> No silent `pytest.mark.skip` at module scope without a reason. Integration
> tests must gate on **service reachability**, not on a local Docker container
> name — so they run wherever the service is reachable (CI compose, the shared
> test stack, a remote stack) instead of silently skipping.

## The de-vacuum fix

Before this work, several spine integration/E2E modules gated on
`is_container_running(config.container)` — i.e. `docker ps --filter name=...`.
That is a *vacuum*: it skips the whole module whenever no **local** container
matches the expected name, even if Neo4j/Milvus are perfectly reachable. The
tests then "pass" by protecting nothing.

The fix switches those gates to real connectivity probes:

- `logos_test_utils.neo4j.is_neo4j_available()` — opens a Bolt session and runs
  `RETURN 1`.
- `logos_test_utils.milvus.is_milvus_available()` — opens a gRPC connection
  (added in this change to mirror the Neo4j probe).

`is_container_running()` / `is_milvus_running()` remain for orchestration code
that genuinely needs to know about a *local* container, but are no longer used
to gate test execution.

## Module-scope skips and their reasons

| File | Gate | Runs in CI? | Reason |
|------|------|-------------|--------|
| `tests/integration/ontology/test_neo4j_crud.py` | `is_neo4j_available()` | ✅ (Neo4j up in compose) | Needs a reachable Neo4j (Bolt + `docker exec cypher-shell` to load ontology). |
| `tests/integration/ontology/test_shacl_neo4j_validation.py` | per-test `is_neo4j_available()` / n10s presence | ✅ | Needs Neo4j; some cases need the n10s plugin. |
| `tests/integration/perception/test_simulation_service_integration.py` | per-test Neo4j readiness | ✅ | Needs Neo4j. |
| `tests/integration/planning/test_planning_workflow.py` | `pytest.mark.skip` (unconditional) | ❌ (intentional) | Tests reference the **old type-label ontology**; must be rewritten for the flexible `:Node` model. Tracked as follow-up — not a connectivity skip. |
| `tests/infra/test_milvus_collections.py` | `is_milvus_available()` | ✅ (Milvus up in compose) | Needs a reachable Milvus. Host/port now resolve from central config (was hardcoded `19530`). Contains the **keystone signal-check** (see below). |
| `tests/infra/test_hcg_client.py` | per-test Neo4j readiness / ontology loaded | ✅ | Needs Neo4j + loaded core ontology for data-dependent cases. |
| `tests/test_seeder_reified.py` · `test_queries_reified.py` · `test_edge_reification.py` | `is_neo4j_available()` | ✅ | HCG client → Neo4j persistence (reified IS_A edges). |
| `tests/logos_events/test_event_bus.py` | `REDIS_AVAILABLE` | ⚠️ only if Redis present | Pub/sub event bus needs Redis. The logos CI compose currently brings up Neo4j + Milvus only; add Redis to exercise this in CI. |
| `tests/e2e/test_phase1_end_to_end.py` | `is_neo4j_available()` **and** `is_milvus_available()` | ✅ | Full spine E2E; needs both Neo4j and Milvus. |
| `tests/e2e/test_phase2_end_to_end.py` | `/health` reachability of app services | ❌ in logos CI (intentional) | Needs the **full app stack** (Sophia/Apollo/Hermes), which logos CI does not stand up. Runs in the cross-repo E2E environment. |
| `tests/e2e/test_cognitive_loop_smoke.py` | `/health` of Hermes + Sophia | ❌ in logos CI (intentional) | Needs running Hermes + Sophia services. |

Legend: ✅ executes in logos CI against the live compose stack · ❌ intentionally
skipped in logos CI (documented reason) · ⚠️ runs only when the dependency is
present.

## CI wiring

- `.github/workflows/ci.yml` (reusable standard CI) already starts the
  `tests/e2e/stack/logos/docker-compose.test.yml` stack (Neo4j + Milvus),
  initialises Milvus collections, and exports `NEO4J_*` / `MILVUS_*` so the
  collected integration tests connect to live services rather than skipping.
- `.github/workflows/integration-tests.yml` (added for #529) is a dedicated job
  that stands up the same stack, runs `tests/integration`, `tests/infra`, and
  the phase-1 spine E2E, and — critically — **fails the build if zero
  integration tests passed**. That guard is what prevents the suite from
  silently regressing back into a vacuum.

## Signal check (keystone bug)

The c-daly/sophia#146 class of bug is a *swallowed / failed embedding write* —
an embedding insert that is caught-and-dropped or never flushed, so nothing is
persisted but nothing fails either.

`tests/infra/test_milvus_collections.py::TestMilvusIntegration::test_embedding_write_is_readable_by_uuid`
guards against it: it writes a uniquely-keyed embedding, flushes, then reads it
back **by primary key** via `collection.query(...)` and asserts exactly that row
is present. A swallowed write leaves nothing to read back, so the test fails.
This runs in CI whenever Milvus is reachable.
