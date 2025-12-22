# INTENT.md — Logos Repository (Root)

This is the **root direction artifact** for the Logos repository.
All agents, tasks, and changes within this repository inherit this intent.
See `docs/standards/INTENT_FRAMEWORK.md` for the full framework specification.

---

## Goal

Provide a stable, evolvable foundation for the LOGOS cognitive architecture,
including canonical contracts, shared ontology, reusable SDKs, and ecosystem-wide standards.

---

## Non-Goals

- Rapid prototyping at the expense of clarity or stability
- Hidden coupling between subsystems or repositories
- Silent breaking changes to contracts or APIs
- Repository-specific logic that belongs in downstream repos (sophia, hermes, talos, apollo)
- Over-engineering shared utilities beyond demonstrated need

---

## Scope

- **Contracts** — OpenAPI specifications defining service interfaces
- **Ontology** — Core ontology, Cypher schemas, and SHACL shapes
- **SDKs** — Python packages (`logos_config`, `logos_hcg`, `logos_test_utils`, etc.)
- **Standards** — Testing, Git, and project conventions for the ecosystem
- **Infrastructure** — Docker compose files, CI workflows, and shared tooling

Changes outside these domains should be questioned.

---

## Invariants

These must not change without explicit override and justification:

### Contracts
- Public contracts in `contracts/` are **backward compatible** unless explicitly overridden
- Contract changes require coordination with all consuming repositories
- Breaking changes require a tracking issue and migration plan

### Code Quality
- All public functions have type hints
- All public functions have docstrings
- Small, composable functions over monolithic blocks
- No secrets, tokens, or PII in logs or code

### Architecture
- Prefer explicit data flow over implicit side effects
- Changes should be understandable by reading code, not requiring chat history
- `logos_config` is the single source of truth for shared configuration

### Process
- All changes go through pull requests (never push directly to `main`)
- Tests must pass before merge
- Cross-repo changes require tracking issues in logos

---

## Overrides

None at the root level.
(Subsystem and feature-level intents may override specific invariants with justification.)

---

## Authority & Stops

The agent **MUST stop and ask** if:

- A public API or contract is being changed
- Cross-repo dependencies are introduced or modified
- Architectural layering is violated
- A new abstraction or pattern is introduced
- Scope expands beyond the current directory or task
- An assumption changes from what was originally stated

---

## Reevaluation Triggers

Reevaluation is **mandatory** when:

- **Step budget exceeded** — More than 10 meaningful steps taken without checkpoint
- **Evidence conflict** — Observed behavior contradicts documented expectations
- **Assumption drift** — A new assumption is introduced or an existing one invalidated
- **Critic confidence drops** — Confidence is Medium or Low (see framework docs)
- **Scope expansion** — Work expands beyond originally stated boundaries

---

## How This File Is Used

1. **Discovery**: Agents search for `INTENT.md` files from working directory up to repo root
2. **Inheritance**: All parent intents apply; constraints accumulate; scope narrows
3. **Overrides**: Local intents may override parent invariants with explicit justification
4. **Evaluation**: Reevaluation checkpoints compare current trajectory against this artifact
5. **Conflict**: If intent files conflict without explicit override, execution halts

This file is the **single source of truth** for direction in this repository.
Models change; this document does not (unless you change it).
