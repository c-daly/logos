# Phase 2 Verification Checklist

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
| **P2-M1** | Services Online | 🔄 In Progress |
| **P2-M2** | Apollo Dual Surface | 🔄 In Progress |
| **P2-M3** | Perception & Imagination | 🔄 In Progress |
| **P2-M4** | Diagnostics & Persona | ✅ Core Complete |

---

## P2-M1: Services Online

**Goal:** Sophia and Hermes APIs running locally and in CI with healthy status endpoints.

### Acceptance Criteria

#### 1.1 Sophia Service Running

**Status:** 🔄 Ready for Implementation

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
- [ ] Screenshot of `/docs` endpoint showing all Sophia APIs
- [ ] Health check response JSON
- [ ] Successful plan creation response
- [ ] Docker Compose logs showing service startup
- [ ] CI workflow run showing Sophia tests passing

**CI Workflow:** `.github/workflows/phase2-sophia-service.yml` (to be created)

**Local Test Script:**
```bash
# scripts/verify_phase2_m1_sophia.sh
./scripts/verify_phase2_m1_sophia.sh
```

#### 1.2 Hermes Service Running

**Status:** 🔄 Ready for Implementation

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
- [ ] Screenshot of `/docs` endpoint showing all Hermes APIs
- [ ] Health check response JSON
- [ ] Successful embedding creation response
- [ ] NLP parsing result JSON
- [ ] Docker Compose logs showing service startup
- [ ] CI workflow run showing Hermes tests passing

**CI Workflow:** `.github/workflows/phase2-hermes-service.yml` (to be created)

**Local Test Script:**
```bash
# scripts/verify_phase2_m1_hermes.sh
./scripts/verify_phase2_m1_hermes.sh
```

#### 1.3 Integration Testing

**Status:** 🔄 Ready for Implementation

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
   pytest tests/phase2/test_integration_smoke.py -v
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
- `docker_compose_ps.txt` - Service status output
- `VERIFICATION_SUMMARY.md` - Summary of verification results

---

## P2-M2: Apollo Dual Surface

**Goal:** CLI refactored + browser app MVP with shared SDK integrating with Sophia/Hermes.

### Acceptance Criteria

#### 2.1 Shared SDK

**Status:** 🔄 Ready for Implementation

**Requirements:**
- TypeScript/Python SDK generated from OpenAPI contracts
- Methods for calling Sophia endpoints (`createPlan`, `getState`, `runSimulation`)
- Methods for calling Hermes endpoints (`embedText`, `parseNLP`, `stt`, `tts`)
- Authentication token handling
- Error handling and retry logic
- Published as npm package and PyPI package (or vendored in monorepo)

**Verification Steps:**

1. **Install SDK (TypeScript):**
   ```bash
   npm install @logos/sdk
   # or if vendored:
   cd packages/logos-sdk
   npm install
   npm run build
   ```

2. **Test SDK in Node.js:**
   ```javascript
   import { SophiaClient, HermesClient } from '@logos/sdk';
   
   const sophia = new SophiaClient({ baseUrl: 'http://localhost:8000', token: 'test-token' });
   const hermes = new HermesClient({ baseUrl: 'http://localhost:8001' });
   
   // Test plan creation
   const plan = await sophia.createPlan({ goal: 'Test goal' });
   console.log('Plan created:', plan.uuid);
   
   // Test embedding
   const embedding = await hermes.embedText({ text: 'Test text' });
   console.log('Embedding created:', embedding.embedding_id);
   ```

3. **Install SDK (Python):**
   ```bash
   pip install logos-sdk
   # or if vendored:
   cd packages/logos-sdk-python
   poetry install
   ```

