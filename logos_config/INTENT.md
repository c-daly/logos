# INTENT.md — logos_config Subsystem

This intent applies to the `logos_config` package and inherits from the repository root.

---

## Goal

Provide a single, reliable source of configuration utilities for the entire LOGOS ecosystem,
including environment resolution, port allocation, and service settings.

---

## Non-Goals

- Complex configuration hierarchies or overrides
- Runtime configuration reloading
- Configuration validation beyond type safety
- Repository-specific business logic
- Production deployment tooling (this is for code, not ops)

---

## Scope

- `logos_config/` directory only
- Applies to all files within this subtree
- Inherits all invariants from repository root

---

## Invariants

In addition to repository-level invariants:

### API Stability
- Public API changes require deprecation warnings first
- Function signatures are backward compatible
- New parameters must have defaults

### Simplicity
- No external dependencies beyond Pydantic
- No I/O in module-level code
- No implicit environment modification
- Functions are pure where possible

### Cross-Repo Consistency
- Port allocation scheme is immutable without ecosystem-wide coordination
- All repos use identical port offset logic
- Configuration models are shared, not duplicated

---

## Overrides

None.

---

## Authority & Stops

The agent **MUST stop and ask** if:

- Changing the port allocation scheme
- Adding new external dependencies
- Modifying public function signatures
- Changing configuration model fields
- Any change that would require downstream repos to update

---

## Reevaluation Triggers

- Changes affect more than 3 files
- Tests in downstream repos might be affected
- New assumptions about environment or deployment
