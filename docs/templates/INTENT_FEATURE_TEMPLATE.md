# INTENT.md — [Feature/Task Name]

<!-- 
This is a TEMPLATE for feature-level intent files.
Copy this file to the feature directory and customize.
Delete this comment block when using.
-->

This intent applies to [describe scope] and inherits from all parent intents.

---

## Goal

[What must be true when this work is done. Be specific and testable.]

---

## Non-Goals

- [What this work explicitly does NOT include]
- [Be specific about scope boundaries]
- [List things someone might assume are in scope but aren't]

---

## Scope

- Files: [specific files or directories]
- Layers: [which parts of the system]
- Inherits: all parent intents

---

## Invariants

In addition to inherited invariants:

- [Task-specific things that must not change]
- [Behaviors to preserve]
- [Interfaces to maintain]

---

## Overrides

<!-- 
Only include this section if you need to override a parent invariant.
If no overrides, state "None." and delete the example.
-->

This task overrides inherited invariant:
- "[Exact text of invariant being overridden]"

Reason:
- [Why this override is necessary]
- [What safeguards are in place]
- [When this override expires]

---

## Authority & Stops

The agent **MUST stop and ask** if:

- [Specific conditions for this task]
- Scope would expand beyond stated boundaries
- An assumption changes from the original understanding
- [Add task-specific stop conditions]

---

## Reevaluation Triggers

- More than [N] files touched
- [Task-specific trigger]
- Any ambiguity about [specific concern]
- Critic confidence drops below High

---

## Acceptance Criteria

<!-- Optional but recommended for task-level intents -->

- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] Tests pass
- [ ] No regressions

---

## Notes

<!-- Optional: context, decisions made, open questions -->
