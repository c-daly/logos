# Research & Tooling

Exploratory work and developer tooling that supports LOGOS development but isn't part of the core architecture.

## Active Research

### TinyMind
**Location:** `PoCs/tiny_mind/` | **Status:** Active

A baby intelligence that learns through conversation. Builds knowledge graphs via chat, PDF reading, web research.

**Already taken into LOGOS:**
- **Reified edges** — TinyMind's core insight ("edges carry more information than nodes") directly led to the reified edge model in logos #490. TinyMind edges carry confidence, temporal validity, strength, magnitude, source provenance, and access tracking. LOGOS adopted this pattern: relationships are nodes with rich metadata, not just labeled arrows.
- **Source provenance** — TinyMind tracks *how* knowledge was acquired (direct observation, user statement, LLM extraction, sensor reading). LOGOS's Provenance nodes serve the same role.
- **Confidence-based dedup** — TinyMind's graph deduplicates by confidence scoring. Sophia's ProposalProcessor uses Milvus L2 similarity thresholds for the same purpose.

**Should consider taking:**
- **Curiosity drive** — TinyMind has a structured curiosity system: it identifies knowledge gaps (missing definitions), potential connections between disconnected clusters, low-confidence uncertainty, shallow but important concepts, and unexplored related topics. Sophia has no intrinsic motivation — it only processes what's sent to it. A curiosity module would let Sophia actively seek knowledge rather than passively receive it.
- **Structural anomaly detection** — TinyMind's `StructuralAnalyzer` identifies suspicious claims, cluster outliers, and type pattern violations. This is exactly the kind of self-auditing the HCG needs as it grows.
- **Knowledge revision** — TinyMind has a full revision system: deduplication, corroboration (strengthening repeated observations), contradiction resolution, and pruning. LOGOS has none of this — once a node is in the HCG, it stays forever at its original confidence.
- **LLM-based extraction with schemas** — TinyMind uses Pydantic schemas to enforce structured LLM output during knowledge extraction. Hermes's current spaCy-based NER is simpler but less flexible.

---

### Axiom
**Location:** `projects/agents/axiom/` | **Status:** Active (77 tests passing)

Research testbed for bootstrapped, goal-free learning. Discovers knowledge through intrinsic motivation without predetermined objectives.

**Already taken into LOGOS:**
- **Three-tier memory concept** — Axiom's ephemeral → probation → permanent memory tiers directly inform the LOGOS memory spec (#415), which proposes ephemeral → short-term → long-term with promotion/demotion. The confidence tracking with history and usage counts mirrors Axiom's `MemoryEntry` pattern.

**Should consider taking:**
- **Confidence dynamics with promotion/demotion** — Axiom entries have confidence histories, usage tracking, and can be promoted or demoted between tiers based on corroboration and utility. The LOGOS memory spec describes this but nothing is implemented yet.
- **Hypothesis formation and testing** — Axiom generates hypotheses from observations, tests them against new data, and marks them verified or refuted. LOGOS's planning system could use this: when new knowledge enters the HCG, check if it confirms or refutes existing beliefs.
- **Intrinsic motivation** — Axiom uses curiosity (surprise) and compression (simplicity) as reward signals. Combined with TinyMind's curiosity goals, this could give Sophia autonomous exploration behavior.
- **Composable expression space** — Axiom represents all knowledge as composable typed expressions. This is more rigorous than LOGOS's current flat property approach and could inform how process/plan nodes are structured.

---

### Genetic Hackathon
**Location:** [c-daly/genetic_hackathon](https://github.com/c-daly/genetic_hackathon) | **Status:** Experiment

Meta-computational discovery via genetic programming. Evolves mathematical and logical transformations, discovers simplification rules, composes tools from prior discoveries.

**Already taken into LOGOS:** Nothing directly yet.

**Should consider taking:**
- **Self-discovered transformation rules** — The system evolves simplification rules and saves them for reuse via a `ToolLibrary`. LOGOS's HCGPlanner could benefit from a similar pattern: plans that work get distilled into reusable plan templates, stored as graph patterns.
- **Behavioral signatures** — Functions are identified by their computed results, not their syntax. Two expressions with identical behavior are equivalent regardless of structure. This could inform how Sophia deduplicates process nodes — check behavioral equivalence, not just structural similarity.
- **Compositional discovery** — Later experiments can use tools discovered by earlier ones. This is exactly how LOGOS planning should work: solved subproblems become capabilities for higher-level planning.

---

### Cognitive Learning Architecture Proposals
**Location:** `PoCs/cognitive_learning_architecture_proposals.md` | **Status:** Complete (research)

Three architectural proposals for bootstrapping action learning without hardcoded schemas.

**Already taken into LOGOS:**
- **Proposal 2 (Agentic Graph Reasoning)** is closest to current LOGOS: LLM-driven graph expansion, curiosity-driven edge formation, confidence-based pruning. The cognitive loop (Hermes extracts → Sophia stores → context enriches) implements the core of this proposal.

**Should consider taking:**
- **Proposal 3 (Hybrid VLA + Curiosity-Driven Graph)** — Combines VLA model embeddings with curiosity-driven graph emergence. Once JEPA-to-CLIP alignment works, this becomes viable: grounded video embeddings feed into the same graph that language produces, with curiosity driving which connections to explore.
- **Confident pruning from TinyMind** — The proposals recommend extending TinyMind's pruning for LOGOS scale. As the HCG grows, low-confidence edges need automated cleanup.

---

### VL-JEPA Exploration
**Location:** `PoCs/vljepa_*.ipynb`, `PoCs/vl-jepa/` | **Status:** Active

Video-language JEPA experiments — clustering, feature decomposition, CLIP comparison.

**Already taken into LOGOS:**
- **CWM-G architecture** — The entire grounded working memory concept (CWM-G) exists because of this research. JEPA provides non-linguistic representations that language models fundamentally cannot.

**Should consider taking:**
- **Feature decomposition findings** — The notebooks show how JEPA features naturally cluster by scene type and action. These clusters could seed the type centroid system: instead of defining types manually, let JEPA feature clusters define grounded types.
- **CLIP complementarity** — The research shows JEPA and CLIP embeddings capture different information (JEPA: temporal/physical, CLIP: semantic/categorical). CWM-G should preserve both rather than projecting JEPA into CLIP space.

---

### JEPA-to-CLIP Alignment
**Location:** `logos/experiments/notebooks/` | **Status:** In progress

Aligning V-JEPA2 video embeddings to CLIP semantic space via LoRA fine-tuning. Target: 8GB VRAM.

---

### Universal Knowledge Graph
**Location:** `PoCs/universal_kg.ipynb` | **Status:** Experiment

Knowledge graph construction from grounded video understanding. Demonstrates building structured knowledge directly from video perception rather than text.

**Should consider taking:**
- **Video-to-graph pipeline** — Shows how to go from raw video → JEPA embeddings → clustered concepts → knowledge graph edges. This is the perception → cognition pipeline that LOGOS needs for non-linguistic understanding.

---

## See Also

- [TOOLING.md](TOOLING.md) — developer workflow tools, agent orchestration, session management

## Conventions

- Track new experiments with GitHub issues (label: `domain:research`)
- Results relevant to academic papers should be flagged (see `docs/SPEC.md` for architecture details; candidate papers are tracked in the project wiki)
- Experiment notebooks live in `logos/experiments/notebooks/` or `PoCs/`
- Design docs for completed experiments are archived in `logos/docs/archive/plans/`
