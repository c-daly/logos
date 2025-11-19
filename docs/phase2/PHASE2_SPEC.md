# Phase 2 Specification — Perception & Apollo UX

Phase 2 extends the Phase 1 prototype into a Talos-optional, perception-driven assistant with dual interfaces (CLI + browser) and a multimodal LLM co-processor. This file will track the authoritative scope as work moves out of `docs/old/`.

## Goals
1. **Sophia services** — Stand up a running `/plan` + `/state` API backed by the HCG (Neo4j + SHACL), planner/executor, and simulation hooks.
2. **Hermes services** — Provide `/embed_text`, minimal NLP/STT/TTS, and Milvus persistence/health endpoints so Apollo can retrieve grounded embeddings.
3. **Apollo Surfaces** — Maintain the CLI while shipping a browser UI with diagnostics/explainability panes and LLM-backed chat.
4. **Perception Workflows** — Support Talos-free media streams (video/images/audio) that flow through CWM-G (JEPA) for next-frame prediction and reasoning.
5. **Diagnostics & Persona** — Build the observability stack, persona entries, and saved views so stakeholders can inspect LOGOS behavior in real time.
6. **Milestones** — Deliver the Phase 2 milestone criteria (to be detailed below) and update `PHASE1_VERIFY` successors.

## Deliverables
- **Sophia service**
  - FastAPI app exposing `/plan`, `/state`, `/simulate`.
  - Uses the Neo4j driver + SHACL validation helpers shipped in this repo.
  - Planner/executor implementation pulled from `logos/tests/phase1` seeds and expanded to consume CWM-G/CWM-E metadata.
  - Docker image + Compose definition that can be launched alongside Neo4j/Milvus.
- **Hermes service**
  - FastAPI app exposing `/embed_text`, `/simple_nlp`, `/stt`, `/tts`.
  - Embedding path writes vectors to Milvus, returns `embedding_id` + metadata and stores the linkage in Neo4j when requested.
  - STT/TTS can be thin wrappers around existing OSS models (e.g., Whisper/Torc) but must conform to the OpenAPI contract.
  - Health endpoints for Milvus collections and Hermès internal queues.
- **Apollo surfaces**
  - CLI remains (refactor to consume the new Sophia/Hermes endpoints via a shared SDK).
  - Browser app (Vite + React + TypeScript) with:
    - Chat panel (LLM-backed, persona aware).
    - Graph viewer pulling from Neo4j via a read-only API.
    - Diagnostics tabs (logs, plan timelines, capability telemetry).
  - Shared component library consumed by CLI + browser (for consistent formatting of plan/state output).
- **Perception workflows**
  - Media ingest service (browser uploads, file watcher, or WebRTC) that hands frames to CWM-G (JEPA).
  - Samples stored as embeddings in Milvus + references in Neo4j.
  - Hooks so Apollo can request “imagination” runs (`/simulate`) for visual questions.
- **Diagnostics/Persona toolchain**
  - Structured log exporter to capture every plan/state change, also feeding persona entries.
  - Persona diary stored as HCG nodes that Apollo/Hermes can query for voice/tone.
  - Demo capture script (record browser session + logs) for verification evidence.
- **Verification**
  - New `docs/phase2/VERIFY.md` describing milestone gates, demo instructions, and evidence requirements.
  - CI workflows for the new services (unit tests, lint, Milvus smoke).

## Implementation Notes
### Sophia service
- Stack: Python 3.11, FastAPI, Neo4j driver, SHACL loader, existing planner modules.
- Authentication: token-based (GitHub PAT or local header) with middleware to enforce read/write scopes.
- `/plan`: accepts goal struct, reads from Neo4j, runs planner, returns process graph + simulation predictions.
- `/state`: returns latest entity states + persona/diagnostic metadata for Apollo.
- `/simulate`: triggers CWM-G to roll out short-horizon predictions; results tagged `imagined:true` in Neo4j.
- Packaging: Dockerfile extending the repo’s base image; Compose service `sophia-api` linked to Neo4j/Milvus.

### Hermes service
- Stack: Python 3.11, FastAPI, sentence-transformer (or equivalent) for embeddings, optional Whisper/TTS backend.
- `/embed_text`: writes to Milvus via pymilvus, tracks metadata in Neo4j (optional) and returns `embedding_id`.
- `/simple_nlp`: tokenization, POS tagging using spaCy or similar.
- STT/TTS endpoints can wrap CLI tools initially; interface defined in `contracts/hermes.openapi.yaml`.
- Health check: `/health` returns Milvus connectivity + queue status.

### Apollo browser
- Stack: Vite + React + TypeScript, Tailwind (or equivalent) for styling.
- Connects to Sophia/Hermes via a shared SDK (generated from OpenAPI).
- Components: Chat (LLM prompt orchestrator), Plan viewer, Graph explorer (Neo4j via read-only API), Diagnostics panel, Persona diary.
- Authentication: GitHub OAuth or token injection; config via `.env`.

### Perception pipeline / CWM-G
- Media ingestion service publishes frames to a queue; JEPA runner consumes and writes predicted states to Neo4j.
- Provide a lightweight simulator mode (no Talos) for browser uploads and a Talos-connected mode when hardware is present.

### Diagnostics & persona
- Use OpenTelemetry to ship logs/metrics to a local collector; dashboards can be simple JSON/CLI at first.
- Persona entries stored as `(:PersonaEntry {timestamp, summary, sentiment, related_process})` nodes; Apollo/Hermes query them to drive tone.

### Verification / CI
- Add GitHub Actions workflows:
  - `phase2-sophia-service.yml` – run API tests, SHACL checks.
  - `phase2-hermes-service.yml` – run embedding tests, Milvus smoke.
  - `phase2-apollo-web.yml` – npm lint/build/test.
  - `phase2-perception.yml` – run JEPA sim smoke tests (optional).
- Document manual demo steps in `docs/phase2/VERIFY.md` (CLI + browser + perception).

## Status Tracking
- Issues labeled `phase:2` + relevant `surface:*`, `capability:*`, `domain:*` tags.
- Project board views grouped by phase should pull directly from this spec.

> This is a living document. As Phase 2 planning solidifies, add subsections for milestones, acceptance criteria, and demos. Keep archival Phase 1 docs under `docs/old/` untouched.