4. **Test SDK in Python:**
   ```python
   from logos_sdk import SophiaClient, HermesClient
   
   sophia = SophiaClient(base_url='http://localhost:8000', token='test-token')
   hermes = HermesClient(base_url='http://localhost:8001')
   
   # Test plan creation
   plan = sophia.create_plan(goal='Test goal')
   print(f'Plan created: {plan.uuid}')
   
   # Test embedding
   embedding = hermes.embed_text(text='Test text')
   print(f'Embedding created: {embedding.embedding_id}')
   ```

**Evidence Requirements:**
- [ ] SDK package.json or pyproject.toml
- [ ] Successful SDK test output (TypeScript and Python)
- [ ] Generated API client code from OpenAPI specs
- [ ] CI workflow showing SDK tests passing

**CI Workflow:** `.github/workflows/phase2-sdk.yml` (to be created)

#### 2.2 CLI Refactor

**Status:** 🔄 Ready for Implementation

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
   ```bash
   logos state list
   
   # Expected output (table format):
   # Entity          | State      | Last Updated
   # --------------- | ---------- | ------------
   # RobotArm01      | idle       | 2025-11-20 00:30:00
   # RedBlock        | at_table   | 2025-11-20 00:29:45
   ```

5. **Test interactive mode:**
   ```bash
   logos interactive
   
   # Starts REPL-style interface:
   # logos> plan create "Test goal"
   # logos> state show RobotArm01
   # logos> exit
   ```

**Evidence Requirements:**
- [ ] CLI help output (`logos --help`)
- [ ] Screenshot of plan creation
- [ ] Screenshot of state listing
- [ ] Video of interactive session
- [ ] Config file example

**CI Workflow:** `.github/workflows/phase2-apollo-cli.yml` (to be created)

#### 2.3 Browser App MVP

**Status:** 🔄 Ready for Implementation

**Requirements:**
- React + TypeScript + Vite application
- Uses shared SDK for API calls
- Components: Chat panel, Plan viewer, Graph explorer, Diagnostics panel
- Authentication via GitHub OAuth or token
- Responsive design (desktop and tablet)
- Deployed locally with `npm run dev`

**Verification Steps:**

1. **Start browser app:**
   ```bash
   cd apollo/web
   npm install
   npm run dev
   
   # Opens http://localhost:5173
   ```

2. **Configure authentication:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with:
   VITE_SOPHIA_URL=http://localhost:8000
   VITE_HERMES_URL=http://localhost:8001
   VITE_AUTH_TOKEN=your-token-here
   ```

3. **Test chat panel:**
   - Open browser to http://localhost:5173
   - Navigate to Chat tab
   - Enter: "What is the current state of RobotArm01?"
   - Verify: Response uses Hermes NLP + Sophia state query
   - Screenshot the conversation

4. **Test plan viewer:**
   - Navigate to Plans tab
   - Click "New Plan"
   - Enter goal: "Pick up the red block"
   - Verify: Plan tree renders with processes and states
   - Screenshot the plan visualization

5. **Test graph explorer:**
   - Navigate to Graph tab
   - Search for entity: "RobotArm01"
   - Verify: Node appears with relationships
   - Click node to see details panel
   - Screenshot the graph view

6. **Test diagnostics panel:**
   - Navigate to Diagnostics tab
   - Verify: Real-time logs appear
   - Verify: Telemetry metrics displayed
   - Screenshot the diagnostics view

**Evidence Requirements:**
- [ ] Video walkthrough of all UI components (2-3 minutes)
- [ ] Screenshot of chat panel with conversation
- [ ] Screenshot of plan viewer with visual plan
- [ ] Screenshot of graph explorer with entity
- [ ] Screenshot of diagnostics panel
- [ ] npm run build success output
- [ ] Lighthouse score (accessibility, performance)

**CI Workflow:** `.github/workflows/phase2-apollo-web.yml` (to be created)

### P2-M2 Evidence Upload

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

**Verification Steps:**

1. **Start media ingest service:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml up -d media-ingest
   ```

