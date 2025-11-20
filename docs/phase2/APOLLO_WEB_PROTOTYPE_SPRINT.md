# Apollo Web Prototype Sprint — Ticket Map

Goal: Deliver a browser UI that (1) lets operators interact with Sophia/Hermes, and (2) exposes diagnostics (graph visualization, plan timelines, persona diary, telemetry) so we can inspect the agent’s internal state in real time. Completing the tickets below gives us a functional slice that exercises every backend dependency the UI relies on.

## 1. Backend/API Prerequisites

| Requirement | Ticket(s) | Notes |
|-------------|-----------|-------|
| Stable Sophia APIs (`/plan`, `/state`, `/simulate`) returning the unified `CWMState` envelope | #218 (closed), #157 (planner upgrades) | If #157 shifts payloads, ensure OpenAPI + SDK regen is part of its acceptance criteria. |
| Stable Hermes APIs (`/embed_text`, `/simple_nlp`, `/stt`, `/tts`) with Milvus persistence | #219 (open), #242 (Milvus smoke & migrations) | UI depends on embedding health checks for diagnostics tab. |
| Shared client SDK for CLI + browser | #236 (open) | Blocks all frontend data fetching; must include generated TypeScript hooks for `/state` pagination and `/simulate`. |

## 2. Apollo Browser Features

| Requirement | Ticket(s) | Notes |
|-------------|-----------|-------|
| Diagnostics & graph visualization panels (plan timeline, HCG view, log stream) | #237 (open) | Should explicitly include Cytoscape integration, timelines, and log stream wiring. |
| Persona diary pane + explainability overlays | #238 (open) | Requires CWM-E data feed and UI components for narrative rendering. |
| Observability dashboards + OTel/structured log ingestion | #239 (open) | Needed so diagnostics tab has live metrics and log filtering. Consider splitting into backend exporter + UI wiring subtasks if scope grows. |

## 3. Perception / Simulation Hooks

| Requirement | Ticket(s) | Notes |
|-------------|-----------|-------|
| Media ingestion service with IDs Apollo can reference | #240 (open) | Must emit IDs used in `/simulate` requests and diagnostics metadata. |
| JEPA runner + `/simulate` schema | #241 (open) | Supplies imagined CWM-G states for the diagnostics view and future Talos integrations. |
| Milvus embedding smoke tests + migration scripts | #242 (open) | Ensures perception data powering the UI is queryable and healthy. |

## 4. Missing Tickets To Create

Even with the issues above, we still need a few focused tasks to guarantee the browser experience:

1. **Apollo data mocking & fixture generation** — ability to run the UI against canned `CWMState` streams for development. (**#243** – Apollo mock data fixtures for CWMState replay).
2. **Diagnostics log stream API** — dedicated endpoint or WebSocket for structured log/OTel events consumed by the browser. (**#244** – Observability: structured log stream for Apollo diagnostics).
3. **End-to-end demo capture for browser** — script + instructions to record the UI interaction (ties into VERIFY). (**#245** – Demo capture script for Apollo browser walkthrough).
4. **Persona diary storage schema finalization** — backend ticket to persist `PersonaEntry` + `EmotionState` nodes using the unified contract. (**#246** – CWM-E persona diary storage & API exposure).

Tag the new tickets with `phase:2`, `surface:browser`, and `sprint:apollo-prototype` (once the label exists) so we can track this sprint independently from the broader Phase 2 backlog.

## 5. Definition of Done for the Sprint

- Browser renders chat, graph visualization, diagnostics tabs, and persona diary backed by real Sophia/Hermes data.
- `/state`, `/plan`, `/simulate` responses all appear in the UI via the shared SDK.
- Diagnostics pane shows log stream + metrics sourced from the observability pipeline.
- Persona diary reflects CWM-E outputs with traceable `state_id` links.
- Demo capture artifact recorded and VERIFY checklist items for UI updated.
