# State Architecture Design

**Status:** Draft
**Date:** 2026-01-01

## The Problem

"State" is used ambiguously across LOGOS. Before implementing provenance (#15) or session boundaries (#101), we need to define what state actually means.

## Core Insight

**There is one graph: the HCG (Hybrid Causal Graph).**

The CWM (Causal World Model) is not a separate system—it's **content within the HCG**. CWM nodes represent Sophia's causal understanding of the world, stored as nodes in the HCG alongside everything else (type definitions, processes, etc.).

The `CWMState` envelope is a **transport/event format** for notifying about HCG changes. Despite the name, it's not limited to CWM nodes—it's a general HCG change notification. Provenance lives on the HCG nodes themselves, not the envelope.

---

## Two Systems, One Graph

| System | What It Stores | Authority |
|--------|----------------|-----------|
| **Talos** | World State (physical reality) | Ground truth from sensors |
| **HCG** | Everything Sophia knows | CWM nodes, processes, types, plans |

Talos owns physical reality. The HCG owns Sophia's knowledge, beliefs, and reasoning.

---

## CWM: Content Within HCG

CWM = Causal World Model. It's Sophia's model of cause and effect, stored as nodes in the HCG.

### CWM Node Categories

| Category | What It Represents | Examples |
|----------|-------------------|----------|
| **CWM-G** (Grounded) | Physical beliefs, predictions | "Block is in bin", "Arm will be at X" |
| **CWM-A** (Abstract) | Conceptual knowledge, goals, plans | "Goal: sort blocks", "User prefers careful handling" |
| **CWM-E** (Affective) | Emotional/reflective states | "Confident about plan", "Uncertain about intent" |

These are **perspectives on the same graph**, not silos:
- Cross-category edges allowed (G observation → A goal it supports)
- Single HCG with node types: `cwm_grounded`, `cwm_abstract`, `cwm_affective`

---

## Memory Tiers

All tiers store CWM data—the difference is persistence status:

| Tier | Storage | Lifetime | Characteristic |
|------|---------|----------|----------------|
| **Ephemeral** | In-memory | Session | Not yet in HCG |
| **Mid-term** | HCG + `expires_at` | Days-weeks | Persisted, TTL can change |
| **Long-term** | HCG (no expiry) | Indefinite | Canonical knowledge |

**Key insight:** No Redis tier. Mid-term vs long-term is just presence/absence of `expires_at` field.

### Promotion: Ephemeral → HCG

Triggered by **salience score** (method TBD). Factors:
- Relevance to existing HCG nodes (structural fit)
- Novelty (not already known)
- Non-triviality (worth remembering)
- Curiosity alignment (fills a gap we're interested in)
- User reaction strength (emotional/social salience)
- Explicit user signal ("remember this")

Higher score → persisted with longer initial TTL.

### TTL Modification

- **Extended by:** Reuse, user confirmation, continued relevance
- **Shortened by:** Contradiction, obsolescence, new information
- **Removed (promotion):** Proven canonical

---

## What is "Current State"?

**Current state = ephemeral CWM (in-memory) + relevant HCG nodes based on current focus.**

It's a **query**, not a copy. Sophia asks "what do I know that's relevant to this goal?" and gets back:
1. Ephemeral data from in-memory buffers
2. CWM nodes from HCG matching the attention pattern

---

## CWMState: Transport Envelope

`CWMState` is an **event format** for notifying about HCG changes. (The name is historical—it's really an HCG change notification, not limited to CWM nodes.)

It wraps:
- Which nodes changed
- What type of change (created, updated, deleted)
- Metadata (timestamp, source, confidence)

**Provenance lives on the HCG nodes**, not the envelope. CWMState just references node IDs—query the HCG for full provenance.

Use cases:
- Apollo subscribes to CWMState events to update display
- Logging/observability of cognitive activity
- Promotion notifications ("this ephemeral data was persisted")

---

## State Flow

```
Physical World
      │
      ▼ (sensors)
┌─────────────┐
│    Talos    │  ← Ground truth (separate system)
│ World State │
└─────────────┘
      │
      ▼ (observation)
┌─────────────────────────────────────────────────────┐
│                        HCG                          │
│                  (Sophia's Graph)                   │
│                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │  CWM-G   │◄─►│  CWM-A   │◄─►│  CWM-E   │        │
│  │ Grounded │   │ Abstract │   │Affective │        │
│  └──────────┘   └──────────┘   └──────────┘        │
│                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │ Process  │   │   Type   │   │   Plan   │        │
│  │  Nodes   │   │   Defs   │   │  Nodes   │        │
│  └──────────┘   └──────────┘   └──────────┘        │
│                                                     │
└─────────────────────────────────────────────────────┘
      │
      ▼ (events)
┌─────────────┐
│  CWMState   │  ← Transport envelope (not storage)
│  (events)   │     Name is historical; really HCG events
└─────────────┘
      │
      ▼
   Apollo (display)
```

---

## What Each Service Does

| Service | Role | Owns |
|---------|------|------|
| **Talos** | Physical reality | World state (sensors, actuators) |
| **Sophia** | Cognition | HCG (all CWM nodes, plans, etc.) |
| **Apollo** | Display | Nothing (consumes CWMState events) |
| **Hermes** | Language | Nothing (stateless) |

---

## Resolved Questions

### Q1: What is "state" canonically?

**Resolved:** Two locations:
1. **Talos** - World state (physical reality)
2. **HCG** - Sophia's knowledge (CWM nodes + everything else)

### Q2: What is "current state" for Sophia?

**Resolved:** Ephemeral in-memory data + relevant HCG nodes for current focus. It's a query, not a copy.

### Q3: What about the `/state` endpoint?

**Resolved:** Should create CWM-G nodes (grounded beliefs), not CWM-A. Physical observations are grounded, not abstract.

### Q4: What is CWMState envelope for?

**Resolved:** Transport/event format for HCG change notifications. Provenance lives on the HCG nodes, not the envelope. Apollo subscribes to these events for display updates.

### Q5: Where does provenance go?

**Resolved:** On HCG nodes. CWMState is just transport—it references node IDs, doesn't duplicate provenance.

---

## Open Questions

### Q1: How does Talos state become CWM-G nodes?

Options:
- A) Sophia polls Talos, creates CWM-G nodes from observations
- B) Talos pushes observations, Sophia creates CWM-G nodes
- C) Sophia queries Talos on-demand before planning
- D) Sophia references Talos nodes directly (no CWM-G copy)