2. **Upload image via API:**
   ```bash
   curl -X POST http://localhost:8002/upload \
     -F "file=@test_image.jpg" \
     -F "metadata={\"source\":\"test\",\"timestamp\":\"2025-11-20T00:30:00Z\"}"
   
   # Expected: 201 Created with media_id
   ```

3. **Stream video frames:**
   ```bash
   # Start stream
   curl -X POST http://localhost:8002/stream/start \
     -H "Content-Type: application/json" \
     -d '{
       "source": "webcam",
       "fps": 10
     }'
   
   # Expected: stream_id returned
   ```

4. **Verify media in Neo4j:**
   ```cypher
   MATCH (m:MediaSample)
   RETURN m.uuid, m.timestamp, m.source, m.type
   ORDER BY m.timestamp DESC
   LIMIT 10
   ```

**Evidence Requirements:**
- [ ] Media upload response JSON
- [ ] Screenshot of media nodes in Neo4j Browser
- [ ] Stream start response
- [ ] Service logs showing frame processing

**CI Workflow:** `.github/workflows/phase2-perception.yml` (to be created)

#### 3.2 CWM-G (JEPA) Processing

**Status:** 🔄 Ready for Implementation

**Requirements:**
- JEPA model loads and initializes
- Consumes frames from media queue
- Generates next-frame predictions
- Stores embeddings in Milvus
- Creates `PerceptionSample` nodes in Neo4j
- CPU-friendly runner available (no GPU required for basic tests)

**Verification Steps:**

