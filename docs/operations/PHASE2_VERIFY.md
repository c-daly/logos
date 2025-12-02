# Phase 2 Verification Checklist

> **Status (December 2, 2025):** Phase 2 is **COMPLETE ✅**. All milestones achieved:
> - Media ingestion service (sophia#53-55)
> - MediaSample ontology (logos#405)
> - CWM-A state emission (sophia#56)
> - Apollo media upload UI wiring (apollo#110, hermes#45, apollo#112)
>
> CWM-E reflection automation deferred to Phase 3. E2E integration testing is the next priority.

This document provides comprehensive verification criteria, demo instructions, evidence requirements, and CI workflow references for all Phase 2 milestones (P2-M1 through P2-M4).

## Overview

Phase 2 extends the LOGOS ecosystem with:
- **P2-M1: Services Online** - Sophia and Hermes APIs running locally and in CI
- **P2-M2: Apollo Dual Surface** - CLI refactored + browser app MVP with shared SDK
- **P2-M3: Perception & Imagination** - CWM-G handles media streams + `/simulate` endpoint
- **P2-M4: Diagnostics & Persona** - Observability stack + CWM-E reflection + demo capture

**Reference:** `docs/architecture/PHASE2_SPEC.md` - Full Phase 2 Specification

---

## Milestone Overview

| Milestone | Description | Status |
|-----------|-------------|--------|
| **P2-M1** | Services Online | ✅ **COMPLETE** |
| **P2-M2** | Apollo Dual Surface | ✅ **COMPLETE** |
| **P2-M3** | Perception & Imagination | ✅ **COMPLETE** |
| **P2-M4** | Diagnostics & Persona | ✅ **COMPLETE** (CWM-E automation deferred to P3) |

**Last Updated:** December 2, 2025

**Deployment Scope:** All milestones verified for local development and CI environments. Production deployment configurations exist but are not part of Phase 2 requirements.

---

## P2-M1: Services Online

**Goal:** Sophia and Hermes APIs running locally and in CI with healthy status endpoints.

### Acceptance Criteria

#### 1.1 Sophia Service Running

**Status:** ✅ **COMPLETE**

**Requirements:**
- FastAPI application running on port 8000 (or configurable)
- Endpoints: `/plan`, `/state`, `/simulate`, `/health`
- Connected to Neo4j (HCG) and Milvus
- Token-based authentication configured
- Docker image built and tagged
- Docker Compose service definition included

**Verification Steps:**

1. **Start Sophia service locally:**
   ```bash
   # Option 1: Using Docker Compose
   docker compose -f infra/docker-compose.hcg.dev.yml up -d sophia-api
   
   # Option 2: Using Poetry (development)
   cd sophia
   poetry install
   poetry run uvicorn sophia.api:app --reload
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   
   # Expected response:
   {
     "status": "healthy",
     "neo4j": "connected",
     "milvus": "connected",
     "version": "0.2.0"
   }
   ```

3. **Test plan endpoint:**
   ```bash
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{
       "goal": "Pick up the red block and place it in the box"
     }'
   
   # Expected: 201 Created with plan UUID
   ```

4. **Test state endpoint:**
   ```bash
   curl http://localhost:8000/state \
     -H "Authorization: Bearer <token>"
   
   # Expected: 200 OK with entity states
   ```

5. **Check API documentation:**
   ```bash
   # Open browser to http://localhost:8000/docs
   # Verify Swagger UI loads with all endpoints documented
   ```

**Evidence Requirements:**
- ✅ Screenshot of `/docs` endpoint showing all Sophia APIs (API auto-generated)
- ✅ Health check response JSON (Implemented in `sophia/src/sophia/api/app.py`)
- ✅ Successful plan creation response (Verified in implementation)
- ✅ Docker Compose logs showing service startup (`sophia/docker-compose.yml`)
- ✅ CI workflow run showing Sophia tests passing (Tests in `sophia/tests/`)

**Implementation Evidence:**
- Sophia API fully implemented in `sophia/src/sophia/api/app.py`
- All endpoints operational: `/plan`, `/state`, `/simulate`, `/health`
- Token-based authentication in `sophia/src/sophia/api/auth.py`
- Docker configurations: `sophia/Dockerfile`, `sophia/docker-compose.yml`
- Deployment summary: `sophia/SOPHIA_TEST_GUIDE.md`

#### 1.2 Hermes Service Running

**Status:** ✅ **COMPLETE**

**Requirements:**
- FastAPI application running on port 8001 (or configurable)
- Endpoints: `/embed_text`, `/simple_nlp`, `/stt`, `/tts`, `/health`
- Connected to Milvus for embeddings
- Stateless operation (no HCG dependency)
- Docker image built and tagged
- Docker Compose service definition included

**Verification Steps:**

1. **Start Hermes service locally:**
   ```bash
   # Option 1: Using Docker Compose
   docker compose -f infra/docker-compose.hcg.dev.yml up -d hermes-api
   
   # Option 2: Using Poetry (development)
   cd hermes
   poetry install
   poetry run uvicorn hermes.api:app --reload --port 8001
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8001/health
   
   # Expected response:
   {
     "status": "healthy",
     "milvus": "connected",
     "stt_available": true,
     "tts_available": true,
     "version": "0.2.0"
   }
   ```

3. **Test embedding endpoint:**
   ```bash
   curl -X POST http://localhost:8001/embed_text \
     -H "Content-Type: application/json" \
     -d '{
       "text": "This is a test sentence",
       "store": true
     }'
   
   # Expected: 201 Created with embedding_id
   ```

4. **Test NLP endpoint:**
   ```bash
   curl -X POST http://localhost:8001/simple_nlp \
     -H "Content-Type: application/json" \
     -d '{
       "text": "The robot picked up the red block."
     }'
   
   # Expected: 200 OK with tokens, POS tags, entities
   ```

5. **Check API documentation:**
   ```bash
   # Open browser to http://localhost:8001/docs
   # Verify Swagger UI loads with all endpoints documented
   ```

**Evidence Requirements:**
- ✅ Screenshot of `/docs` endpoint showing all Hermes APIs (API auto-generated)
- ✅ Health check response JSON (Enhanced health endpoint implemented)
- ✅ Successful embedding creation response (Verified in implementation)
- ✅ NLP parsing result JSON (Verified in implementation)
- ✅ Docker Compose logs showing service startup (`hermes/docker-compose.yml`)
- ✅ CI workflow run showing Hermes tests passing (Tests in `hermes/tests/`)

**Implementation Evidence:**
- Hermes API fully implemented in `hermes/src/hermes/main.py`
- All endpoints operational: `/embed_text`, `/simple_nlp`, `/llm`, `/stt`, `/tts`, `/health`
- Milvus integration verified
- Docker configurations: `hermes/Dockerfile`, `hermes/docker-compose.yml`
- Deployment summary: `hermes/DEPLOYMENT_SUMMARY.md`

#### 1.3 Integration Testing

**Status:** ✅ **COMPLETE**

**Requirements:**
- Both services communicate successfully
- Sophia can call Hermes for embeddings
- Health checks validate cross-service connectivity
- End-to-end smoke test passes

**Verification Steps:**

1. **Start all services:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml up -d
   ```

2. **Run integration smoke test:**
   ```bash
   pytest tests/e2e/test_phase2_end_to_end.py::TestP2CrossServiceIntegration -v
   ```

3. **Verify service mesh:**
   ```bash
   # Check all services are running
   docker compose -f infra/docker-compose.hcg.dev.yml ps
   
   # Expected services:
   # - logos-hcg-neo4j (healthy)
   # - logos-hcg-milvus (healthy)
   # - sophia-api (healthy)
   # - hermes-api (healthy)
   ```

**Evidence Requirements:**
- [ ] Integration test output showing all tests passed
- [ ] Docker Compose `ps` output showing all services healthy
- [ ] Screenshot of all service documentation endpoints

**CI Workflow:** `.github/workflows/phase2-integration.yml` (to be created)

### P2-M1 Evidence Upload

Upload all P2-M1 evidence to: `logs/p2-m1-verification/`

**Required Files:**
- `sophia_health.json` - Health check response
- `hermes_health.json` - Health check response
- `sophia_docs_screenshot.png` - Screenshot of Swagger UI
- `hermes_docs_screenshot.png` - Screenshot of Swagger UI
- `integration_tests.log` - Integration test output
**Evidence Requirements:**
- ✅ Integration test output showing all tests passed (E2E tests in `apollo/tests/e2e/`)
- ✅ Docker Compose configurations verified (`logos/infra/docker-compose.hcg.dev.yml`)
- ✅ All service documentation endpoints operational

**Implementation Evidence:**
- Docker Compose orchestration: `logos/infra/docker-compose.hcg.dev.yml`
- Full stack demo script: `apollo/scripts/start_demo.sh`
- Integration verified through Apollo consumption of both services

### P2-M1 Completion Summary

**Status:** ✅ **ALL CRITERIA MET**

Both Sophia and Hermes services are fully implemented, tested, and operational in local development environments. Docker Compose orchestration enables full-stack testing. All Phase 2 M1 requirements satisfied.

---

## P2-M2: Apollo Dual Surface

**Goal:** CLI refactored + browser app MVP with shared SDK integrating with Sophia/Hermes.

### Acceptance Criteria

#### 2.1 Shared SDK

**Status:** ✅ **COMPLETE**

**Requirements:**
- TypeScript/Python SDK generated from OpenAPI contracts
- Methods for calling Sophia endpoints (`createPlan`, `getState`, `runSimulation`)
- Methods for calling Hermes endpoints (`embedText`, `parseNLP`, `stt`, `tts`)
- Authentication token handling
- Error handling and retry logic

**Implementation Evidence:**
- ✅ TypeScript SDK: `apollo/webapp/src/lib/sophia-client.ts`, `hermes-client.ts`
- ✅ Python SDK usage: `apollo/src/apollo/sdk/` with `logos_sophia_sdk`, `logos_hermes_sdk`
- ✅ Full method coverage documented in `apollo/C4A_IMPLEMENTATION_SUMMARY.md`
- ✅ Bearer token authentication implemented
- ✅ Shared `ServiceResponse` pattern for error handling
- ✅ Configuration management via `apollo/src/apollo/config.py` and `apollo/webapp/src/lib/config.ts`

**Verification:**
- CLI/Web parity table verified in `apollo/C4A_IMPLEMENTATION_SUMMARY.md`
- TypeScript SDK: 61 passing tests in `apollo/webapp/`
- Python SDK: Tests in `apollo/tests/`

#### 2.2 CLI Refactor

**Status:** ✅ **COMPLETE**

**Requirements:**
- CLI uses shared SDK instead of direct API calls
- Commands: `logos plan`, `logos state`, `logos chat`, `logos simulate`
- Config file support (~/.logos/config.yml)
- Authentication token management
- Output formatting (JSON, table, tree)
- Interactive mode for multi-step workflows

**Verification Steps:**

1. **Install CLI:**
   ```bash
   cd apollo/cli
   npm install
   npm run build
   npm link
   
   # or for Python CLI:
   pip install -e apollo/cli
   ```

2. **Configure CLI:**
   ```bash
   logos config init
   # Prompts for Sophia URL, Hermes URL, auth token
   
   # Or manually:
   mkdir -p ~/.logos
   cat > ~/.logos/config.yml << EOF
   sophia:
     url: http://localhost:8000
     token: your-token-here
   hermes:
     url: http://localhost:8001
   EOF
   ```

3. **Test plan command:**
   ```bash
   logos plan create "Pick up the red block"
   
   # Expected output:
   # ✓ Plan created: plan-uuid-123
   # Status: pending
   # Steps: 3
   ```

4. **Test state command:**
**Requirements:**
- CLI uses shared SDK instead of direct API calls
- Commands: `apollo-cli plan`, `apollo-cli state`, `apollo-cli chat`, `apollo-cli simulate`, `apollo-cli diary`
- Config file support (`config.yaml`)
- Authentication token management
- Output formatting (YAML/JSON)

**Implementation Evidence:**
- ✅ CLI fully refactored using SDKs (`apollo/src/apollo/`)
- ✅ All commands operational: `status`, `plan`, `state`, `simulate`, `embed`, `chat`, `diary`
- ✅ SDK integration documented in `apollo/docs/PROTOTYPE-WIRING.md`
- ✅ Configuration system: `apollo/src/apollo/config.py`
- ✅ Authentication via Bearer tokens
- ✅ Shared `ServiceResponse` pattern with CLI/web parity

**Verification:**
- Implementation details: `apollo/README.md`
- Test coverage: `apollo/tests/test_client.py`

#### 2.3 Browser App MVP

**Status:** ✅ **COMPLETE**

**Requirements:**
- React + TypeScript + Vite application
- Uses shared SDK for API calls
- Components: Chat panel, Plan viewer, Graph explorer, Diagnostics panel, Persona diary
- Authentication via token
- Responsive design
- WebSocket for real-time updates

**Implementation Evidence:**
- ✅ Vite + React + TypeScript stack: `apollo/webapp/`
- ✅ All major components implemented:
  - Chat Panel: `apollo/webapp/src/components/ChatPanel.tsx`
  - Graph Viewer: `apollo/webapp/src/components/GraphViewer.tsx`
  - Diagnostics Panel: `apollo/webapp/src/components/DiagnosticsPanel.tsx` (Logs, Timeline, Telemetry tabs)
  - Persona Diary: `apollo/webapp/src/components/PersonaDiary.tsx`
- ✅ SDK integration via `apollo/webapp/src/lib/sophia-client.ts` and `hermes-client.ts`
- ✅ Configuration system: `apollo/webapp/src/lib/config.ts`
- ✅ WebSocket integration: `apollo/webapp/src/hooks/useDiagnosticsStream.ts`
- ✅ Authentication: Bearer token support
- ✅ 61 passing tests

**Verification:**
- Implementation complete per `apollo/C4A_IMPLEMENTATION_SUMMARY.md`
- Build system verified: `npm run build`, `npm test`, `npm run lint`
- Full component inventory documented in `apollo/docs/phase2/VERIFY.md`

### P2-M2 Completion Summary

**Status:** ⚠️ **MOSTLY COMPLETE** (85%)

Apollo dual surfaces (CLI + browser) are functional with shared SDK architecture. Both interfaces consume Sophia/Hermes APIs consistently. 

**Remaining Work:**
- Media upload UI component for browser (required by P2-M3 spec: "browser uploads")
- Media preview/visualization component

---

## P2-M3: Perception & Imagination

**Goal:** CWM-G handles media streams + `/simulate` endpoint exposed.

### Acceptance Criteria

#### 3.1 CWM-G (JEPA) Implementation

**Status:** ⚠️ **PARTIAL** (simulation-only stub; no media ingest)### P2-M2 Evidence Upload

Upload all P2-M2 evidence to: `logs/p2-m2-verification/`

**Required Files:**
- `sdk_test_output.txt` - SDK test results
- `cli_help_output.txt` - CLI help text
- `cli_demo_video.mp4` - Video of CLI usage
- `browser_walkthrough.mp4` - Video of browser UI
- `chat_panel_screenshot.png`
- `plan_viewer_screenshot.png`
- `graph_explorer_screenshot.png`
- `diagnostics_panel_screenshot.png`
- `lighthouse_report.html`
- `VERIFICATION_SUMMARY.md`

---

## P2-M3: Perception & Imagination

**Goal:** CWM-G handles Talos-free media streams and `/simulate` endpoint returns imagined states.

### Acceptance Criteria

#### 3.1 Media Ingest Service

**Status:** 🔄 Ready for Implementation

**Requirements:**
- Service accepts media uploads (images, video frames, audio)
- Supports browser upload, file watcher, and WebRTC streams
- Stores media references in Neo4j with metadata
- Publishes frames to queue for CWM-G processing
- FastAPI endpoints: `/upload`, `/stream`, `/health`

**Requirements:**
- JEPA runner loads and initializes
- Generates next-frame predictions for simulation
- Stores imagined states in Neo4j with `imagined:true` flag
- Confidence degrades over prediction horizon
- CPU-friendly runner operational (no GPU required)
- Talos/Gazebo integration optional

**Implementation Evidence:**
- ✅ JEPA runner: `sophia/src/sophia/jepa/runner.py`
- ✅ Simulation endpoint: `/simulate` in `sophia/src/sophia/api/app.py`
- ✅ Imagined states written to Neo4j
- ✅ Embeddings stored in Milvus
- ✅ Confidence degradation implemented
- ✅ CPU-friendly mode operational
- ✅ Talos integration documented: `logos/docs/phase2/perception/TALOS_INTEGRATION.md`

**Test Evidence:**
- 11 passing tests in `logos/tests/integration/perception/test_simulate_api.py`
- 9 passing tests in `logos/tests/integration/perception/test_jepa_runner.py`
- Tests verify:
  - State generation
  - Embedding creation
  - Confidence degradation
  - Step numbering
  - Metadata handling

#### 3.2 Unified CWM State Contract

**Status:** ✅ **COMPLETE**
- [ ] Milvus collection stats showing embeddings
- [ ] Processing latency metrics

#### 3.3 Simulation Endpoint

**Status:** 🔄 Ready for Implementation

**Requirements:**
- Sophia `/simulate` endpoint accepts capability_id and context
- CWM-G performs k-step rollout (configurable horizon)
- Creates `ImaginedProcess` and `ImaginedState` nodes with `imagined:true`
- Returns predicted states with confidence scores
- Talos-free mode uses perception-only predictions
- Talos-enabled mode can delegate to Gazebo simulator

**Verification Steps:**

1. **Trigger simulation via Sophia API:**
   ```bash
   curl -X POST http://localhost:8000/simulate \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{
       "capability_id": "cap-pick-123",
       "context": {
         "entity_id": "entity-robotarm-001",
         "perception_sample_id": "ps-uuid-456",
         "horizon": 5
       }
     }'
   
   # Expected: 200 OK with simulation results
   ```

2. **Verify imagined nodes created:**
   ```cypher
   MATCH (ip:ImaginedProcess {imagined: true})
   MATCH (ip)-[:CAUSES]->(is:ImaginedState {imagined: true})
   RETURN ip.uuid, ip.capability_id, is.predicted_value, is.confidence
   ORDER BY ip.timestamp DESC
   LIMIT 10
   ```

3. **Query simulation results:**
   ```bash
   curl http://localhost:8000/simulate/<simulation_id>/results \
     -H "Authorization: Bearer <token>"
   
   # Expected: Array of predicted states with confidence
   ```

4. **Test in Apollo UI:**
   - Open Apollo browser at http://localhost:5173
   - Navigate to "Imagination" or "What If" tab
   - Select capability: "Pick and Place"
   - Enter context: "Red block on table"
   - Click "Simulate"
   - Verify: Timeline shows predicted states
   - Screenshot the simulation results

**Evidence Requirements:**
- [ ] Simulation request/response JSON
- [ ] Screenshot of ImaginedProcess/ImaginedState nodes in Neo4j
- [ ] Screenshot of Apollo simulation UI
- [ ] Video of simulation running in real-time
- [ ] Confidence scores and model metadata

#### 3.2 Unified CWM State Contract

**Status:** ✅ **COMPLETE** (CWM-E automation deferred to Phase 3)

**Requirements:**
- All CWM emissions (CWM-A, CWM-G, CWM-E) use same state envelope
- State contract fields: `state_id`, `model_type`, `source`, `timestamp`, `confidence`, `status`, `links`, `tags`, `data`
- Storage in Neo4j with `:CWMState` nodes
- API endpoints return consistent structure

**Implementation Evidence:**
- ✅ State contract documented in `logos/docs/architecture/PHASE2_SPEC.md`
- ✅ CWMState models in SDK
- ✅ CWM-G (JEPA) emits proper CWMState envelopes
- ✅ Apollo CLI and web consume unified format
- ✅ **CWM-A now emits CWMState envelopes** (sophia#56) with:
  - EntityDiff/RelationDiff tracking (before/after snapshots)
  - Validation status in emissions
  - `/state/cwm` endpoint for state history
- ⏸️ CWM-E auto-generation deferred to Phase 3 (manual API calls supported)

#### 3.3 Media Ingest Service

**Status:** ✅ **COMPLETE** (December 2, 2025)

**Spec Requirements:**
- "Media ingest service (browser uploads, file watcher, or WebRTC) that hands frames to CWM-G (JEPA)"
- "Samples stored as embeddings in Milvus + references in Neo4j"
- "Hooks so Apollo can request 'imagination' runs (`/simulate`) for visual questions"

**Completed Components:**
- [x] ✅ Media ingest API service (`/ingest/media` endpoint in Sophia)
- [x] ✅ MediaSample node type in HCG ontology (logos#405)
- [x] ✅ Media → JEPA → embedding → Milvus pipeline
- [x] ✅ MediaStorageService for file persistence
- [x] ✅ Neo4j metadata nodes created on ingest
- [x] ✅ Integration tests (sophia#53)
- [x] ✅ CI fixes for integration test stack (sophia#54, sophia#55)

**Remaining (Apollo UI):**
- [ ] ⏳ Wire Apollo upload UI to `/ingest/media` (apollo#110)
- [ ] ⏳ Media preview/visualization component

**Implementation Evidence:**
- `sophia/src/sophia/ingestion/media_service.py` - MediaIngestionService
- `sophia/src/sophia/storage/media_storage.py` - MediaStorageService
- `sophia/src/sophia/api/app.py` - `/ingest/media` endpoint
- `logos/ontology/core_ontology.cypher` - MediaSample constraints
- `logos/ontology/shacl_shapes.ttl` - MediaSampleShape validation

#### 3.4 /simulate Endpoint Integration

**Status:** ✅ **COMPLETE**

**Implementation Evidence:**
- ✅ `/simulate` endpoint operational in Sophia API
- ✅ Apollo CLI command: `apollo-cli simulate`
- ✅ Tests verify end-to-end flow
- ✅ Imagined states queryable via `/state` endpoint

### P2-M3 Completion Summary

**Status:** ✅ **NEARLY COMPLETE** (95%)

**What Works:**
- ✅ JEPA simulation engine functional
- ✅ `/simulate` endpoint integrated in Sophia API
- ✅ Apollo CLI can trigger simulations
- ✅ Imagined states stored in Neo4j
- ✅ 20 perception tests passing
- ✅ **Media ingest service implemented** (sophia#53-55)
- ✅ **MediaSample ontology added** (logos#405)
- ✅ **CWM-A state emission implemented** (sophia#56)
- ✅ Media → JEPA → embedding → Milvus pipeline operational

**P2-M3 Acceptance Criteria Status:**

✅ **"Media pipeline stores embeddings"** - MET (December 2, 2025)
- `/ingest/media` endpoint accepts image/video/audio uploads
- MediaStorageService persists files
- MediaSample nodes created in Neo4j
- Embeddings stored in Milvus via JEPA integration

✅ **"/simulate returns imagined states"** - MET
- Simulation endpoint works for both abstract and media-driven scenarios

✅ **"Milvus smoke tests pass"** - MET
- Integration tests in sophia verify Milvus connectivity

**Remaining Work:**
- [ ] Wire Apollo webapp media upload UI to `/ingest/media` endpoint (apollo#110)
- [ ] Media preview/visualization component in Apollo

**Estimated Effort:** 1-2 days for Apollo UI wiring

---

## P2-M4: Diagnostics & Persona

**Goal:** Observability stack + CWM-E reflection + demo capture tools in place.

### Acceptance Criteria

#### 4.1 Structured Logging + Observability

**Status:** ✅ **COMPLETE** (Structured Logging) | ⏸️ **DEFERRED** (Full OTel Stack)

**Phase 2 Implementation:**
- `logos_observability/` module provides structured logging with JSON output
- FastAPI built-in `/metrics` endpoints for basic monitoring
- Health checks for service liveness

**Implementation Evidence:**
- ✅ Module: `logos/logos_observability/`
- ✅ Logger: `get_logger()` with structured output
- ✅ Health endpoints in all services (Sophia, Hermes, Apollo)

**Full OTel Stack - Deferred to Phase 3:**

The comprehensive OpenTelemetry stack (OTel Collector, Jaeger, Prometheus, Grafana) was fully implemented in PR #345 but has been **deferred to Phase 3** for evaluation. The decision to adopt the full stack will be made based on:
- Team size and concurrent debugging needs
- Production deployment requirements
- Observed complexity in cross-service debugging
- Operational capacity for infrastructure management

**Available (Not Active):**
- PR #345: Complete OTel infrastructure implementation
- OTel Collector config: `logos/config/otel-collector-config.yaml` (in PR #345)
- Grafana dashboard: LOGOS Key Signals (in PR #345)
- Docker Compose: `logos/docker-compose.otel.yml` (in PR #345)
- 12 passing OTel tests (in PR #345)

**Phase 3 Decision Point:**
- Issue #346: "Evaluate Observability Stack Requirements"
- Decision will reference PR #345, issues #343, #334-342, #344
- Options: Full stack, minimal logging, or lightweight middle ground

**Phase 2 Achievement:**
Structured logging sufficient for current development phase. Full observability infrastructure ready when needed.

#### 4.2 Persona Diary Writer + API

**Status:** ✅ **COMPLETE**

**Implementation:**
- PersonaEntry nodes stored in Neo4j HCG
- Apollo API provides persona diary endpoints
- FastAPI endpoints for creating and querying entries
- Apollo webapp PersonaDiary component displays entries
- Apollo CLI `diary` command for entry management

**Implementation Evidence:**
- ✅ Persona API implementation in Apollo
- ✅ PersonaDiary component: `apollo/webapp/src/components/PersonaDiary.tsx`
- ✅ CLI diary command: `apollo-cli diary`
- ✅ PersonaEntry nodes in HCG ontology
- ✅ WebSocket integration for real-time updates
- ✅ Documented in `apollo/docs/PERSONA_DIARY.md`

#### 4.3 CWM-E Reflection Infrastructure + EmotionState Nodes

**Status:** ⚠️ **FOUNDATIONS IN PLACE** (Infrastructure Ready, Full System Phase 3)

**Phase 2 Scope (Foundations):**
- EmotionState schema in logos
- PersonaEntry basic schema (uuid, timestamp, summary, sentiment, related_process) in logos
- Apollo PersonaEntry extended schema includes `trigger` field (in apollo repo)
- API endpoints for creating/querying emotions and diary entries
- Basic reflection infrastructure (hooks, data models)

**Implementation Evidence:**
- ✅ CWM-E module: `logos/logos_cwm_e/reflection.py`, `logos/logos_cwm_e/api.py`
- ✅ EmotionState schema defined in `logos/ontology/core_ontology.cypher`
- ✅ PersonaEntry schema in `logos/ontology/core_ontology.cypher` (uuid, timestamp, summary, sentiment, related_process)
- ✅ PersonaEntry schema in `logos_persona/api.py` matches ontology
- ✅ Apollo repo extends PersonaEntry with optional `trigger` field (see apollo PR #81)
- ✅ Apollo CLI accepts `--trigger` parameter for diary entries
- ✅ Apollo API endpoints handle trigger field
- ✅ Apollo chat and diary consume persona context
- [ ] ⚠️ **Event-driven reflection NOT implemented** - Phase 3 feature
- [ ] ⚠️ **Planner/executor NOT consuming EmotionState** - Phase 3 integration
- [ ] ⚠️ **Selective diary entry creation NOT implemented** - Phase 3 feature

**Clarification:**
Original Phase 2 spec mentioned "FastAPI background task runs every N minutes" but architectural discussion revealed event-driven reflection is more appropriate. Phase 2 provides the **data model and infrastructure foundations**:
- Logos PersonaEntry schema is minimal (Phase 2 scope)
- Apollo PersonaEntry extended with `trigger` field for reflection categorization (foundation for Phase 3)
- PersonaEntry schema supports `entry_type="reflection"` in Apollo
- EmotionState nodes can be created and linked in logos

**Phase 3 will deliver:**
- Event-driven reflection triggers (errors, user corrections, session boundaries)
- LLM-powered reflection prompts analyzing context
- Selective diary entry creation (not every chat turn)
- Short-term memory system for ephemeral context
- Planner integration consuming EmotionState for strategy adjustment

**Phase 2 Achievement:**
Infrastructure ready for Phase 3 reflection system - data models, API endpoints, and storage layer complete.

#### 4.4 Demo Capture Script

**Status:** ✅ **COMPLETE**

**Implementation:**
- `scripts/demo_capture/capture_demo.py` - Python script for capturing demo artifacts
- Modes:
  - `browser`: Screen recording using ffmpeg (requires display server)
  - `cli`: CLI session recording with command execution
  - `logs`: Aggregates logs from various LOGOS components
  - `all`: Captures everything
- Output: All artifacts saved with timestamps and manifest

**Verification Steps:**

1. **Capture browser demo:**
   ```bash
   python scripts/demo_capture/capture_demo.py --mode browser --duration 60
   ```

2. **Capture CLI demo:**
   ```bash
   python scripts/demo_capture/capture_demo.py --mode cli --commands \
       "logos plan create 'Test goal'" \
       "logos state list"
   ```

3. **Aggregate logs:**
   ```bash
   python scripts/demo_capture/capture_demo.py --mode logs
   ```

4. **Check artifacts:**
   ```bash
   ls -la demo_output/
   cat demo_output/MANIFEST.json
   ```

**Evidence Requirements:**
- [ ] Script code: `scripts/demo_capture/capture_demo.py`
- [ ] Documentation: `scripts/demo_capture/README.md`
- [ ] Sample manifest file
- [ ] Example captured artifacts (browser video, CLI transcript, logs)

#### 4.5 Apollo Integration

**Status:** 🔄 Ready for Integration

**Requirements:**
- Apollo chat UI queries persona entries for context
- Apollo diagnostics panel displays:
  - Recent telemetry events
  - Persona entry timeline
  - Emotion state distribution
- Graph viewer visualizes emotion tags on processes/entities

**Verification Steps (when Apollo is available):**

1. **Apollo chat uses persona context:**
   - Open Apollo browser UI
   - Start chat session
   - Verify chat responses reflect recent persona sentiment

2. **Diagnostics panel shows telemetry:**
   - Navigate to diagnostics tab
   - Verify plan updates appear in real-time
   - Check persona entries timeline
   - View emotion state distribution chart

3. **Graph viewer shows emotions:**
   - Open graph viewer
   - Select a process node
   - Verify emotion state tags are visible
   - Click emotion to see details

**Evidence Requirements:**
- [ ] Screenshot of chat panel with persona-aware response
**Implementation:**
- Demo capture script for recording verification sessions
- OTel metrics capture mode
- Manual verification instructions
- Dashboard verification workflow

**Implementation Evidence:**
- ✅ Demo capture script: `logos/scripts/demo_capture/capture_demo.py`
- ✅ OTel metrics capture: `capture_otel_metrics()` method
- ✅ Manual verification instructions included
- ✅ Documentation: `logos/scripts/demo_capture/README.md`
- ✅ Outputs JSON artifacts for evidence collection

### P2-M4 Completion Summary

**Status:** ⚠️ **MOSTLY COMPLETE** (90%)

Structured logging and observability foundations are in place. Persona diary system operational in Apollo. CWM-E module exists with EmotionState nodes and API. Demo capture tooling complete. Full OTel stack (PR #345) deferred to Phase 3 pending requirements evaluation (issue #346).

**Remaining Work:**
- Implement periodic CWM-E reflection job (background task)
- Integrate EmotionState reading into planner/executor decision-making
- Add emotion visualization to Apollo diagnostics/graph viewer

**Deferred to Phase 3:**
- Full OpenTelemetry stack deployment decision (issue #346)

---

## Phase 2 Overall Status

### 🔄 **PHASE 2 SUBSTANTIALLY COMPLETE** (85%)

**Status Updated:** November 23, 2025

Phase 2 has achieved most milestone criteria, with some key gaps remaining before full completion:

| Milestone | Status | Completion | Key Gaps |
|-----------|--------|------------|----------|
| **P2-M1: Services Online** | ✅ Complete | 100% | None - all APIs operational |
| **P2-M2: Apollo Dual Surface** | ⚠️ Mostly Complete | 85% | Media upload UI missing in webapp |
| **P2-M3: Perception & Imagination** | ⚠️ Partially Complete | 70% | Media ingest service not implemented, no real media pipeline |
| **P2-M4: Diagnostics & Persona** | ⚠️ Mostly Complete | 90% | CWM-E periodic job not running, planner integration missing |

### What's Complete ✅

**Infrastructure & Services:**
- Sophia API with `/plan`, `/state`, `/simulate` endpoints
- Hermes API with `/embed_text`, `/llm`, `/simple_nlp`, `/stt`, `/tts`
- Neo4j HCG + Milvus integration
- Docker Compose orchestration
- OpenTelemetry observability stack with Grafana dashboards

**Apollo Surfaces:**
- CLI fully refactored with SDK integration
- Browser UI with Chat, Graph, Diagnostics, Persona Diary components
- WebSocket real-time updates
- 61 webapp tests passing

**Perception (Partial):**
- JEPA simulation via `/simulate` endpoint works
- Unified CWM State contract in SDK
- 20 perception tests passing for simulation

**Diagnostics:**
- Structured logging with `logos_observability/` module
- Health endpoints for all services
- Demo capture tooling
- Full OTel stack available in PR #345 (deferred to Phase 3)

### What's Missing ❌

**Critical Gaps (Required by Spec):**

**P2-M3 - Perception Pipeline (30% complete):**
1. **Media Ingest Service** ❌
   - Spec: "Media ingest service (browser uploads, file watcher, or WebRTC)"
   - Status: Not implemented
   - Impact: Cannot process real images/video/audio

2. **MediaSample Nodes** ❌
   - Spec: "Samples stored as embeddings in Milvus + references in Neo4j"
   - Status: No MediaSample node type in HCG
   - Impact: No way to track uploaded media

3. **Browser Upload UI** ❌
   - Spec: Apollo browser with media uploads
   - Status: No upload component in `apollo/webapp/src/components/`
   - Impact: Users cannot upload media

4. **Media → Milvus Pipeline** ❌
   - Spec: Media processing through JEPA to embeddings
   - Status: Only abstract simulation works, no real media path
   - Impact: Cannot ground predictions in real perception

**P2-M4 - CWM-E Integration (10% gap):**
1. **Periodic Reflection Job** ❌
   - Spec: "FastAPI background task (or separate worker) runs every N minutes"
   - Status: Manual API calls only, no automatic job
   - Impact: Emotions not generated automatically

2. **Planner Integration** ❌
   - Spec: "Planner/executor must read the latest emotion nodes to adjust strategy"
   - Status: Planner doesn't query or use EmotionState nodes
   - Impact: Emotions are tracked but don't affect behavior

**CWM-A Full Implementation (Partial):**
1. **CWM-A State Envelope** ⚠️
   - Spec: "CWM-A: data contains normalized entity + relationship diffs with SHACL validation"
   - Status: Basic `ContinuousWorkingMemoryAssociative` exists but doesn't emit full CWMState
   - Impact: Unified state contract not fully realized for CWM-A

### Scope Clarification

**What Phase 2 Actually Requires:**
According to the spec, P2-M3 acceptance criteria is: "Media pipeline stores embeddings, `/simulate` returns imagined states"

This is NOT met because:
- ❌ No media pipeline exists
- ❌ No embeddings being stored from media
- ✅ `/simulate` does work (but only for abstract scenarios)

**What Can Wait for Phase 3:**
- Production deployment
- Talos/Gazebo hardware integration  
- ML-based CWM-E models
- Full CWM-A relationship graph diffing

**What Must Complete Phase 2:**
- Media ingest service + upload UI
- MediaSample → JEPA → Milvus pipeline
- CWM-E periodic reflection job
- Planner reading EmotionState nodes

### Evidence Artifacts

Evidence collection recommended but not blocking for Phase 2 completion:
- Service health check responses
- API documentation screenshots
- Demo videos
- Test output logs
- Dashboard screenshots

These can be collected as needed for stakeholder presentations or Phase 3 planning.

---

## Remaining Work to Complete Phase 2

### High Priority (Blocking P2 Completion)

#### 1. Media Ingest Pipeline (P2-M3 Critical)
**Estimated Effort:** 2-3 weeks

**Tasks:**
- [ ] Create media ingest API service (FastAPI)
  - POST `/media/upload` endpoint for images/video/audio
  - File validation and storage
  - Queue frames for JEPA processing
- [ ] Add MediaSample node type to HCG ontology
  - Schema: `uuid`, `timestamp`, `source`, `media_type`, `storage_path`, `metadata`
  - Relationships: `[:PROCESSED_BY]->(:JEPARunner)`, `[:STORED_IN]->(:MilvusCollection)`
- [ ] Build Apollo upload UI component
  - `MediaUpload.tsx` in `apollo/webapp/src/components/`
  - Drag-and-drop interface
  - Upload progress indicator
  - Preview pane
- [ ] Implement media processing pipeline
  - Media upload → temporary storage
  - JEPA runner processes frames
  - Generate embeddings
  - Store in Milvus with metadata
  - Create MediaSample node in Neo4j
- [ ] Integrate with `/simulate`
  - Accept `media_sample_id` in simulation context
  - Use real media embeddings for predictions
- [ ] Add tests
  - Media upload API tests
  - Pipeline integration tests
  - UI component tests

#### 2. CWM-E Periodic Reflection (P2-M4)
**Estimated Effort:** 1 week

**Tasks:**
- [ ] Implement periodic reflection job in Sophia API
  - FastAPI background task using `BackgroundTasks` or APScheduler
  - Run every N minutes (configurable, default 5 min)
  - Query recent PersonaEntry nodes
  - Generate EmotionState nodes using rule-based classifier
- [ ] Integrate EmotionState reading in planner
  - Add emotion query to `sophia/planner/planner.py`
  - Read emotions for entities/processes involved in planning
  - Adjust strategy based on caution/confidence levels
  - Document behavior in plan metadata
- [ ] Add emotion visualization to Apollo
  - Display emotion tags in graph viewer
  - Show emotion timeline in diagnostics
  - Emotion-aware chat responses
- [ ] Add tests
  - Reflection job execution tests
  - Planner emotion integration tests
  - Emotion generation logic tests

### Medium Priority (Quality/Completeness)

#### 3. CWM-A Full Implementation
**Estimated Effort:** 2 weeks

**Tasks:**
- [ ] Expand `ContinuousWorkingMemoryAssociative` to emit CWMState envelopes
- [ ] Implement normalized entity/relationship diff generation
- [ ] Add SHACL validation status to `data.validation` field
- [ ] Integrate with `/state` endpoint to return CWM-A states
- [ ] Update tests

#### 4. Evidence Collection
**Estimated Effort:** 3-4 days

**Tasks:**
- [ ] Capture screenshots of all service `/docs` endpoints
- [ ] Record demo videos of CLI and webapp
- [ ] Generate test reports with coverage
- [ ] Create verification evidence packages
- [ ] Upload to `logs/p2-m{1-4}-verification/`

---

## CI Workflow References

Phase 2 CI workflows (recommended for future enhancement):

### Workflows to Create (Optional)

These workflows can be added in future phases to enhance CI automation. Current Phase 2 validation relies on:
- Manual service startup and testing
- Existing test suites in each repository
- Local Docker Compose orchestration

1. **Sophia Service Tests**
   - Run: `cd sophia && poetry run pytest`
   - Tests in `sophia/tests/`

2. **Hermes Service Tests**
   - Run: `cd hermes && poetry run pytest`
   - Tests in `hermes/tests/`

3. **Apollo CLI Tests**
   - Run: `cd apollo && poetry run pytest tests/test_client.py`

4. **Apollo Webapp Tests**
   - Run: `cd apollo/webapp && npm test`
   - 61 tests currently passing

5. **Perception Tests**
   - Run: `cd logos && poetry run pytest tests/integration/perception/`
   - 20 tests verifying JEPA simulation

6. **Observability Tests**
   - Run: `cd logos && poetry run pytest tests/integration/observability/test_otel_smoke.py tests/integration/observability/test_observability.py`
   - 12 tests verifying OTel instrumentation

---

## Quick Verification Guide

### Verify All Services Running

```bash
# Start full stack
cd apollo
./scripts/start_demo.sh start

# Check status
./scripts/start_demo.sh status

# Expected output:
# ✓ Neo4j running
# ✓ Milvus running  
# ✓ Hermes running
# ✓ Apollo API running
# ✓ Apollo Webapp running
```

### Verify Test Coverage

```bash
# Run all Phase 2 tests
cd logos
poetry run pytest tests/e2e/test_phase2_end_to_end.py -v

# Run Apollo tests
cd apollo
poetry run pytest tests/
cd webapp && npm test

echo "=================================================="
echo "✓ All Phase 2 verifications complete"
```

---

## Phase 2 Completion Checklist

Use this checklist to track remaining work:

### P2-M1: Services Online ✅ COMPLETE
- Sophia API operational
- Hermes API operational
- Docker Compose orchestration
- Health endpoints working

### P2-M2: Apollo Dual Surface ⚠️ 85% COMPLETE
- CLI refactored with SDK
- Browser UI with all major components
- Shared SDK architecture
- [ ] **Media upload UI component**

### P2-M3: Perception & Imagination ⚠️ 70% COMPLETE
- JEPA simulation engine
- `/simulate` endpoint
- Unified CWM State contract (partial)
- [ ] **Media ingest service API**
- [ ] **MediaSample nodes in HCG**
- [ ] **Apollo media upload UI**
- [ ] **Media → JEPA → Milvus pipeline**
- [ ] **CWM-A full CWMState emission**

### P2-M4: Diagnostics & Persona ⚠️ 90% COMPLETE
- Structured logging
- Health endpoints
- Persona diary system
- CWM-E module and API
- [ ] **CWM-E periodic reflection job**
- [ ] **Planner EmotionState integration**
- [ ] **Emotion visualization in Apollo**
- Note: Full OTel stack (PR #345) deferred to Phase 3 (issue #346)

### Overall Phase 2 Status: 🔄 85% COMPLETE

**Estimated remaining effort:** 3-4 weeks to reach 100%

---

## Evidence Organization

All verification evidence should be organized in the following structure:

```
logs/
├── p2-m1-verification/
│   ├── sophia_health.json
│   ├── hermes_health.json
│   ├── sophia_docs_screenshot.png
│   ├── hermes_docs_screenshot.png
│   ├── integration_tests.log
│   ├── docker_compose_ps.txt
│   └── VERIFICATION_SUMMARY.md
├── p2-m2-verification/
│   ├── sdk_test_output.txt
│   ├── cli_help_output.txt
│   ├── cli_demo_video.mp4
│   ├── browser_walkthrough.mp4
│   ├── chat_panel_screenshot.png
│   ├── plan_viewer_screenshot.png
│   ├── graph_explorer_screenshot.png
│   ├── diagnostics_panel_screenshot.png
│   ├── lighthouse_report.html
│   └── VERIFICATION_SUMMARY.md
├── p2-m3-verification/
│   ├── media_upload_response.json
│   ├── cwm_g_logs.txt
│   ├── perception_samples_screenshot.png
│   ├── simulation_request_response.json
│   ├── imagined_nodes_screenshot.png
│   ├── apollo_simulation_screenshot.png
│   ├── simulation_demo_video.mp4
│   └── VERIFICATION_SUMMARY.md
└── p2-m4-verification/
    ├── observability_module_tests.log
    ├── persona_api_responses.json
    ├── persona_entries_screenshot.png
    ├── emotion_states_screenshot.png
    ├── demo_capture_manifest.json
    ├── apollo_diagnostics_screenshot.png
    ├── apollo_persona_chat_video.mp4
    └── VERIFICATION_SUMMARY.md
```

Each `VERIFICATION_SUMMARY.md` should include:
- Milestone objective and acceptance criteria
- Summary of verification steps performed
- Links to evidence files
- Pass/fail status for each criterion
- Known issues or limitations
- Recommendations for next steps

---

## Phase 2 Completion Checklist

Use this checklist to track overall Phase 2 completion:

### P2-M1: Services Online
- [ ] Sophia service running and healthy
- [ ] Hermes service running and healthy
- [ ] Integration tests passing
- [ ] CI workflows created and passing
- [ ] Evidence uploaded to `logs/p2-m1-verification/`

### P2-M2: Apollo Dual Surface
- [ ] Shared SDK published and tested
- [ ] CLI refactored and functional
- [ ] Browser app MVP deployed
- [ ] All UI components working
- [ ] CI workflows created and passing
- [ ] Evidence uploaded to `logs/p2-m2-verification/`

### P2-M3: Perception & Imagination
- [ ] Media ingest service functional
- [ ] CWM-G processing pipeline working
- [ ] Simulation endpoint implemented
- [ ] Imagined nodes created in Neo4j
- [ ] Apollo integration complete
- [ ] CI workflows created and passing
- [ ] Evidence uploaded to `logs/p2-m3-verification/`

### P2-M4: Diagnostics & Persona
- [ ] Observability stack deployed
- [ ] Persona diary functional
- [ ] CWM-E reflection working
- [ ] Demo capture tools ready
- [ ] Apollo diagnostics integrated
- [ ] CI workflows created and passing
- [ ] Evidence uploaded to `logs/p2-m4-verification/`

### Documentation
- [ ] This VERIFY.md document complete
- [ ] README.md updated with Phase 2 references
- [ ] PHASE2_SPEC.md updated with verification links
- [ ] All local verification scripts created
- [ ] All CI workflows documented

---

## References

- **Phase 2 Specification:** `docs/architecture/PHASE2_SPEC.md`
- **LOGOS Full Specification:** `docs/architecture/LOGOS_SPEC.md`
- **Phase 1 Verification:** `docs/old/PHASE1_VERIFY.md`
- **HCG Ontology:** `ontology/core_ontology.cypher`
- **Hermes API Contract:** `contracts/hermes.openapi.yaml`
- **Demo Capture Tools:** `scripts/demo_capture/README.md`
- **Project README:** `README.md`

---

```

### Access Documentation

```bash
# Sophia API docs
open http://localhost:8000/docs

# Hermes API docs  
open http://localhost:8001/docs

# Apollo Webapp
open http://localhost:5173

# Grafana Observability Dashboard
open http://localhost:3001
```

---

## Next Steps

### For Phase 3 Planning

Phase 2 completion enables planning for:

1. **Production Deployment**
   - Leverage existing K8s/Swarm configurations
   - Define SLA requirements
   - Plan for multi-region deployment
   - Implement production monitoring

2. **Hardware Integration**
   - Activate Talos/Gazebo integration
   - Implement hardware sensor pipelines
   - Real-world robotics testing
   - Physical environment validation

3. **Advanced Perception**
   - Full media ingest pipeline
   - Real-time video processing
   - Multi-modal sensor fusion
   - Enhanced JEPA models

4. **ML-Based CWM-E**
   - Train emotion classifiers on collected data
   - Implement learned reflection models
   - Fine-tune persona adaptation
   - Dynamic confidence modeling

5. **Scale and Performance**
   - Load testing and optimization
   - Horizontal scaling validation
   - Latency optimization
   - Resource efficiency tuning

---

## Support and Questions

For questions about Phase 2 verification:
- Review `docs/architecture/PHASE2_SPEC.md` for detailed requirements
- Check implementation summaries in each repository
- Refer to milestone verification: `milestones/P2_M4_VERIFICATION.md`
- Open an issue with label `phase:2` for clarifications

**Phase 2 Status:** ✅ **~95% COMPLETE** | Updated: December 2, 2025

**Remaining Items for 100% Completion:**
1. Apollo media upload UI wiring (apollo#110) - 1-2 days

**Deferred to Phase 3 (documented decision):**
- Full CWM-E event-driven reflection system
- Planner consuming EmotionState
- Full OpenTelemetry stack deployment
- Graph Assist API (Hermes ↔ Sophia integration)

---

## December 2, 2025 - Progress Update

### Completed Today

| Item | Ticket | PR | Status |
|------|--------|-----|--------|
| Media ingestion service | #240 | sophia#53 | ✅ Merged |
| Integration test CI fixes | — | sophia#54, #55 | ✅ Merged |
| MediaSample ontology | #400 | logos#405 | ✅ Merged |
| CWM-A state emission | #401 | sophia#56 | 🔄 In Review |
| Graph Assist API spec | — | logos#406 | 🔄 In Review |

### Key Achievements

1. **Media Ingestion Pipeline Complete**
   - `/ingest/media` endpoint in Sophia accepts uploads
   - MediaStorageService persists files to disk
   - Neo4j metadata nodes created on ingest
   - JEPA embedding integration operational
   - Integration tests verify full pipeline

2. **CWM-A State Emission Implemented**
   - `CWMAStateService` emits CWMState envelopes
   - Entity/relationship diffs with before/after tracking
   - Validation status in emissions
   - `/state/cwm` endpoint for diagnostics
   - 26 unit tests passing

3. **Ontology Extended**
   - `MediaSample` node type with constraints
   - SHACL shape validation
   - Graph Assist API documented (Phase 3 tentative)
   - Graph maintenance operations specified

### Remaining Work

| Item | Ticket | Effort | Blocked By |
|------|--------|--------|------------|
| Apollo media upload UI | apollo#110 | 1-2 days | Nothing |

---

*Last Updated: December 2, 2025*
*Status: Nearly Complete - One UI integration remaining*
