# LOGOS References & Inspiration

A curated list of papers, talks, and videos that inform the architecture, world models, and workflows described in the LOGOS project.

## Core Ideas & Cognitive Architectures
- **Hybrid Causal Graphs & Knowledge Graphs**
  - Pearl, Judea. *Causality* (2009) — foundational text on causal graphs.
  - Google DeepMind. “ReAct: Synergizing Reasoning and Acting in Language Models” (2022) — inspiration for action/plan loops.
  - IBM Project Debater & knowledge graph approaches.
- **Non-linguistic cognition & symbolic reasoning**
  - SOAR, ACT-R — classical cognitive architectures with graph memories.
  - “Language Is Not All You Need: Aligning Language Models with Multimodal Perception” — motivation for separating Sophia (non-linguistic) from Apollo/Hermes.

## World Models & JEPA
- **Joint Embedding Predictive Architectures (JEPA)**
  - LeCun, Yann. “A Path Towards Autonomy” (CVPR 2022 keynote) — outlines JEPA concepts.
  - “I-JEPA: Image-based Joint-Embedding Predictive Architecture” (LeCun et al.) — vision grounding.
  - “Object-Centric JEPA for Robotic Manipulation” — action-conditioned JEPAs for Talos execution.
- **Simulators/Imagination**
  - Ha & Schmidhuber. “World Models” (2018).
  - Google Dreamer / PlaNet papers for model-based RL.

## SHACL, Ontologies, and Validation
- W3C SHACL specification — deterministic validation used in Phase 1.
- Neo4j neosemantics (n10s) docs — live SHACL gating.
- “Shaping Graph Data with SHACL” (Neo4j blog posts, 2023).

## Perception & Multimodality
- OpenAI/Meta/GPT-4V release notes — inspiration for Apollo’s perception requests.
- Meta Segment Anything / perception stacks for visual grounding.
- LangChain tutorials on multimodal LLMs.

## Diagnostics, Persona, and Emotional Reasoning
- “Emotion in AI Planning” (various academic papers) — informs CWM-E.
- OpenTelemetry docs — instrumentation strategy.
- “Personas for Conversational Agents” (Microsoft research) — designing persona diaries.

## Talks & Videos
- **Yann LeCun’s CVPR 2022 keynote** — JEPA vision.
- **Meta’s JEPA demos** (YouTube) — practical glimpses of grounded predictions.
- **Neo4j NODES conference talks** on SHACL/n10s.
- **Google Cloud Vertex AI** webinars on knowledge graphs + vector search.

## Useful Links
- LOGOS flexible spec: `docs/architecture/LOGOS_SPEC_FLEXIBLE.md`
- Phase 1 spec: `docs/phase1/PHASE1_SPEC.md`
- Phase 2 spec: `docs/architecture/PHASE2_SPEC.md`
- GitHub Project LOGOS board: https://github.com/users/c-daly/projects/10

Additions welcome—PRs or issues referencing new papers/talks keep this list current.