1. **Start CWM-G processor:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml up -d cwm-g-processor
   ```

2. **Upload image for processing:**
   ```bash
   # Upload image
   MEDIA_ID=$(curl -X POST http://localhost:8002/upload \
     -F "file=@robot_scene.jpg" | jq -r '.media_id')
   
   # Trigger JEPA processing
   curl -X POST http://localhost:8003/process/${MEDIA_ID}
   ```

3. **Verify perception sample created:**
   ```cypher
   MATCH (ps:PerceptionSample)-[:DERIVED_FROM]->(m:MediaSample)
   WHERE m.uuid = '<media_id>'
   RETURN ps.uuid, ps.prediction_confidence, ps.embedding_id
   ```

4. **Check embedding in Milvus:**
   ```python
   from pymilvus import connections, Collection
   
   connections.connect("default", host="localhost", port="19530")
   collection = Collection("perception_embeddings")
   
   # Search for similar samples
   results = collection.search(
       data=[embedding_vector],
       anns_field="embedding",
       param={"metric_type": "L2", "params": {"nprobe": 10}},
       limit=5
   )
   print(f"Found {len(results[0])} similar samples")
   ```

**Evidence Requirements:**
- [ ] CWM-G startup logs showing model loaded
- [ ] PerceptionSample nodes in Neo4j (screenshot)
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

### P2-M3 Evidence Upload

Upload all P2-M3 evidence to: `logs/p2-m3-verification/`

**Required Files:**
- `media_upload_response.json`
- `cwm_g_logs.txt`
- `perception_samples_screenshot.png`
- `simulation_request_response.json`
- `imagined_nodes_screenshot.png`
- `apollo_simulation_screenshot.png`
- `simulation_demo_video.mp4`
- `VERIFICATION_SUMMARY.md`

---

## P2-M4: Diagnostics & Persona

**Goal:** Observability stack + CWM-E reflection + demo capture tools in place.

### Acceptance Criteria

#### 4.1 Structured Logging + OpenTelemetry Export

**Status:** ✅ Complete

**Implementation:**
- `logos_observability/` module provides OpenTelemetry instrumentation
- Structured logging with JSON output for easy parsing
- Telemetry exporter captures plan/state updates, process execution, and persona events
- Local file storage in `/tmp/logos_telemetry/` with JSONL format

**Verification Steps:**

1. **Import and initialize telemetry:**
   ```python
   from logos_observability import setup_telemetry, get_logger
   
   setup_telemetry(service_name="sophia")
   logger = get_logger("sophia.planner")
   ```

2. **Log events and verify output:**
   ```python
   logger.log_plan_update(
       plan_uuid="test-plan-123",
       action="created",
       details={"goal": "example goal"}
   )
   ```

3. **Check telemetry files:**
   ```bash
   ls -la /tmp/logos_telemetry/
   cat /tmp/logos_telemetry/plan_update_*.jsonl
   ```

**Evidence Requirements:**
- [ ] Module code: `logos_observability/telemetry.py`, `logos_observability/exporter.py`
- [ ] Unit tests passing
- [ ] Telemetry output samples in logs
- [ ] CI workflow showing observability tests passing

**CI Workflow:** `.github/workflows/phase2-observability.yml` (to be created)

#### 4.2 Persona Diary Writer + API

**Status:** ✅ Complete

**Implementation:**
- `logos_persona/` module provides persona diary functionality
- PersonaEntry nodes stored in Neo4j HCG with properties:
  - `uuid`: Unique identifier
  - `timestamp`: Creation time
  - `summary`: Text summary of activity/interaction
  - `sentiment`: Emotional tone (e.g., "confident", "cautious", "neutral")
  - `related_process`: Optional link to Process node
- FastAPI endpoints for creating and querying entries
- Relationships: `(:PersonaEntry)-[:RELATES_TO]->(:Process)`

**Verification Steps:**

1. **Start Neo4j and initialize ontology with PersonaEntry constraints:**
   ```bash
   docker compose -f infra/docker-compose.hcg.dev.yml up -d neo4j
   # Ontology loading includes PersonaEntry constraints
   ```

2. **Create persona entries:**
   ```python
   from logos_persona import PersonaDiary
   from neo4j import GraphDatabase
   
   driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "logosdev"))
   diary = PersonaDiary(driver)
   
   entry = diary.create_entry(
       summary="Successfully completed pick-and-place task",
       sentiment="confident",
       related_process="process-uuid-123"
   )
   ```

3. **Query entries via API:**
   ```bash
   # Get recent entries
   curl http://localhost:8000/persona/entries?limit=10
   
   # Get entries by sentiment
   curl http://localhost:8000/persona/entries?sentiment=confident
   
   # Get sentiment summary
   curl http://localhost:8000/persona/sentiment/summary
   ```

4. **Verify in Neo4j Browser:**
   ```cypher
   MATCH (pe:PersonaEntry)
   RETURN pe
   ORDER BY pe.timestamp DESC
   LIMIT 10
   ```

**Evidence Requirements:**
- [ ] Module code: `logos_persona/diary.py`, `logos_persona/api.py`
- [ ] Ontology updates: `ontology/core_ontology.cypher` (PersonaEntry constraints)
- [ ] Screenshot of persona entries in Neo4j Browser
- [ ] API response examples
- [ ] Unit tests passing

#### 4.3 CWM-E Reflection Job + EmotionState Nodes

**Status:** ✅ Complete

**Implementation:**
- `logos_cwm_e/` module provides CWM-E reflection functionality
- EmotionState nodes stored in Neo4j with properties:
  - `uuid`: Unique identifier
  - `timestamp`: Creation time
  - `emotion_type`: Type of emotion (e.g., "confident", "cautious", "curious")
  - `intensity`: Confidence/strength (0.0-1.0)
  - `context`: Description of what triggered this emotion
  - `source`: Generation source (default: "cwm-e-reflection")
- Relationships:
  - `(:EmotionState)-[:TAGGED_ON]->(:Process)` - Emotion tagged on process
  - `(:EmotionState)-[:TAGGED_ON]->(:Entity)` - Emotion tagged on entity
  - `(:EmotionState)-[:GENERATED_BY]->(:PersonaEntry)` - Emotion derived from reflection
- Reflection job analyzes persona entries and generates emotion states
- FastAPI endpoints for triggering reflection and querying emotions

**Verification Steps:**

1. **Create persona entries with various sentiments:**
   ```python
   diary.create_entry(summary="Task completed", sentiment="confident")
   diary.create_entry(summary="Error encountered", sentiment="cautious")
   ```

2. **Run reflection job:**
   ```python
   from logos_cwm_e import CWMEReflector
   from neo4j import GraphDatabase
   
   driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "logosdev"))
   reflector = CWMEReflector(driver)
   
   # Analyze recent persona entries and generate emotions
   emotions = reflector.reflect_on_persona_entries(limit=10)
   ```

3. **Query via API:**
   ```bash
   # Run reflection job
   curl -X POST http://localhost:8000/cwm-e/reflect?limit=10
   
   # Get emotions for a process
   curl http://localhost:8000/cwm-e/emotions/process/{process_uuid}
   
   # Get emotions for an entity
   curl http://localhost:8000/cwm-e/emotions/entity/{entity_uuid}
   ```

4. **Verify in Neo4j Browser:**
   ```cypher
   MATCH (es:EmotionState)-[:TAGGED_ON]->(p:Process)
   RETURN es, p
   ORDER BY es.timestamp DESC
   LIMIT 10
   ```

5. **Planner/Executor consumption example:**
   ```python
   # Planners and executors can query emotion states for context
   emotions = reflector.get_emotions_for_process(process_uuid)
   
   # Adjust behavior based on emotion intensity
   if any(e.emotion_type == "cautious" and e.intensity > 0.7 for e in emotions):
       # Use more conservative planning strategy
       pass
   ```

**Evidence Requirements:**
- [ ] Module code: `logos_cwm_e/reflection.py`, `logos_cwm_e/api.py`
- [ ] Ontology updates: `ontology/core_ontology.cypher` (EmotionState constraints)
- [ ] Screenshot of emotion states in Neo4j Browser
- [ ] Screenshot showing emotion tags in Apollo diagnostics panel
- [ ] Unit tests passing

#### 4.4 Demo Capture Script

**Status:** ✅ Complete

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
- [ ] Screenshot of diagnostics panel with telemetry
- [ ] Screenshot of graph viewer with emotion tags
- [ ] Video demo of persona-aware chat (1-2 minutes)

### P2-M4 Evidence Upload

Upload all P2-M4 evidence to: `logs/p2-m4-verification/`

**Required Files:**
- `observability_module_tests.log` - Test output
- `persona_api_responses.json` - Sample API responses
- `persona_entries_screenshot.png` - Neo4j Browser screenshot
- `emotion_states_screenshot.png` - Neo4j Browser screenshot
- `demo_capture_manifest.json` - Example manifest
- `apollo_diagnostics_screenshot.png`
- `apollo_persona_chat_video.mp4`
- `VERIFICATION_SUMMARY.md`

---

## CI Workflow References

Phase 2 verification requires the following CI workflows to be created and passing:

### Workflows to Create

1. **`.github/workflows/phase2-sophia-service.yml`**
   - Run Sophia API unit tests
   - Test Neo4j and Milvus connectivity
   - Validate OpenAPI contract compliance
   - Build and tag Docker image

2. **`.github/workflows/phase2-hermes-service.yml`**
   - Run Hermes API unit tests
   - Test Milvus connectivity
   - Test STT/TTS endpoints (mock)
   - Validate OpenAPI contract compliance
   - Build and tag Docker image

3. **`.github/workflows/phase2-sdk.yml`**
   - Generate SDK from OpenAPI specs
   - Run SDK unit tests (TypeScript and Python)
   - Test SDK against live services (integration)
   - Publish SDK packages (on release)

4. **`.github/workflows/phase2-apollo-cli.yml`**
   - Run CLI unit tests
   - Test CLI commands against mock services
   - Build CLI binaries
   - Test installation process

5. **`.github/workflows/phase2-apollo-web.yml`**
   - Run npm lint
   - Run TypeScript compilation
   - Run unit tests (Jest/Vitest)
   - Run E2E tests (Playwright)
   - Build production bundle
   - Run Lighthouse audits

6. **`.github/workflows/phase2-perception.yml`**
   - Run CWM-G unit tests
   - Test media ingest service
   - Test JEPA model loading (CPU mode)
   - Test embedding creation in Milvus

7. **`.github/workflows/phase2-observability.yml`**
   - Run observability module tests
   - Test telemetry export
   - Test log aggregation

8. **`.github/workflows/phase2-integration.yml`**
   - Start all Phase 2 services
   - Run end-to-end integration tests
   - Test cross-service communication
   - Verify health checks

### Running CI Workflows Locally

To run workflows locally for debugging:

```bash
# Install act (https://github.com/nektos/act)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run a specific workflow
act -j phase2-sophia-service

