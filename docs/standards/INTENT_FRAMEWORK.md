# Intent Framework — Cascading Direction Artifacts

This document specifies the **Intent Framework**: a system for providing consistent, model-agnostic direction to AI agents across sessions, models, and repositories.

---

## Overview

The Intent Framework solves a fundamental problem with AI-assisted development:

> **Agents are stateless and inconsistent. Direction must be externalized.**

Instead of relying on:
- Chat history (ephemeral)
- Model memory (non-existent)
- Implicit understanding (unreliable)

We rely on:
- **Explicit, saved artifacts** that define what must not change
- **Cascading inheritance** that mirrors how config systems work
- **Structural enforcement** that catches drift before it causes damage

---

## Core Concepts

### Direction Artifacts (`INTENT.md`)

A direction artifact is a **saved file** that defines:
- What the work is about (goal)
- What success does not include (non-goals)
- What must not change (invariants)
- When to stop and ask (authority boundaries)
- When to reevaluate (triggers)

Direction artifacts:
- Live in the repository (not in prompts or chat)
- Are colocated with the code they constrain
- Cascade from global to local
- Are model-agnostic

### Modes (Capability Guardrails)

Modes define **what an agent is allowed to do right now**:
- **Explore** — Read only, no opinions
- **Propose** — Ideas only, no execution
- **Execute** — Act within approved scope
- **Critique** — Judge risk, not solutions
- **Reevaluate** — Stop and reflect

Modes are instructions, not documents. They change frequently.
Direction never changes inside a mode.

### Control Loops (Reevaluation)

Reevaluation is:
- **Mandatory** (not optional)
- **Triggered** (not discretionary)
- **Structured** (not freeform)
- **Confidence-driven** (depth scales with risk)

---

## Cascading Inheritance

### Discovery Rule

For any task, the effective direction is built from **all `INTENT.md` files** found by searching:

1. From the current working directory
2. Upward through each parent directory
3. **Stopping at the repository root**

This mirrors Git config, ESLint, Nginx, and other mature systems.

### Inheritance Semantics

**Hard inheritance** applies:
- All parent intents **always apply**
- Constraints **accumulate** (union)
- Scope can **only narrow** (never expand)
- Invariants **never disappear** (only explicit overrides)

### Override Rules

Overrides must be:
- **Explicit** — Stated in an `# Overrides` section
- **Justified** — Include a reason
- **Localized** — Apply only within the current subtree
- **Reviewable** — Subject to the same scrutiny as code

Example:
```markdown
# Overrides

This feature temporarily relaxes invariant:
- "No API changes"

Reason:
- Required to expose existing internal behavior for testing.
- Scope is limited to `tests/fixtures/`.
```

### Conflict Resolution

If two intent files conflict and no explicit override exists:
> **Execution halts and escalates to human.**

Agents may **detect** conflicts. Agents may **never** resolve them.

---

## Intent File Schema

All `INTENT.md` files share the same structure:

```markdown
# INTENT.md — [Scope Description]

## Goal
(Required at the most local level; optional at higher levels)

## Non-Goals
(What success explicitly does NOT include)

## Scope
(Repos, layers, files, or contracts allowed/forbidden)

## Invariants
(Things that must not change without explicit override)

## Overrides
(Explicit exceptions to parent invariants, with justification)

## Authority & Stops
(Conditions that require halting and asking)

## Reevaluation Triggers
(Conditions that mandate reevaluation)
```

### Schema Notes

- **Goal**: Only required at the feature/task level. Higher levels define philosophy, not tasks.
- **Non-Goals**: Critical for preventing scope creep. Be explicit.
- **Invariants**: Accumulated from all parent files. Cannot be silently removed.
- **Overrides**: Must reference the specific invariant being overridden.
- **Authority & Stops**: Hard stops, not suggestions.
- **Reevaluation Triggers**: Automatic checkpoints based on observable conditions.

---

## Three-Level Hierarchy (Recommended)

### Level 1 — Repository Root

**Scope**: Entire repository
**Purpose**: Philosophy, global invariants, ecosystem rules
**Changes**: Rarely

Example location: `/INTENT.md`

Contents typically include:
- Backward compatibility requirements
- Code quality standards
- Process requirements (PRs, tests, coordination)
- Security and privacy invariants

### Level 2 — Subsystem / Layer

