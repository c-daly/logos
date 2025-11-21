# Project LOGOS: A Non-Linguistic Causal Architecture

*Preliminary research paper draft — work in progress.*

---

## Abstract
Large language models provide competent natural language interfaces yet lack grounded state, causal guarantees, and explainability when asked to operate embodied agents. Project LOGOS addresses these gaps through the Hybrid Cognitive Graph (HCG), a multi-model causal world representation that fuses symbolic graph reasoning (CWM-A), grounded imagination (CWM-G), and reflective persona state (CWM-E). Sophia, Hermes, Talos, and Apollo expose this structure through APIs, browser/CLI tooling, and JEPA-powered simulation, enabling Talos-optional deployments that remain causally coherent. This paper introduces the architecture, highlights the ontology + SHACL verification base alongside the CLI/Sophia/Hermes services, details the perception pipeline and dual Apollo surfaces, and outlines the evaluation plan that measures latency, CWM coverage, persona fidelity, and visualization quality. Early integration results indicate that LOGOS can reject invalid plans, surface imagined states with provenance, and provide deterministic audit trails when acting as a causal co-processor for LLM-powered experiences.

---

## 1 Introduction

### 1.1 Motivation
Autonomous agents increasingly delegate planning and execution to LLM-driven controllers. While linguistically expressive, these controllers often operate without explicit state, forcing downstream systems to infer causality from text. LOGOS departs from that pattern by mandating that every perception, plan, and reflection is grounded in the HCG and validated before affecting the world. The resulting pipeline lets operators reason about causal chains directly, swap hardware without rewriting cognition, and keep language as a transport layer handled by Hermes and Apollo.

All world-model activity—perceptual updates, planner deliberations, even CWM-E reflections—remains inside a linguistic-free logical symbol space. Concepts, processes, and emotions are encoded as graph nodes, embeddings, and SHACL-validated predicates rather than free-form prose. Language is only rendered at the edges (Apollo/Hermes) after Sophia has already produced symbol-level conclusions, preserving deterministic reasoning even when LLMs participate as optional narrators.

This emphasis on physical understanding is not limited to embodied robots. Even a purely conversational surface benefits from a grounded model that can reason about forces, affordances, and temporal ordering: a chatbot diagnosing a manufacturing issue or guiding a user through assembly needs the same causal predictions as a drone planner. LOGOS therefore treats perception and JEPA-style imagination as universal cognitive primitives rather than optional robotics features.

### 1.2 Contributions
1. **Hybrid Cognitive Graph (HCG) with deterministic guardrails** that blend Neo4j structures, Milvus embeddings, and SHACL validation to keep agent knowledge coherent.
2. **Unified causal world model** (CWM-A/G/E) that exposes observed, imagined, and reflective states through a single `CWMState` envelope consumed by services and diagnostics.
3. **Talos-optional deployment architecture** that treats Sophia + LOGOS infra as the mandatory substrate while Hermes, Talos, and Apollo remain swappable adapters.
4. **Evaluation framework** covering API latency, imagination coverage, diagnostics fidelity, and visualization responsiveness to quantify the benefits of causal co-processing.

The implementation roadmap still references operational milestones, but conceptually LOGOS behaves as one cooperative mind built from relatively simple centers (HCG + CWM layers + interaction adapters). Phases only describe delivery order; the architecture itself remains holistic and language-free regardless of embodiment.

---

## 2 Background and Related Work
LLM agent frameworks (e.g., ReAct, AutoGPT) showcase plan-language loops but lack explicit causal graphs, leading to opaque failures. Cognitive architectures such as SOAR or ACT-R maintain structured knowledge but rarely integrate modern embeddings or multimodal simulation. Robotics stacks fuse perception and control yet often hard-code embodiment assumptions. LOGOS positions itself at the intersection: symbolic rigor with constraint validation, vector-backed recall, JEPA imagination, and multimodal UX bridges. We leave formal literature citations for the next revision; this draft focuses on documenting the system design and evaluation hooks already implemented in the repository.

---

## 3 System Overview

### 3.1 Component Layout
LOGOS consists of five collaborating systems (see `docs/spec/LOGOS_SPEC_FLEXIBLE.md`):
1. **Sophia** — non-linguistic cognitive core orchestrating goals, planners, and executors that operate on the HCG.
2. **Hermes** — stateless language services (STT, TTS, NLP preprocessing, embedding) that convert natural language into graph-compatible artifacts without mutating the HCG.
3. **Talos** — capability bus/hardware abstraction; optional in deployments yet supported through shared contracts.
4. **Apollo** — interaction surfaces (CLI + browser) that expose diagnostics, chat, plan viewers, and read-only views of the persona diary emitted by CWM-E.
5. **HCG infrastructure** — Neo4j, Milvus, SHACL validators, and tooling hosted in the LOGOS meta repository.