# Run with specific event
act push -j phase2-integration

# Run with secrets
act -s GITHUB_TOKEN=<token>
```

---

## Local Verification Scripts

Create the following helper scripts in `scripts/` directory:

### `scripts/verify_phase2_m1_sophia.sh`
```bash
#!/bin/bash
# Verify Sophia service (P2-M1)
echo "Starting Sophia service verification..."
docker compose -f infra/docker-compose.hcg.dev.yml up -d sophia-api
sleep 5
curl http://localhost:8000/health | jq .
curl http://localhost:8000/docs
echo "✓ Sophia service verification complete"
```

### `scripts/verify_phase2_m1_hermes.sh`
```bash
#!/bin/bash
# Verify Hermes service (P2-M1)
echo "Starting Hermes service verification..."
docker compose -f infra/docker-compose.hcg.dev.yml up -d hermes-api
sleep 5
curl http://localhost:8001/health | jq .
curl http://localhost:8001/docs
echo "✓ Hermes service verification complete"
```

### `scripts/verify_phase2_all.sh`
```bash
#!/bin/bash
# Run all Phase 2 verifications
set -e

echo "Phase 2 Verification - Running all milestone checks"
echo "=================================================="

echo "P2-M1: Services Online"
./scripts/verify_phase2_m1_sophia.sh
./scripts/verify_phase2_m1_hermes.sh