**Scope**: A major module, service, or layer
**Purpose**: Local architectural norms, domain rules
**Changes**: Occasionally

Example locations:
- `/logos_config/INTENT.md`
- `/contracts/INTENT.md`
- `/ontology/INTENT.md`

Contents typically include:
- Subsystem-specific invariants
- Performance or design constraints
- Domain-specific non-goals

### Level 3 — Feature / Task

**Scope**: One feature, PR, or focused change
**Purpose**: Concrete goal, temporary constraints
**Changes**: Frequently (created and deleted per task)

Example locations:
- `/logos_config/health/INTENT.md`
- `/contracts/sophia/INTENT.md`
- `.work/feature-x.intent.md` (alternative pattern)

Contents typically include:
- Specific goal for this work
- Tight scope boundaries
- Explicit overrides (if any)
- Task-specific stop conditions

---

## Agent Modes (Detailed)

### Explore Mode

**Purpose**: Build shared reality from the codebase.

**Allowed**:
- File reading
- Cross-repo search
- Documentation lookup
- Contract inspection

**Forbidden**:
- Suggestions ("we should...")
- Opinions
- Conclusions
- Any file modifications

**Output format**:
- Facts only
- File paths with line numbers
- Direct quotes
- Existing behavior descriptions

### Propose Mode

**Purpose**: Generate options without committing.

**Allowed**:
- Suggesting approaches
- Identifying tradeoffs
- Estimating scope
- Listing assumptions

**Forbidden**:
- File modifications
- Execution of any kind
- Deciding without approval

**Output format**:
- 1-2 candidate approaches
- Explicit assumptions
- Known risks
- "This could be wrong if..."

### Execute Mode

**Purpose**: Implement approved changes.

**Allowed**:
- File modifications within approved scope
- Running tests
- Creating commits (on branches only)

**Forbidden**:
- Scope expansion without re-approval
- Reinterpreting the approved plan
- Pushing to protected branches
- Silent assumption changes

**Required behavior**:
- Announce each step before taking it
- Stop on assumption changes
- Respect reevaluation checkpoints

### Critique Mode

**Purpose**: Assess risk without solving.

**Allowed**:
- Identifying risks
- Flagging scope creep
- Detecting contract violations
- Grading confidence

**Forbidden**:
- Generating alternatives
- Solving problems
- Writing code

**Output format**:
- Confidence rating (High / Medium / Low)
- Reasons for rating
- Risk flags with severity
- Required action (none / reevaluate / escalate)

### Reevaluate Mode

**Purpose**: Stop and reflect on trajectory.

**Allowed**:
- Summarizing current state
- Comparing against intent
- Identifying drift
- Recommending continue / pivot / abort

**Forbidden**:
- Any execution
- Continuing without completing reevaluation

**Output format** (varies by depth — see below)

---

## Reevaluation System

### Confidence-Driven Depth

Reevaluation depth scales **inversely** with critic confidence:

| Confidence | Depth | Scope | Human Required |
|------------|-------|-------|----------------|
| **High** | Minimal | Local intent only | No |
| **Medium** | Targeted | Local + parent intents | Optional |
| **Low** | Full reset | Entire cascade | Yes |

### Reevaluation Triggers

Reevaluation is **mandatory** when:

1. **Step budget exceeded** — More than N meaningful steps without checkpoint
2. **Assumption drift** — A new assumption introduced or existing one invalidated
3. **Evidence conflict** — Observed facts contradict documentation or expectations
4. **Scope expansion** — Work expands beyond originally stated boundaries
5. **Critic confidence** — Confidence rating is Medium or Low

### Reevaluation Output (By Depth)

#### High Confidence (Minimal)

Required outputs:
- One-paragraph summary of current trajectory
- Confirmation that goal still matches direction contract
- Statement: "No contract violations detected"

#### Medium Confidence (Targeted)

