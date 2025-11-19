# ADR-0004: HTN-based Planning Approach

**Status:** Accepted

**Date:** 2024-01 (Phase 1 Foundation)

**Decision Makers:** Project LOGOS Core Team

**Related Issues:** Phase 1 Planning, M3 Milestone

## Context and Problem Statement

Sophia's Planner component must decompose high-level goals into executable action sequences. The planner operates on the HCG to:
- Take abstract goals (e.g., "prepare coffee", "tidy workspace")
- Generate hierarchical task networks
- Ground abstract actions into concrete Talos capabilities
- Maintain causal coherence with the HCG world model
- Support replanning when conditions change

The planning approach must balance:
- Expressiveness (handle complex, real-world tasks)
- Efficiency (plan in reasonable time for interactive use)
- Explainability (humans can understand and verify plans)
- Integration with HCG (leverage graph structure for domain knowledge)

Which planning paradigm should we use as the foundation for Sophia's Planner?

## Decision Drivers

* **Hierarchical decomposition**: Goals naturally decompose into subgoals (make coffee → grind beans + heat water + brew)
* **Domain knowledge integration**: Leverage HCG for action preconditions and effects
* **Causal coherence**: Plans must respect causal relationships in the world model
* **Explainability**: Generated plans should be human-readable and verifiable
* **Replanning support**: Handle dynamic environments where initial plans may fail
* **Implementation complexity**: Must be achievable within Phase 1 scope
* **Research foundation**: Build on established planning algorithms rather than inventing new approaches

## Considered Options

* **Option 1**: HTN (Hierarchical Task Network) planning
* **Option 2**: STRIPS-style classical planning (PDDL)
* **Option 3**: Monte Carlo Tree Search (MCTS) planning
* **Option 4**: Large Language Model (LLM) prompted planning

## Decision Outcome

Chosen option: "HTN (Hierarchical Task Network) planning", because it naturally aligns with how humans decompose goals into subgoals and provides explicit hierarchical structure that maps cleanly to HCG's Process nodes and causal relationships. HTN allows domain knowledge (from the HCG) to guide decomposition while maintaining explainability.

### Positive Consequences

* Hierarchical structure matches human intuition about task decomposition
* Methods explicitly encode domain knowledge (how to achieve goals)
* Plans are naturally explainable (show goal → subgoal decomposition tree)
* Integrates cleanly with HCG Process and State nodes
* Can leverage graph traversal to find applicable methods
* Supports partial plans and incremental refinement
* Well-established algorithms (SHOP2, PANDA) provide implementation guidance
* Enables "why" explanations (show decomposition choices)

### Negative Consequences

* Requires domain-specific method definitions (cannot plan over arbitrary domains)
* More implementation complexity than simple STRIPS planning
* Method libraries must be authored and maintained
* Finding optimal plans is computationally expensive
* May produce brittle plans that fail with slight environmental changes

## Pros and Cons of the Options

### HTN (Hierarchical Task Network) planning

* Good, because hierarchical decomposition mirrors human problem-solving
* Good, because explicit methods encode domain knowledge from HCG
* Good, because plans include hierarchical structure (not just flat action sequences)
* Good, because well-studied with established algorithms (SHOP2, PANDA)
* Good, because supports varying levels of abstraction in plans
* Good, because can explain plans by showing goal decomposition
* Bad, because requires authoring method definitions for each domain
* Bad, because less flexible than domain-independent approaches
* Bad, because finding optimal decompositions is computationally hard

### STRIPS-style classical planning (PDDL)

* Good, because domain-independent (same planner works for any domain)
* Good, because mature tooling and benchmarks (Fast Downward, FF planner)
* Good, because well-defined semantics and correctness guarantees
* Good, because can find optimal plans with admissible heuristics
* Bad, because flat action sequences lack hierarchical structure
* Bad, because harder to incorporate domain-specific knowledge
* Bad, because plans are less human-readable (no abstraction levels)
* Bad, because PDDL syntax is verbose and unfamiliar to most developers
* Bad, because doesn't leverage HCG's hierarchical structure

### Monte Carlo Tree Search (MCTS) planning

* Good, because handles uncertainty and stochastic domains naturally
* Good, because proven success in game playing and sequential decision problems
* Good, because can balance exploration vs. exploitation
* Bad, because computationally expensive (requires many rollouts)
* Bad, because less explainable (statistical sampling, not logical reasoning)
* Bad, because requires accurate forward models (simulation)
* Bad, because convergence time unpredictable
* Bad, because overkill for deterministic domains (Phase 1 focus)

### Large Language Model (LLM) prompted planning

* Good, because leverages pretrained world knowledge
* Good, because can handle novel situations without explicit methods
* Good, because natural language interface for defining goals
* Bad, because non-deterministic (same goal may yield different plans)
* Bad, because no formal correctness guarantees
* Bad, because hard to verify causal coherence with HCG
* Bad, because "black box" reasoning (cannot explain decomposition choices)
* Bad, because expensive inference costs (API calls or local GPU)
* Bad, because contradicts LOGOS philosophy of non-linguistic cognition

## Implementation Strategy

### Phase 1 HTN Planner Architecture

```
HCG (Neo4j)
    ↓
Method Library (Cypher + Python)
    ↓
HTN Planner (recursive decomposition)
    ↓
Abstract Plan (hierarchy of tasks)
    ↓
Executor (grounds to Talos capabilities)
```

### Example HTN Method (Pseudocode)

```python
# Method: Prepare Coffee
# Goal: State(coffee=ready)
# Preconditions: State(beans=available), State(water=available)
# Decomposition:
#   1. Grind beans → State(grounds=ready)
#   2. Heat water → State(water=hot)
#   3. Brew coffee → State(coffee=ready)
#   Ordering: (1 || 2) → 3  # Steps 1,2 parallel, then 3
```

### HCG Integration

HTN methods are stored as Process nodes in the HCG:
- Process.type = "method"
- Process.name = method identifier
- Process.preconditions → State nodes (via REQUIRES relationship)
- Process.effects → State nodes (via CAUSES relationship)
- Process.decomposition → Child Process nodes (ordered)

## Future Extensions

Phase 2+ may incorporate:
- **Hybrid HTN + LLM**: LLM suggests methods, HTN validates causal coherence
- **Learning from experience**: Adjust method preferences based on execution outcomes
- **Probabilistic HTN**: Handle uncertainty in action outcomes
- **Reactive replanning**: Detect plan failures and trigger decomposition repairs

## Links

* Related to [ADR-0001](0001-use-neo4j-for-graph-database.md) - HCG stores methods and plans
* Stub implementation in `planner_stub/` directory
* Planning tests in M3 milestone workflow
* Executor integration in M4 end-to-end demo

## References

* [SHOP2 HTN Planner](https://www.cs.umd.edu/projects/shop/)
* [PANDA Planning System](https://www.uni-ulm.de/in/ki/panda)
* [Hierarchical Task Network Planning](https://en.wikipedia.org/wiki/Hierarchical_task_network) - Overview
* [HTN Planning: Complexity and Expressivity](https://www.aaai.org/Papers/AAAI/1994/AAAI94-203.pdf)
* Project LOGOS Specification: Section 3.3 (Sophia Planner component)
* Project LOGOS Specification: Section 4.1 (Process nodes in HCG)
