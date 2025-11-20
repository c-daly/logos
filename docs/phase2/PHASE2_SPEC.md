# Phase 2 Specification — Perception & Apollo UX

Phase 2 extends the Phase 1 prototype into a Talos-optional, perception-driven assistant with dual interfaces (CLI + browser) and a multimodal LLM co-processor. This file will track the authoritative scope as work moves out of `docs/old/`.

## Goals
1. **Sophia services** — Stand up a running `/plan` + `/state` API backed by the HCG (Neo4j + SHACL), planner/executor, and simulation hooks.
2. **Hermes services** — Provide `/embed_text`, minimal NLP/STT/TTS, and Milvus persistence/health endpoints so Apollo can retrieve grounded embeddings.
3. **Apollo Surfaces** — Maintain the CLI while shipping a browser UI with diagnostics/explainability panes and LLM-backed chat.
4. **Perception Workflows** — Support Talos-free media streams (video/images/audio) that flow through CWM-G (JEPA) for next-frame prediction and reasoning.
5. **Diagnostics & Persona** — Build the observability stack, persona entries, and saved views so stakeholders can inspect LOGOS behavior in real time.
6. **Milestones** — Deliver the Phase 2 milestone criteria (detailed below) and update `PHASE1_VERIFY` successors.

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
- **CWM-E implementation**:
  - Backing store: reuse Neo4j (new labels `EmotionState`, `PersonaEntry`) plus Milvus for embedding/search if needed.
  - Reflection job: FastAPI background task (or separate worker) runs every N minutes, queries recent `PersonaEntry` + plan/state nodes, and computes sentiment/confidence/trust tags using a lightweight model (e.g., fine-tuned classifier or rule set derived from plan outcomes).
  - Writes `(:EmotionState { sentiment, confidence, caution, timestamp })` nodes linked to `(:Process)` and `(:PersonaEntry)` via `[:EMOTION_FOR]`.
  - Planner/executor must read the latest emotion nodes to adjust strategy (e.g., avoid risky capability when `caution` high). Apollo/Hermes use the same nodes to shape persona tone.
- **Imagination / simulation pipeline**:
  - `/simulate` accepts `{ capability_id, context }` payloads. Context carries entity references, pointers to sensor frames, and optional Talos metadata (even in Talos-free scenarios, pass the perception sample ID).
  - CWM-G (JEPA runner) performs k-step rollout and returns predicted states plus confidence; create `(:ImaginedProcess)`/`(:ImaginedState)` nodes with `imagined:true`, linked to the triggering plan.
  - Record metadata (model version, horizon, assumptions) in the nodes so Apollo/Hermes can narrate “what was imagined” and why.
  - Provide both a CPU-friendly runner (for Talos-free deployments) and hooks to swap in Talos/Gazebo simulators when hardware is present.

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
- CWM-E reflection pass consumes persona entries + plan/state history to derive qualitative tags (confidence, caution, trust). Implement a periodic job (FastAPI background task or separate worker) that writes `(:EmotionState)` nodes linked to processes/entities. Planner/executor must read those tags when deciding strategies, and Apollo’s chat persona should reference them to adjust tone. Start with a rule-based classifier (e.g., degrade confidence after failed plan, increase caution after errors) and evolve toward a learned model once enough data exists.

### Verification / CI
- Add GitHub Actions workflows:
  - `phase2-sophia-service.yml` – run API tests, SHACL checks.
  - `phase2-hermes-service.yml` – run embedding tests, Milvus smoke.
  - `phase2-apollo-web.yml` – npm lint/build/test.
  - `phase2-perception.yml` – run JEPA sim smoke tests (optional).
- Document manual demo steps in `docs/phase2/VERIFY.md` (CLI + browser + perception).

## Milestones & Acceptance Criteria

| Milestone | Description | Acceptance Criteria |
|-----------|-------------|---------------------|
| **P2-M1** — Services Online | Sophia/Hermes APIs running locally + in CI | `/plan`, `/state`, `/simulate`, `/embed_text`, `/simple_nlp`, `/stt`, `/tts` respond with healthy status; CI workflows green; docs updated |
| **P2-M2** — Apollo Dual Surface | CLI refactored + browser app MVP | Shared SDK integrates with Sophia/Hermes, browser renders chat + plan viewer, CLI remains functional |
| **P2-M3** — Perception & Imagination | CWM-G handles Talos-free media streams + `/simulate` exposed | Media pipeline stores embeddings, `/simulate` returns imagined states recorded in Neo4j, Milvus smoke tests pass |
| **P2-M4** — Diagnostics & Persona | Observability stack + CWM-E reflection in place | EmotionState nodes produced, Apollo persona uses them, dashboards/log export ready, demo capture flows documented |

## Verification Checklist

**See:** `docs/phase2/VERIFY.md` for comprehensive verification criteria, demo instructions, evidence requirements, and CI workflow references.

### Quick Reference
- [ ] P2-M1 evidence: API test logs + screenshots of `/docs` for both services.
- [ ] P2-M2 evidence: Video/screenshot of browser UI and CLI session, plus automated tests.
- [ ] P2-M3 evidence: Recorded `/simulate` run with imagined nodes visible in Neo4j Browser.
- [ ] P2-M4 evidence: Diagnostics dashboard snapshot, persona entry log, and demo capture artifact.

All evidence should be uploaded to `logs/p2-m{1-4}-verification/` directories following the structure defined in VERIFY.md.

## Status Tracking
- Issues labeled `phase:2` + relevant `surface:*`, `capability:*`, `domain:*` tags.
- Project board views grouped by phase should pull directly from this spec.

> This is a living document. As Phase 2 planning solidifies, add subsections for milestones, acceptance criteria, and demos. Keep archival Phase 1 docs under `docs/old/` untouched.