Current: D (shared Neo4j), but Sophia doesn't actively read it.

**Status:** Defer until hardware integration

---

## Planning State Contract

Planning must work across any domain (robot, chess, travel, digital tasks).

### Domain-Specific Content, Common Contract

```python
class PlanState(Protocol):
    """All domain states must satisfy this for planning."""

    def satisfies(self, condition: Condition) -> bool:
        """Check if precondition/goal is met."""

    def apply(self, effect: Effect) -> "PlanState":
        """Return new state with effect applied."""

    def diff(self, other: "PlanState") -> StateDiff:
        """What changed between states."""

class Action(Protocol):
    """All actions must have preconditions and effects."""

    precondition: Condition  # pattern that must match current state
    effect: Effect           # mutation to apply to state
```

### In Graph Terms

- **State** = subgraph snapshot
- **Condition** = Cypher pattern that must match
- **Effect** = Cypher mutation (CREATE/SET/DELETE)
- **satisfies()** = pattern match exists
- **apply()** = execute mutation, return new subgraph

Pluggable algorithms (A*, MCTS, HTN, LLM) all use the same contracts.

---

## Summary

### Resolved
- **One graph:** HCG is the source of truth for Sophia's knowledge
- **CWM is content:** CWM-A/G/E are node categories within HCG, not separate systems
- **CWMState is transport:** Event envelope for HCG notifications (name historical), provenance on HCG nodes
- **Memory tiers:** Ephemeral (in-memory) → Mid-term (HCG + expires_at) → Long-term (HCG)
- **No Redis:** Mid-term vs long-term is just `expires_at` field
- **Current state:** Query over ephemeral + relevant HCG nodes
- **Planning contracts:** Domain-specific content, common interface

### Deferred
- Talos → CWM-G integration (until hardware work begins)

### Next Steps

1. Scope #15 to **Plan provenance only** (clear, useful now)
2. Update `/state` endpoint to create CWM-G nodes
3. Define planning contracts formally in code
4. Revisit Talos integration when hardware work begins