### 3.2 Hybrid Cognitive Graph and CWM States
The HCG stores entities, concepts, states, and processes with explicit causal edges. Every mutation is validated via SHACL (pySHACL locally; optional Neo4j+N10s job) before persisting. CWM outputs materialize as `CWMState` nodes with consistent IDs (`cwm_<model>_<uuid>`), timestamps, confidences, and links to related plans, entities, media samples, or Talos runs. Payloads encode logical relations, embeddings, or emotion scalars rather than natural-language sentences, ensuring that observed states (CWM-A), imagined rollouts (CWM-G), and persona reflections (CWM-E) remain comparable, machine-auditable artifacts.

### 3.3 Data Flow and APIs
User inputs travel through Apollo into Sophia, which queries and updates the HCG via Neo4j drivers and Milvus embeddings. Hermes provides speech/text bridges and embeddings, while Talos (when present) receives validated plans. `/plan`, `/state`, and `/simulate` are the canonical Sophia endpoints; `/embed_text`, `/simple_nlp`, `/stt`, and `/tts` are the Hermes endpoints. Diagnostics subscribers and CWM-E reflection jobs observe the event stream, write persona diary entries back into the HCG, and make them available to any client (Apollo is one implementation).

---

## 4 Foundational Architecture

### 4.1 Infrastructure & Ontology
The initial LOGOS build delivers the Compose-based HCG cluster (Neo4j + Milvus), ontology files (`ontology/core_ontology.cypher`, `ontology/shacl_shapes.ttl`), and helper scripts for loading constraints and initializing vector collections. The foundational specification in this repository explicitly calls out Docker prerequisites, plugin requirements (APOC, GDS, neosemantics), and health scripts. These artifacts establish the deterministic base required for all higher-level capabilities.

### 4.2 Testing, Verification, and Prototype Flow
The team implemented opt-in heavy tests, SHACL jobs, and CLI scripts (e.g., `scripts/e2e_prototype.sh`) that run a goal→plan→execute loop against the HCG. Verification evidence resides in the archival checklist captured alongside the spec but is referenced in the flexible file to keep provenance intact. This work yields a reproducible CLI demo and CI workflows that gate ontology or planner changes.

---

## 5 Perception, Imagination, and Apollo UX

### 5.1 Sophia and Hermes Services
The current service layer exposes Sophia through FastAPI endpoints (`/plan`, `/state`, `/simulate`) wired to the Neo4j driver and SHACL validation helpers. Planner/executor modules pull metadata from CWM-G/E to ensure persona-consistent plans. Hermes acts as a companion FastAPI service delivering embeddings (persisted to Milvus), simple NLP, and STT/TTS, complete with health checks for Milvus collections and worker queues.

### 5.2 Perception Pipeline and JEPA Imagination
Talos-free demonstrations rely on Apollo uploading media samples that feed a JEPA runner (CWM-G). The runner emits embeddings, frames, and rollouts stored in Milvus/Neo4j, enabling `/simulate(capability, context)` to return imagined outcomes with confidence scores and horizon metadata. Imagined vs observed states share the `CWMState` contract, ensuring diagnostics can compare them directly and highlight divergence. Even when no actuator exists, these grounded predictions let conversational clients answer questions about feasibility, safety, or future outcomes with more authority than purely textual reasoning.

### 5.3 Apollo Dual Surfaces, Diagnostics, and Persona Diary
The CLI continues as a thin client over the shared SDK, while the browser (Vite + React + TypeScript) serves as the main storytelling surface. It hosts three pillars: chat/LLM panel with persona awareness, HCG/plan visualizations, and diagnostics dashboards streaming logs, telemetry, and persona reflections. CWM-E outputs are themselves symbolic structures—emotion vectors, confidence deltas, tagged processes—so any user-facing surface (Apollo or otherwise) retrieves structured entries from the HCG and may optionally render them as language without altering the underlying reasoning substrate.

---

## 6 Evaluation Plan

### 6.1 Metrics
Building on the repository’s metrics notes, the evaluation campaign will track:
- **API latency & availability** for `/plan`, `/state`, `/simulate`, and Hermes endpoints (target <2s for `/state`, <5s for planning/simulation).
- **CWMState coverage & integrity**, including counts per model type, link validation between UI entries and Neo4j nodes, and imagined vs observed ratios.
- **Diagnostics & persona fidelity**, measuring log correlation accuracy, diary freshness (<1 minute), and telemetry completeness.
- **Visual interaction quality** such as HCG graph responsiveness (<100 ms lag), timeline accuracy, and chat-to-plan alignment checks.
- **Gullibility factor**, quantifying how often Sophia trusts user reports over grounded predictions, how quickly conflicts are detected, and how trust scores decay when reports prove false.