Required outputs:
- Restated goal (in agent's own words)
- List of active assumptions with confidence
- What would falsify the current approach
- Summary of progress so far
- Explicit check against non-goals

#### Low Confidence (Full Reset)

Required outputs:
- Full restatement of direction contract
- Explicit mapping: contract → current approach
- Known unknowns
- Alternative approaches (high-level, not detailed)
- Recommendation: continue / pivot / abort

### Confidence Stickiness

Confidence is **sticky downward**:
- High → Medium → Low

Confidence does **not** auto-recover upward without explicit reevaluation.
This prevents "confidence laundering."

---

## Critic Output Schema

Critics output a structured assessment, never solutions:

```markdown
## Confidence Rating
[High | Medium | Low]

## Reasons for Confidence Level
- Reason 1 (tied to specific contract section)
- Reason 2
- ...

## Risk Flags
- [Severity: Low | Medium | High] Description of risk
- ...

## Required Action
[No action needed | Reevaluate assumptions | Pause and escalate to human]
```

### Critic Input

Critics receive:
- Direction contract (the relevant `INTENT.md` files)
- Current plan or execution summary
- Declared assumptions

Critics do **not** receive:
- Full chat history
- Explorer output
- Prior justifications

This partial blindness is intentional — it prevents sunk-cost bias.

---

## Practical Workflow

### Phase 0 — Create Direction Artifact

Before any work begins:
1. Create or identify the relevant `INTENT.md` file
2. Define goal, non-goals, scope, invariants
3. This file is immutable for the duration of the task

### Phase 1 — Exploration (Optional)

- Mode: Explore
- Input: Direction artifact
- Output: Facts, file paths, quotes

### Phase 2 — Proposal

- Mode: Propose
- Input: Direction artifact + explorer output
- Output: Approaches, assumptions, risks

### Phase 3 — Critique

- Mode: Critique
- Input: Direction artifact + proposal
- Output: Confidence rating, risks, required action

### Phase 4 — Reevaluation (Automatic)

Based on critic confidence:
- High → Minimal check, continue
- Medium → Targeted reevaluation
- Low → Full reset, human gate

### Phase 5 — Execution

- Mode: Execute
- Input: Direction artifact + approved plan
- Constraints: Branch only, step announcements, checkpoints

### Phase 6 — Reevaluation Loop

Repeat Phase 3-5 as needed, triggered by:
- Step budget
- Assumption changes
- Evidence conflicts
- Critic flags

### Phase 7 — Final Critique

Before merge:
- One last critic pass
- Risk assessment only
- Human decides merge

---

## Anti-Patterns

### Silent Override

**Wrong**:
```markdown
# Goal
Refactor the API (ignoring the backward compatibility requirement)
```

**Right**:
```markdown
# Overrides
This task overrides invariant:
- "Public APIs are backward compatible"

Reason:
- The existing API has a fundamental design flaw that cannot be fixed incrementally.
- Migration plan documented in MIGRATION.md.
```

### Implicit Scope Expansion

**Wrong**: Agent modifies files outside stated scope without asking.

**Right**: Agent stops when scope would expand and requests approval.

### Confidence Laundering

**Wrong**: After a Low confidence rating, agent claims High confidence in next message.

**Right**: Confidence can only improve through explicit reevaluation that addresses the underlying concerns.

### Philosophy in Mode Guards

**Wrong**: Mode instructions include "be careful" or "think before acting."

**Right**: Mode instructions specify allowed/forbidden actions. Philosophy lives in direction artifacts.

---

## Integration with AGENTS.md

The Intent Framework complements, not replaces, `AGENTS.md`:

| Artifact | Purpose | Scope | Changes |
|----------|---------|-------|---------|
| `AGENTS.md` | How agents work in this repo | Repository | Rarely |
| `INTENT.md` (root) | Global invariants and philosophy | Repository | Rarely |
| `INTENT.md` (subsystem) | Layer-specific constraints | Directory subtree | Occasionally |
| `INTENT.md` (feature) | Task-specific direction | Single task | Frequently |

`AGENTS.md` defines **process**.
`INTENT.md` defines **purpose**.

---

## Quick Reference

### Intent File Discovery
```
Search: current directory → parent directories → stop at repo root
Apply: all found files, in order
Override: only with explicit justification
Conflict: halt and escalate (never resolve)
```

### Reevaluation Depth
```
High confidence   → Minimal (local intent only)
Medium confidence → Targeted (local + parents)
Low confidence    → Full reset (entire cascade + human)
```

### The Three Questions

Before any agent action, three questions must be answerable:

1. **What is the direction?** (INTENT.md files)
2. **What mode is active?** (Explore / Propose / Execute / Critique / Reevaluate)
3. **When is the next reevaluation?** (Triggers defined in intent)

If any question cannot be answered, stop and clarify.

---

## Changelog

- **v1.0** — Initial framework specification
