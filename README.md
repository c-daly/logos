# Project LOGOS — Meta Repository

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
3. Use the `ontology/core_ontology.cypher` and `ontology/shacl_shapes.ttl` files to initialize and validate the HCG (see Section 4.3.1).

Project Management
- See `.github/PROJECT_BOARD_SETUP.md` for instructions on setting up the GitHub Project Board, labels, milestones, and issue tracking system.
- Use `.github/scripts/generate_issues.py` to automatically create issues from the action items document.
- Weekly progress reports are automatically generated every Monday via GitHub Actions.
- All project tracking infrastructure is documented in `.github/README.md`.

Notes and next steps
- The `core_ontology.cypher` and `shacl_shapes.ttl` are intentionally minimal, syntactically valid, and contain comments indicating where the full ontology and constraints described in the spec will be extended.
- This repo is the canonical place for future ontology updates, SHACL extensions, contract evolution, and HCG infra changes.
- See `docs/action_items.md` for the complete task breakdown and current progress.
