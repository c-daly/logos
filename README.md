# Project LOGOS — Meta Repository

[![Validate LOGOS Artifacts](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml)
[![Run Tests](https://github.com/c-daly/logos/actions/workflows/test.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/test.yml)

This repository is the canonical "foundry" for Project LOGOS. It contains the formal specification, API contracts, the Hybrid Causal Graph (HCG) founding documents, and the development infrastructure for the shared HCG cluster.

Purpose
- Host the canonical spec and design artifacts that bind all LOGOS components together (see Section 3.1: Overview and Core Principles).
- Provide the HCG founding documents: `core_ontology.cypher` and `shacl_shapes.ttl` (see Section 4.1 and Section 4.3.1).
- Provide the dev infrastructure (Neo4j + Milvus) used by Sophia, Hermes, Talos, and Apollo during Phase 1 (see Section 7.1 and Section 5.2).
- Store the canonical API contracts (Hermes API per Table 2 in Section 3.4).

Repos in the LOGOS ecosystem
- `c-daly/sophia` — Sophia: non-linguistic cognitive core (Orchestrator, CWM-A, CWM-G, Planner, Executor). (See Section 3.3.)
- `c-daly/hermes` — Hermes: stateless language &amp; embedding utility (stt, tts, simple_nlp, embed_text). (See Table 2, Section 3.4.)
- `c-daly/talos` — Talos: hardware abstraction layer (sensors/actuators, simulated interfaces for Phase 1). (See Section 3.5.)
- `c-daly/apollo` — Apollo: thin client UI &amp; command layer. (See Section 3.5.)

Phase 1 focus
This repo is targeted at Phase 1 ("Formalize HCG and Abstract Pipeline") from Section 7.1. The main deliverables provided here are:
- The HCG ontology scaffold (`ontology/core_ontology.cypher`) — Section 4.1.
- The SHACL shapes used as Level 1 deterministic validation guardrails (`ontology/shacl_shapes.ttl`) — Section 4.3.1.
- A canonical Hermes OpenAPI contract for the stateless linguistic tools (`contracts/hermes.openapi.yaml`) — Table 2 in Section 3.4.
- Development docker-compose to run Neo4j (with neosemantics/SHACL support) and Milvus (vector store) as the hybrid HCG backend (`infra/docker-compose.hcg.dev.yml`) — Sections 4.1 &amp; 5.2.

How to run the HCG dev cluster (dev-only)
1. From this repo run:
   docker compose -f infra/docker-compose.hcg.dev.yml up -d
2. Neo4j will be reachable on ports 7474 (HTTP) and 7687 (Bolt). Milvus on 19530/9091.
3. Load the core ontology:
   ./infra/load_ontology.sh
4. Initialize Milvus collections:
   ./infra/init_milvus.sh
5. See `infra/README.md` for detailed instructions and manual loading options.

Python Tooling
- This repository includes Python-based utilities for project management and artifact validation.
- See `DEVELOPMENT.md` for setup instructions and documentation.
- Install tools via: `pip install -e ".[dev]"`
- CLI tools: `logos-generate-issues`, `logos-create-issues-by-epoch`
- Run tests: `pytest`

Project Management
- See `.github/PROJECT_BOARD_SETUP.md` for instructions on setting up the GitHub Project Board, labels, milestones, and issue tracking system.
- Use `logos-generate-issues` or `.github/scripts/generate_issues.py` to automatically create issues from the action items document.
- Weekly progress reports are automatically generated every Monday via GitHub Actions.
- All project tracking infrastructure is documented in `.github/README.md`.

CI/CD and Validation
- Automated validation of all canonical artifacts runs on every push and pull request.
- **Cypher Ontology**: Syntax validation using Neo4j 5.13.0 (`ontology/core_ontology.cypher`)
- **SHACL Shapes**: RDF/Turtle syntax validation using rdflib (`ontology/shacl_shapes.ttl`)
- **OpenAPI Contract**: OpenAPI 3.1.0 specification validation using swagger-cli (`contracts/hermes.openapi.yaml`)
- See `.github/workflows/validate-artifacts.yml` for the complete validation pipeline.

SHACL Validation Strategy
- **Default CI Gate (pyshacl)**: Fast, connectionless validation runs automatically on every push/PR ✅
  - Tests in `tests/phase1/test_shacl_pyshacl.py` validate shapes against fixtures without requiring Neo4j
  - Ensures SHACL shapes are syntactically correct and fixtures conform to expectations
  - **This is the primary gate** - PRs must pass these tests to merge
- **Integration Tests (Neo4j+n10s)**: Opt-in validation for comprehensive testing 🔧
  - Tests in `tests/phase1/test_shacl_neo4j_validation.py` validate data using Neo4j's n10s plugin
  - Requires Neo4j with n10s plugin installed and `RUN_NEO4J_SHACL=1` environment variable
  - Runs weekly or can be triggered manually via workflow dispatch
  - For local setup instructions, see `docs/PHASE1_VERIFY.md` - M2 section "Neo4j n10s Integration Tests (Opt-In)"
  - Workflow: `.github/workflows/shacl-neo4j-validation.yml`

Phase 1 Verification and Gate
- Phase 1 must be completed and verified before Phase 2 work can begin.
- **Verification Checklist**: See `docs/PHASE1_VERIFY.md` for complete Phase 1 verification criteria.
- **Milestone Gates**: Each milestone is verified through automated tests that produce individual badges:
  - **M1** (HCG Store/Retrieve): [![M1 Gate](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml)
  - **M2** (SHACL Validation): [![M2 Gate](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml)
  - **M3** (Planning): [![M3 Gate](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml)
  - **M4** (End-to-End Demo): [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml)
- **E2E Prototype Script**: Run `./scripts/e2e_prototype.sh` to test the complete flow (Apollo → Sophia → Talos → HCG)
- Phase 2 work is blocked until all milestone gates pass (automated tests green + manual verifications complete).
- Final documentation/UX polish before calling Phase 1 “done” lives under the `phase 1 closers` label (issues #200, #201, #202, #203, #204, #205, #206, #208). These cover the opt-in Neo4j SHACL job, planner/executor shims, Apollo CLI entrypoint, Milvus smoke test, stronger M4 assertions, and CI/test cleanup.

Notes and next steps
- The `core_ontology.cypher` and `shacl_shapes.ttl` are intentionally minimal, syntactically valid, and contain comments indicating where the full ontology and constraints described in the spec will be extended.
- This repo is the canonical place for future ontology updates, SHACL extensions, contract evolution, and HCG infra changes.
- See `docs/action_items.md` for the complete task breakdown and current progress.