echo "P2-M2: Apollo Dual Surface"
# SDK tests
pytest tests/phase2/test_sdk.py -v

# CLI tests
pytest tests/phase2/test_cli.py -v

# Browser tests
cd apollo/web && npm test && cd ../..

echo "P2-M3: Perception & Imagination"
pytest tests/phase2/test_perception.py -v
pytest tests/phase2/test_simulation.py -v

echo "P2-M4: Diagnostics & Persona"
pytest tests/test_observability.py -v
pytest tests/test_persona_diary.py -v
pytest tests/test_cwm_e_reflection.py -v

echo "=================================================="
echo "✓ All Phase 2 verifications complete"
```

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
- **LOGOS Full Specification:** `docs/architecture/LOGOS_SPEC_FLEXIBLE.md`
- **Phase 1 Verification:** `docs/old/PHASE1_VERIFY.md`
- **HCG Ontology:** `ontology/core_ontology.cypher`
- **Hermes API Contract:** `contracts/hermes.openapi.yaml`
- **Demo Capture Tools:** `scripts/demo_capture/README.md`
- **Project README:** `README.md`

---

## Support and Questions

For questions about Phase 2 verification:
- Review the PHASE2_SPEC.md for detailed requirements
- Check existing evidence in logs/m1-verification/ and logs/m4-verification/ for examples
- Refer to Phase 1 verification patterns for consistency
- Open an issue with label `phase:2` and `verification` for clarifications

**Phase 2 Status:** 🔄 In Progress | Target Completion: TBD

---

*Last Updated: 2025-11-20*
