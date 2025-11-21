# Phase 2 Metrics & Response Quality Notes

This file captures ideas for how to evaluate the quality and observability of Phase 2 responses (Sophia/Hermes APIs, Apollo browser/CLI, perception outputs). As we implement the metrics, link to scripts, dashboards, or evidence artifacts.

## 1. Response Latency & Availability

- **Plan/State APIs**: Track median/p95 latency for `/plan`, `/state`, `/simulate` while running the prototype scenario. Target < 2s for `/state`, < 5s for `/plan` and `/simulate`.
- **Hermes endpoints**: Record latency + success rate for `/embed_text`, `/simple_nlp`, `/stt`, `/tts` to ensure embeddings/logs populate diagnostics panels.
- **Diagnostics stream**: Verify log/telemetry events reach the browser within 250 ms of the underlying state change.

*How to capture*: CLI script hitting each endpoint with sample payloads, storing results in `logs/metrics/*.json`; optionally wire into a simple pytest benchmark or `scripts/metrics/run_latency_checks.py`.

## 2. CWMState Coverage & Consistency

- **Model coverage**: Ensure each UI pane displays examples from CWM-A, CWM-G, and CWM-E during a demo run. Record counts per model type.
- **Link integrity**: Randomly sample `state_id` entries in the UI and verify corresponding Neo4j nodes exist with matching metadata (`plan_id`, `entity_ids`, etc.).
- **Imagined vs observed ratio**: For `/simulate` requests, track how many imagined states are produced per goal and whether they are surfaced in diagnostics.

*How to capture*: Export a subset of `states[]` from API responses, run integrity checks via a notebook or `scripts/metrics/check_cwmstate_integrity.py`, and attach output to verification logs.

## 3. Diagnostics & Persona Fidelity

- **Log correlation accuracy**: Confirm diagnostics pane logs reference the correct `state_id`/plan step and match backend log entries.
- **Persona diary freshness**: Measure time between CWM-E reflection creation and appearance in the UI; target under 1 minute.
- **Telemetry completeness**: Verify that required metrics (CPU, API latency, Milvus health) populate the telemetry tab without gaps during a demo.

*How to capture*: Use the observability exporter to emit sample events, then snapshot the UI and backend log tail; track any mismatches.

## 4. Visual Interaction Quality

- **Graph responsiveness**: Count FPS or interaction latency of the HCG visualization under typical plan size (e.g., 200 nodes). Target smooth panning/zooming (< 100 ms lag).
- **Timeline accuracy**: Validate that the plan timeline reflects actual plan step timestamps from Sophia responses.
- **Chat/LLM alignment**: If the chat panel uses an LLM, measure agreement between suggested actions and actual plan results (qualitative check).

## 5. Gullibility Factor (Grounded vs Reported Conflict)

Measure how often Sophia prioritizes user-reported statements over the grounded latent state:

- **Conflict detection rate**: Count cases where user claims contradict HCG facts/JEPA predictions. Track how many conflicts are caught before plans execute.
- **Override thresholds**: Record confidence deltas when Sophia decides to trust the user despite contradictory evidence (e.g., CWM-A says entity is at location X but user says Y). Require explicit `assumptions` entries in `CWMState` to justify overrides.
- **Recovery latency**: How long (or how many steps) it takes for the agent to course-correct when a trusted statement proves false.
- **Trust decay curve**: Maintain a per-entity/user trust score based on recent accuracy; regression tests should ensure trust only increases when predictions and reports align.

Visualization idea: a “gullibility gauge” in diagnostics showing current trust levels and recent conflict events. Evidence should include Neo4j exports of conflicting `CWMState` nodes, logs of conversational prompts, and planner decisions.

## 6. Scenario Coverage “Have We Arrived?” Index

Track whether LOGOS can execute representative scenarios end-to-end without regressions:

- **Embodied loop**: Talos-driven manipulation (or Gazebo twin) with JEPA predictions recorded as `CWMState`.
- **Talos-free perception**: Apollo web uploads media, CWM-G imagines futures, Sophia updates the HCG without actuation.
- **CLI-only ops run**: Operator walks through goal→plan→diagnostics entirely from the CLI.
- **Browser+LLM co-processor**: Apollo chat proposes actions, Sophia validates them, diagnostics stay consistent.
- **Swappable hardware**: Same goal executed against two Talos adapters (simulated vs physical) with identical API outputs.

Each scenario contributes a binary score (1 = demonstrated with attached logs/screenshots, 0 = missing). Sum to create the “Have we gotten there yet?” readiness metric; require ≥4/5 before calling the overall milestone complete. Archive evidence in `logs/scenario_coverage/` with timestamps and short narratives (Neo4j export, JEPA dump, persona log).

## 7. Next Steps

- [ ] Define scripts or notebooks to capture each metric idea.
- [ ] Attach metric outputs to the relevant Phase 2 verification artifacts (`logs/p2-m*/metrics/`).
- [ ] Integrate critical metrics into CI (or at least a `make metrics` target) once tooling stabilizes.
- [ ] Revisit this list after the Apollo prototype sprint to add/remove metrics based on what proved most useful.
