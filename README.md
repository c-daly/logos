# Project LOGOS — Meta Repository

[![Validate LOGOS Artifacts](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/validate-artifacts.yml)
[![Phase 2 E2E](https://github.com/c-daly/logos/actions/workflows/phase2-e2e.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/phase2-e2e.yml)
[![Phase 2 OTEL](https://github.com/c-daly/logos/actions/workflows/phase2-otel.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/phase2-otel.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A Non-Linguistic Cognitive Architecture for Autonomous Agents**

This repository is the canonical "foundry" for Project LOGOS. It contains the formal specification, API contracts, the Hybrid Causal Graph (HCG) founding documents, and the development infrastructure for the shared HCG cluster.

**[Phase 1 Complete ✅](docs/evidence/PHASE1.md)** | **[Phase 2 Complete ✅](docs/evidence/PHASE2.md)** | **Phase 3: Planning 📋** | [Read the docs](docs/) | [📊 Project Assessment](ASSESSMENT_SUMMARY.md)

Purpose
- Host the canonical spec and design artifacts that bind all LOGOS components together (see Section 3.1: Overview and Core Principles).
- Provide the HCG founding documents: `core_ontology.cypher` and `shacl_shapes.ttl` (see Section 4.1 and Section 4.3.1).
- Provide the dev infrastructure (Neo4j + Milvus) used by Sophia, Hermes, Talos, and Apollo during Phase 1 (see Section 7.1 and Section 5.2).
- Store the canonical API contracts (Hermes API per Table 2 in Section 3.4).

Repos in the LOGOS ecosystem
- `c-daly/sophia` — Sophia: non-linguistic cognitive core (Orchestrator, CWM-A, CWM-G, Planner, Executor). (See Section 3.3.)
- `c-daly/hermes` — Hermes: stateless language &amp; embedding utility (stt, tts, simple_nlp, embed_text, llm). (See Table 2, Section 3.4.)
- `c-daly/talos` — Talos: hardware abstraction layer (sensors/actuators, simulated interfaces for Phase 1). (See Section 3.5.)
- `c-daly/apollo` — Apollo: smart presentation layer. (See Section 3.5.)

Embodiment &amp; UX flexibility
- Talos exposes capabilities via APIs, not a fixed robot. A LOGOS deployment may plug in simulators, one robot, many robots, or no hardware at all without changing Sophia or the HCG.
- Apollo is any interaction surface that drives the documented goal/plan/state APIs: today that is a CLI; future touch/voice interfaces or kiosks remain fully compliant as long as they use the same contracts.

Documentation layout
- Architecture specs live in `docs/architecture/` (see `PHASE1_SPEC.md`, `PHASE2_SPEC.md`, `PHASE3_SPEC.md`).
- Operations/CI/testing/verification live in `docs/operations/`.
- Observability references live in `docs/observability/`.
- API docs (generated) live in `docs/api/` and are published to GitHub Pages.

Phase roadmap (see `docs/architecture/` for specs):
- **Phase 1 – Formalize HCG & Abstract Pipeline** ✅: Ontology, SHACL, Compose infra, CLI prototype. Spec: `docs/architecture/PHASE1_SPEC.md` | [Verification Evidence](docs/evidence/PHASE1.md).
- **Phase 2 – Perception & Apollo UX** ✅: Sophia/Hermes services, Apollo browser + CLI, perception pipeline, diagnostics/persona. Spec: `docs/architecture/PHASE2_SPEC.md` | [Verification Evidence](docs/evidence/PHASE2.md).
- **Phase 3 – Learning & Embodiment Options**: Episodic memory, probabilistic validation, optional physical demos (manipulator, touchscreen), multi-agent prep. Spec: `docs/architecture/PHASE3_SPEC.md`.
- **Phase 4 – Operational Autonomy**: Continuous learning with safety gates, observability/rollback tooling, production deployment patterns. Spec TBD.
- **Phase 5 – Networked Agents / Swarm**: LOGOS instances collaborating, sharing HCG slices, coordinating Talos fleets. Spec TBD.

What’s new
- Added OpenTelemetry dev stack (collector + Jaeger + Prometheus); see `docs/observability/OTEL_INFRASTRUCTURE.md`.
- Milvus test stack ports shifted to 18530/18091 (update client configs accordingly).
- CI no longer uploads coverage to Codecov; Poetry is used in perception workflows.

Infrastructure Setup

The LOGOS ecosystem requires a development infrastructure cluster consisting of:
- **Neo4j 5.13.0**: Graph database for the Hybrid Causal Graph (HCG)
- **Milvus v2.3.3**: Vector database for semantic search and embeddings
- **SHACL Validation Service**: REST API for RDF/SHACL validation

**Prerequisites**
- Docker and Docker Compose installed and running
- At least 4GB RAM allocated to Docker
- Ports 7474, 7687, 19530, 9091, and 8081 available

**Quick Start**

1. **Start the HCG development cluster:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml up -d
   ```

2. **Verify services are running:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml ps
   ```
   
   Expected services: `logos-hcg-neo4j`, `logos-hcg-milvus`, `logos-shacl-validation`

3. **Load the core ontology into Neo4j:**
   ```bash
   ./infra/load_ontology.sh
   ```
   
   This creates constraints, indexes, and foundational HCG nodes.

4. **Initialize Milvus collections:**
   ```bash
   ./infra/init_milvus.sh
   ```
   
   This creates vector collections for Entity, Concept, State, and Process embeddings.

5. **Verify the setup:**
   - Neo4j Browser: http://localhost:7474 (credentials: `neo4j/neo4jtest`)
   - SHACL Validation API: http://localhost:8081/docs
   - Check health: `python3 infra/check_hcg_health.py`

**Stopping the Cluster**
```bash
# Stop services (preserves data)
docker compose -f infra/docker-compose.hcg.dev.yml down

# Stop and remove all data (clean slate)
docker compose -f infra/docker-compose.hcg.dev.yml down -v
```

**Detailed Documentation**

For comprehensive documentation including:
- Manual loading options
- SHACL validation strategies (pyshacl vs Neo4j+n10s)
- Backup and restore procedures
- Troubleshooting and port configuration
- Integration with LOGOS components

See `infra/README.md` for complete infrastructure documentation.

Python Tooling
- This repository includes Python-based utilities for project management and artifact validation.
- See `DEVELOPMENT.md` for setup instructions and documentation.
- Install tools via: `pip install -e ".[dev]"`
- CLI tools: `logos-generate-issues`, `logos-create-issues-by-epoch`
- Run tests: `pytest`
- The shared reusable CI workflow defined here also powers the Sophia/Hermes/Talos/Apollo repos.

## Local Testing (CI Parity)

The LOGOS meta repo is the source of `.github/workflows/reusable-standard-ci.yml`. Run the same commands locally to mirror the CI signal:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
ruff check src tests
black --check src tests
mypy src
pytest --cov --cov-report=term --cov-report=xml
```

Keeping these commands green ensures the `test.yml` workflow (and any downstream repos using the reusable template) stay healthy.

Project Management
- See `.github/PROJECT_BOARD_SETUP.md` for instructions on setting up the GitHub Project Board, labels, milestones, and issue tracking system.
- Use `logos-generate-issues` or `.github/scripts/generate_issues.py` to automatically create issues from the action items document.
- Weekly progress reports are automatically generated every Monday via GitHub Actions.
- All project tracking infrastructure is documented in `.github/README.md`.

API Documentation
- **Interactive API Documentation**: Browse comprehensive API documentation at [c-daly.github.io/logos/api](https://c-daly.github.io/logos/api/)
- **Available APIs**: 
  - [Hermes API](https://c-daly.github.io/logos/api/hermes.html) - Language & embedding utility (STT, TTS, NLP, embeddings, LLM gateway)
  - Sophia, Talos, and Apollo API docs will be added as specifications become available
- **Local Generation**: Run `./scripts/generate-api-docs.sh` to build documentation locally
- **Auto-Publishing**: Documentation is automatically rebuilt and published via GitHub Actions when OpenAPI specs change
- See `docs/api/README.md` for details on adding new API documentation

CI/CD and Validation
- Automated validation of all canonical artifacts runs on every push and pull request.
- **Cypher Ontology**: Syntax validation using Neo4j 5.13.0 (`ontology/core_ontology.cypher`)
- **SHACL Shapes**: RDF/Turtle syntax validation using rdflib (`ontology/shacl_shapes.ttl`)
- **OpenAPI Contract**: OpenAPI 3.1.0 specification validation using swagger-cli (`contracts/hermes.openapi.yaml`)
- See `.github/workflows/validate-artifacts.yml` for the complete validation pipeline.

SHACL Validation Strategy
- **Default CI Gate (pyshacl)**: Fast, connectionless validation runs automatically on every push/PR ✅
  - Tests in `tests/integration/ontology/test_shacl_pyshacl.py` validate shapes against fixtures without requiring Neo4j
  - Ensures SHACL shapes are syntactically correct and fixtures conform to expectations
  - **This is the primary gate** - PRs must pass these tests to merge
- **Integration Tests (Neo4j+n10s)**: Opt-in validation for comprehensive testing 🔧
  - Tests in `tests/integration/ontology/test_shacl_neo4j_validation.py` validate data using Neo4j's n10s plugin
  - Requires Neo4j with n10s plugin installed and `RUN_NEO4J_SHACL=1` environment variable
  - Runs weekly or can be triggered manually via workflow dispatch
  - For local setup instructions, see `docs/PHASE1_VERIFY.md` - M2 section "Neo4j n10s Integration Tests (Opt-In)"
  - Workflow: `.github/workflows/shacl-neo4j-validation.yml`

## Phase 1 Verification and Gate

**Phase 1 Status: Complete** ✅

Phase 1 formalized the HCG ontology, SHACL validation, development infrastructure, and CLI prototype.

- **Verification Checklist**: See `docs/old/PHASE1_VERIFY.md` (archival) alongside the living `docs/phase1/PHASE1_SPEC.md`
- **Milestone Gates**: Each milestone is verified through automated tests that produce individual badges:
  - **M1** (HCG Store/Retrieve): [![M1 Gate](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m1-neo4j-crud.yml)
  - **M2** (SHACL Validation): [![M2 Gate](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m2-shacl-validation.yml)
  - **M3** (Planning): [![M3 Gate](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m3-planning.yml)
  - **M4** (End-to-End Demo): [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml)

**Completed Features:**
- ✅ Neo4j HCG infrastructure with core ontology (`core_ontology.cypher`)
- ✅ SHACL validation shapes (`shacl_shapes.ttl`) with pyshacl and Neo4j n10s support
- ✅ Milvus vector database integration for embeddings
- ✅ Apollo CLI prototype for goal/plan/state interaction
- ✅ Sophia orchestrator with CWM-A, CWM-G, Planner, Executor
- ✅ Hermes language utilities (STT, TTS, NLP, embeddings, LLM gateway)
- ✅ Talos hardware abstraction layer with simulated interfaces
- ✅ E2E pick-and-place demo with full causal graph tracking
- ✅ Automated CI/CD with milestone gate tests

**Tools & Scripts:**
- **E2E Prototype Script**: Run `./scripts/e2e_prototype.sh` to test the complete flow (Apollo → Sophia → Talos → HCG)
- **Planner Stub Service**: Run `./scripts/start_planner.sh` to start the planner API stub for M3/M4 testing (see `planner_stub/README.md`)

**M4 Pick-and-Place Demo:**
- **Demo Overview**: See `docs/M4_DEMO_ASSETS.md` for comprehensive demo documentation
- **Complete Walkthrough**: Follow `docs/PICK_AND_PLACE_WALKTHROUGH.md` for step-by-step instructions
- **Quick Demo**: Run `./scripts/run_m4_demo.sh` to execute the full demo with metrics capture

## Phase 2 Verification and Gate

**Phase 2 Status: ✅ COMPLETE**

Phase 2 extends LOGOS with Sophia/Hermes services, Apollo dual surfaces (CLI + browser), perception pipeline integration, and diagnostics/persona features.

- **Specification**: `docs/architecture/PHASE2_SPEC.md`
- **Verification Checklist**: `docs/operations/PHASE2_VERIFY.md`
- **Verification Evidence**: `apollo/docs/evidence/` (screenshots + API responses)
- **Milestone Gates**: Each milestone verified through automated tests:
  - **P2-M1** (Services Online): [![P2-M1 Gate](https://github.com/c-daly/logos/actions/workflows/phase2-e2e.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/phase2-e2e.yml) ✅ Complete
  - **P2-M2** (Apollo Dual Surface): [![Apollo CI](https://github.com/c-daly/apollo/actions/workflows/ci.yml/badge.svg)](https://github.com/c-daly/apollo/actions/workflows/ci.yml) [![Apollo E2E](https://github.com/c-daly/apollo/actions/workflows/e2e.yml/badge.svg)](https://github.com/c-daly/apollo/actions/workflows/e2e.yml) ✅ Complete
  - **P2-M3** (Perception & Imagination): [![Hermes CI](https://github.com/c-daly/hermes/actions/workflows/ci.yml/badge.svg)](https://github.com/c-daly/hermes/actions/workflows/ci.yml) [![Sophia CI](https://github.com/c-daly/sophia/actions/workflows/ci.yml/badge.svg)](https://github.com/c-daly/sophia/actions/workflows/ci.yml) ✅ Complete
  - **P2-M4** (Observability): [![P2-M4 Gate](https://github.com/c-daly/logos/actions/workflows/phase2-otel.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/phase2-otel.yml) ✅ Complete (CWM-E deferred to P3)

**Completed Features:**
- ✅ Sophia API with /plan, /state, /simulate, /ingest endpoints
- ✅ Hermes API with STT, TTS, NLP, embeddings, LLM gateway
- ✅ Apollo browser app with WebSocket real-time updates
- ✅ Apollo CLI with full SDK integration
- ✅ Media ingestion pipeline (upload → processing → HCG storage)
- ✅ Apollo media upload UI component (apollo#110 merged)
- ✅ MediaSample ontology with SHACL shapes
- ✅ CWM-A normalized state emission (CWMState envelopes)
- ✅ OpenTelemetry observability stack
- ✅ Persona diary integration

**Deferred to Phase 3:**
- ⏸️ Automatic CWM-E reflection (attention/working-memory modeling)

## 📊 Project Assessment

**Quick Summary:**
- **Phase 1:** ✅ Complete
- **Phase 2:** ✅ Complete — core services, dual surfaces, media ingestion, and CWM state emission all verified

**Phase 2 Evidence:** Playwright verification screenshots and API responses in `apollo/docs/evidence/`.

**Deferred to Phase 3:** Automatic CWM-E reflection (requires attention/working-memory modeling).

Notes and next steps
- The `core_ontology.cypher` and `shacl_shapes.ttl` are intentionally minimal, syntactically valid, and contain comments indicating where the full ontology and constraints described in the spec will be extended.
- This repo is the canonical place for future ontology updates, SHACL extensions, contract evolution, and HCG infra changes.
- Historical action items and research notes now live under `docs/old/`; current planning lives in the phase-specific specs and GitHub Project board.

## Contributing

Project LOGOS is not currently accepting external contributions.

**Resources:**
- Review the [Code of Conduct](CODE_OF_CONDUCT.md)
- See [SECURITY.md](SECURITY.md) for security policies

**Ways to Contribute:**
- 🐛 Report bugs and issues
- 📖 Improve documentation
- 💡 Suggest new features aligned with our non-linguistic cognition philosophy
- 🔧 Submit pull requests
- 🧪 Add tests and improve coverage
- 🌐 Extend the ontology for new domains
- 📝 Write blog posts or tutorials

**Questions?** Open a [GitHub Discussion](https://github.com/c-daly/logos/discussions) or file an issue.

## License

Project LOGOS is released under the [MIT License](LICENSE). See the LICENSE file for details.

## Community and Outreach

- 📝 [Blog Post Series](docs/outreach/BLOG_SERIES_PLAN.md): "Building a Non-Linguistic Mind"
- 📄 [Research Paper](docs/outreach/RESEARCH_PAPER_OUTLINE.md): In preparation
- 🎥 Demo Video: Coming Q1 2025
- 💬 Join the discussion on [GitHub Discussions](https://github.com/c-daly/logos/discussions)

## Acknowledgments

Project LOGOS builds on decades of cognitive architecture research and modern graph database technologies. We're grateful to the open-source community and the researchers who paved the way for non-linguistic AI systems.