Scripts under `scripts/metrics/` (planned) and pytest benchmarks will generate JSON logs stored in `logs/p2-m*/metrics/` for reproducibility. These metrics double as acceptance criteria for the milestone checklist maintained in the governance docs.

### 6.2 Evidence and Datasets
- **Services**: OpenAPI captures, curl transcripts, and CI logs showing successful runs of Sophia/Hermes workflows.
- **Perception**: Sample media inputs, JEPA rollout clips, embedding dumps demonstrating Milvus linkages.
- **Apollo**: Browser walkthrough video and CLI session logs from the shared SDK, proving parity between surfaces.
- **Diagnostics**: Observability dashboards, persona diary excerpts, and demo capture artifacts catalogued in `logs/`.

### 6.3 Baselines and Comparisons
The preliminary study will compare LOGOS against:
1. **LLM-only controller** — textual planning without HCG validation to quantify improvements in plan validity and latency impact.
2. **Symbolic-only planner** — SHACL-validated but embedding-free baseline to measure retrieval benefits and JEPA-assisted perception coverage.
3. **Human operator** — optional benchmark for Apollo UX responsiveness and interpretability.
These baselines frame ablations such as disabling SHACL checks, removing CWM-G imagination, or bypassing persona reflections.

### 6.4 Data & Benchmark Strategy
The most persuasive evidence will require curated datasets rather than ad-hoc demos. Key actions:
- Assemble reusable scenario bundles (media samples, Talos traces, CLI transcripts) that populate the HCG/Milvus stores and can be replayed deterministically.
- Capture ground-truth annotations for perception sequences (scene labels, future-frame references) so JEPA rollouts and symbolic inferences can be scored numerically.
- Log every `/plan`, `/state`, `/simulate` interaction along with SHACL reports and persona deltas into versioned artifacts under `logs/benchmarks/`.
- Publish a summary table correlating each scenario to the metrics outlined above (latency, coverage, diagnostics fidelity, scenario coverage index) so reviewers can understand how LOGOS performs across deployments.

Without these datasets and evaluation harnesses the architecture remains speculative; capturing them early is a prerequisite for any credible submission.

---

## 7 Discussion

### 7.1 Benefits
- **Causal integrity** via SHACL + graph-native reasoning, reducing hallucinated actions.
- **Embodiment flexibility** through Talos-optional contracts and adapter-first design.
- **Explainability** thanks to diagnostics, persona diaries, and observed/imagined provenance links.

### 7.2 Limitations
- Perception currently relies on JEPA rollouts without hardware feedback; physical Talos integrations remain future work.
- Evaluation metrics focus on internal latency/coverage; user studies and long-horizon tasks are pending.
- References and comparisons need formal citations and quantitative data once experiments complete.

---

## 8 Future Work
Future expansions aim to add episodic memory, probabilistic validation, and embodiment demos, then progress toward continuous learning with safety gates and multi-agent coordination. Immediate priorities include capturing reproducible metrics, integrating Talos hardware simulators, and extending Apollo’s SDK for partner ecosystems.

---

## 9 Conclusion
LOGOS reframes autonomous assistants as causal graph reasoners with language relegated to the interface. The combination of HCG, unified CWM state, JEPA-powered imagination, and dual Apollo surfaces offers a reusable foundation for explainable, Talos-optional deployments. This preliminary paper captures the architecture and evaluation scaffolding already implemented, setting the stage for empirical validation and publication-ready figures in upcoming iterations.

---

## 10 What It Takes for LOGOS to Matter

To move beyond an elegant architecture and genuinely influence the field, LOGOS must prove four things:

1. **Data-backed grounding** — Provide publicly inspectable datasets, annotated perception sequences, and scenario logs so other researchers can replay findings. Without reproducible evidence the universal latent state remains hypothetical.
2. **Quantified reliability** — Demonstrate measurable gains in plan validity, gullibility resistance, and diagnostics fidelity over LLM-only or symbolic-only baselines. The metrics in Section 6 need to show statistically significant improvements, not just qualitative anecdotes.
3. **Cross-surface impact** — Ship convincing demos across at least three deployment styles (embodied, Talos-free perception, pure conversational) to prove that the cooperating centers philosophy generalizes. Success in only one niche would relegate LOGOS to a specialized stack.
4. **Developer adoption path** — Document SDKs, APIs, and governance workflows that let external teams extend the system without breaking causal guarantees. Matter comes from other groups building on the HCG/CWM contracts, not just the original authors.

If these criteria are met, LOGOS can transition from a research curiosity to a blueprint for grounded, explainable agents. Failing to deliver on any of them would turn the project into just another architectural proposal with limited practical influence.

---

## References
*(To be populated with formal citations during the full drafting stage.)*
